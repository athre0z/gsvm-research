"""
    Disassembler for GalaxyScript bytecode.

    The MIT License (MIT)

    Copyright (c) 2015 Joel Hoener <athre0z@zyantific.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from __future__ import print_function, division
from operands import Register, Immediate, AddExpression, Reference

# Instruction decoders
decode_unk = lambda i: ()
decode_noops = lambda i: ()
decode_reg = lambda i: (Register(i[21:26]), )
decode_reg_reg = lambda i: (Register(i[21:26]), Register(i[16:21]))
decode_reg_reg_reg = lambda i: (Register(i[21:26]), Register(i[16:21]), Register(i[11:16]))
decode_reg_const21 = lambda i: (Register(i[21:26]), Immediate(i[0:21], 21))
decode_reg_gref21 = lambda i: (Register(i[21:26]), Reference(Immediate(i[0:21], 21), Reference.GLOBAL))
decode_reg_const8 = lambda i: (Register(i[21:26]), Immediate(i[0:8], 8))
decode_cond_branch = lambda i: (Register(i[21:26]), Reference(Immediate(i[0:21] << 2, 23), Reference.CODE, True))
decode_insn_jmp = lambda i: (Reference(Immediate(i[0:21] << 2, 21), Reference.CODE, True), )
decode_add_lsh11 = lambda i: (Register(i[21:26]), Immediate(i[0:21] << 11, 32))
decode_reg_glob = lambda i: (Register(i[21:26]), Reference(Immediate(i[0:21], 21), Reference.GLOBAL))
decode_insn_add_i8 = lambda i: (Register(i[21:26]), Register(i[16:21]), Immediate(i[0:8], 8))
decode_insn_pop = lambda i: (Immediate(i[4:26], 22), Immediate(i[0:4], 4))
decode_insn_retn = lambda i: (Immediate(i[0:16], 16), )  # TODO: immediate consists of multiple components. parse.

decode_insn_ld_local32b = lambda i: (
    Register(i[21:26]),
    Reference(AddExpression(Register(Register.BP), Immediate(i[0:16], 16)), Reference.STACK),
)
decode_insn_push_local32 = lambda i: (
    Immediate(i[21:26], 5, Immediate.CONST_BOOL),
    Reference(AddExpression(Register(Register.BP), Immediate(i[0:16], 16)), Reference.STACK),
)

def make_decode_reg_reg_const16(type_):
    return lambda i: (
        Register(i[21:26]),
        Reference(AddExpression(Register(i[16:21]), Immediate(i[0:16], 16)), type_),
    )

decode_reg_reg_const16_s = make_decode_reg_reg_const16(Reference.STACK)
decode_reg_reg_const16_g = make_decode_reg_reg_const16(Reference.GLOBAL)
decode_reg_reg_const16_c = make_decode_reg_reg_const16(Reference.CODE)
decode_reg_reg_const16_u = make_decode_reg_reg_const16(Reference.UNIFIED)

def decode_insn_call(insn):
    reg = insn[21:26]
    func_idx = insn[1:21]
    r = Immediate(insn[0:1], 1, Immediate.CONST_BOOL)
    return (Immediate(func_idx, 20), r) if reg == 0 else (Register(reg), r)

def decode_insn_push(insn):
    reg = insn[21:26]
    return (Immediate(insn[0:21], 21) if reg == Register.BP else Register(reg)),

def decode_store(insn):
    val_reg = insn[16:21]
    base_reg = insn[21:26]
    imm = insn[0:16]
    if base_reg == Register.BP:
        dst = Reference(AddExpression(Register(Register.BP), Immediate(imm, 16)), Reference.STACK)
    else:
        if imm == 0:
            ref_type = Reference.GLOBAL
        elif imm == 1:
            ref_type = Reference.STACK
        else:
            ref_type = Reference.UNIFIED
        dst = Reference(Register(base_reg), ref_type)
    return dst, Register(val_reg) if val_reg != Register.SP else Immediate(0, 32)

def decode_decref(insn):
    reg = insn[21:26]
    imm = Immediate(insn[0:21], 21)
    rhs = AddExpression(Register(reg), imm) if reg != 30 else imm
    return Reference(AddExpression(Register(Register.BP), rhs), Reference.STACK),

def decode_mov(insn):
    dst_reg = Register(insn[21:26])
    src_reg = Register(insn[16:21])
    imm = Immediate(insn[0:16], 16)
    return dst_reg, AddExpression(src_reg, imm) if imm.val else src_reg

# Operand usage information
OP_USE1 = 1 << 1
OP_USE2 = 1 << 2
OP_USE3 = 1 << 3
OP_CHG1 = 1 << 4
OP_CHG2 = 1 << 5
OP_CHG3 = 1 << 6
OP_JUMP = 1 << 7
OP_CALL = 1 << 8
OP_NFLW = 1 << 9  # does not pass flow to next insn
OP_UCG1 = OP_USE1 | OP_CHG1
OP_UCG2 = OP_USE2 | OP_CHG2
OP_UCG3 = OP_USE3 | OP_CHG3

# Opcode specific information
opcodes = [
    ('add',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x00
    ('add_gc',       decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x01
    ('add_i21',      decode_reg_const21,       OP_CHG1 | OP_USE2          ),  # 0x02
    ('add_lsh11',    decode_add_lsh11,         OP_UCG1 | OP_USE2          ),  # 0x03
    ('and',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x04
    ('ckarbnds',     decode_reg_const21,       OP_USE1 | OP_USE2          ),  # 0x05
    ('jz',           decode_cond_branch,       OP_USE1 | OP_USE2 | OP_JUMP),  # 0x06
    ('jmp',          decode_insn_jmp,          OP_USE1 | OP_JUMP | OP_NFLW),  # 0x07
    ('jnz',          decode_cond_branch,       OP_USE1 | OP_USE2 | OP_JUMP),  # 0x08
    ('not',          decode_reg_reg,           OP_CHG1 | OP_USE2          ),  # 0x09
    ('div',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x0A
    ('fdiv',         decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x0B
    ('decref',       decode_decref,            OP_USE1                    ),  # 0x0C
    ('seteq',        decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x0D
    ('seteq_gc',     decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x0E
    ('call',         decode_insn_call,         OP_USE1 | OP_USE2 | OP_CALL),  # 0x0F
    ('setge',        decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x10
    ('enter',        decode_reg_const21,       OP_USE1 | OP_USE2          ),  # 0x11
    ('bp',           decode_noops,             0                          ),  # 0x12
    ('ld_const_i21', decode_reg_const21,       OP_CHG1 | OP_USE2          ),  # 0x13
    ('ld_global32i', decode_reg_glob,          OP_CHG1 | OP_USE2          ),  # 0x14
    ('ld_global8i',  decode_reg_glob,          OP_CHG1 | OP_USE2          ),  # 0x15
    ('mov',          decode_mov,               OP_CHG1 | OP_USE2          ),  # 0x16
    ('add_i8',       decode_insn_add_i8,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x17
    ('ld_local32b',  decode_insn_ld_local32b,  OP_CHG1 | OP_USE2          ),  # 0x18
    ('ld_local32',   decode_reg_reg_const16_s, OP_CHG1 | OP_USE2          ),  # 0x19
    ('ld_local8',    decode_reg_reg_const16_s, OP_CHG1 | OP_USE2          ),  # 0x1A
    ('ld_global32',  decode_reg_reg_const16_g, OP_CHG1 | OP_USE2          ),  # 0x1B
    ('ld_global8',   decode_reg_reg_const16_g, OP_CHG1 | OP_USE2          ),  # 0x1C
    ('ld_mem32',     decode_reg_reg_const16_u, OP_CHG1 | OP_USE2          ),  # 0x1D
    ('ld_mem8',      decode_reg_reg_const16_u, OP_CHG1 | OP_USE2          ),  # 0x1E
    ('mod',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x1F
    ('mul',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x20
    ('mul_i21',      decode_reg_const21,       OP_UCG1 | OP_USE2          ),  # 0x21
    ('fmul',         decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x22
    ('setneq',       decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x23
    ('neg',          decode_reg_reg,           OP_CHG1 | OP_USE2          ),  # 0x24
    ('setneq_gc',    decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x25
    ('seteq0',       decode_reg_reg,           OP_CHG1 | OP_USE2          ),  # 0x26
    ('or',           decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x27
    ('pop',          decode_insn_pop,          OP_USE1 | OP_USE2          ),  # 0x28
    ('push',         decode_insn_push,         OP_USE1                    ),  # 0x29
    ('push_local32', decode_insn_push_local32, OP_USE1 | OP_USE2          ),  # 0x2A
    ('retn',         decode_insn_retn,         OP_USE1 | OP_NFLW          ),  # 0x2B
    ('shl_r',        decode_reg_reg,           OP_UCG1 | OP_USE2          ),  # 0x2C
    ('shl_i8',       decode_reg_const8,        OP_UCG1 | OP_USE2          ),  # 0x2D
    ('shr_r',        decode_reg_reg,           OP_UCG1 | OP_USE2          ),  # 0x2E
    ('shr_i8',       decode_reg_const8,        OP_UCG1 | OP_USE2          ),  # 0x2F
    ('st_mem32',     decode_store,             OP_CHG1 | OP_USE2          ),  # 0x30
    ('st_mem8',      decode_store,             OP_CHG1 | OP_USE2          ),  # 0x31
    ('st_gc',        decode_store,             OP_CHG1 | OP_USE2          ),  # 0x32
    ('mkgc',         decode_reg,               OP_USE1                    ),  # 0x33
    ('mkstr',        decode_reg_gref21,        OP_CHG1 | OP_USE2          ),  # 0x34
    ('strcat',       decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x35
    ('unk_36',       decode_reg_reg_const16_g, 0                          ),  # 0x36
    ('sub',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x37
    ('sub_gc',       decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x38
    ('xor',          decode_reg_reg_reg,       OP_CHG1 | OP_USE2 | OP_USE3),  # 0x39
]