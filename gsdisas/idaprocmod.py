"""
    IDA processor module for GalaxyScript bytecode.

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

# This script is based on Hex-Rays processor module template (c) Hex-Rays

import sys
import idaapi
from idaapi import *
from gsdisas import *
from gsdisas.tables import *
from gsdisas.operands import *

# ----------------------------------------------------------------------

class GsVmProcessor(idaapi.processor_t):
    """
    Processor module for the GalaxyScript virtual machine.
    """

    # IDP id ( Numbers above 0x8000 are reserved for the third-party modules)
    id = 0x8000 + 0x4786

    # Processor features
    flag = PR_SEGS | PR_USE32 | PR_DEFSEG32 | PR_RNAMESOK | PRN_HEX | PR_NO_SEGMOVE

    # Number of bits in a byte for code segments (usually 8)
    # IDA supports values up to 32 bits
    cnbits = 8

    # Number of bits in a byte for non-code segments (usually 8)
    # IDA supports values up to 32 bits
    dnbits = 8

    # short processor names
    # Each name should be shorter than 9 characters
    psnames = ['gsvm']

    # long processor names
    # No restriction on name lengthes.
    plnames = ['GalaxyScript VM']

    def __init__(self):
        super(GsVmProcessor, self).__init__()
        self._init_instructions()
        self._init_regs()

    def _init_instructions(self):
        self.instruc = []
        for i, cur_opcode in enumerate(opcodes):
            feature = 0
            feature_mapping = [
                (OP_USE1, CF_USE1),
                (OP_USE2, CF_USE2),
                (OP_USE3, CF_USE3),
                (OP_CHG1, CF_CHG1),
                (OP_CHG2, CF_CHG2),
                (OP_CHG3, CF_CHG3),
                (OP_JUMP, CF_JUMP),
                (OP_CALL, CF_CALL),
                (OP_NFLW, CF_STOP),
            ]
            for cur_feature in feature_mapping:
                if cur_opcode[2] & cur_feature[0]:
                    feature |= cur_feature[1]
            self.instruc.append({
                'name': cur_opcode[0],
                'feature': feature,
                'cmt': '',
            })
            setattr(self, 'itype_' + str(cur_opcode[0]), i)
        self.instruc_end = len(self.instruc) # + 1
        self.icode_return = self.itype_retn

    def _init_regs(self):
        self.regNames = []
        for i in xrange(30):
            self.regNames.append('r' + str(i))
        self.regNames += [
            'bp', 'sp',
            'cs', 'gs', 'ss', # fake segment registers
        ]
        for i, cur_reg in enumerate(self.regNames):
            setattr(self, 'ireg_' + cur_reg, i)
        self.regFirstSreg = self.ireg_cs
        self.regLastSreg = self.ireg_ss
        self.regCodeSreg = self.ireg_cs
        self.regDataSreg = self.ireg_gs

    # size of a segment register in bytes
    segreg_size = 0

    # Array of typical code start sequences (optional)
    codestart = ['\x44']

    # Array of 'return' instruction opcodes (optional)
    retcodes = ['\xAC']

    # icode of the first instruction
    instruc_start = 0

    # Size of long double (tbyte) for this processor (meaningful only if ash.a_tbyte != NULL) (optional)
    tbyte_size = 0

    #
    # Number of digits in floating numbers after the decimal point.
    # If an element of this array equals 0, then the corresponding
    # floating point data is not used for the processor.
    # This array is used to align numbers in the output.
    #      real_width[0] - number of digits for short floats (only PDP-11 has them)
    #      real_width[1] - number of digits for "float"
    #      real_width[2] - number of digits for "double"
    #      real_width[3] - number of digits for "long double"
    # Example: IBM PC module has { 0,7,15,19 }
    #
    # (optional)
    #real_width = (0, 7, 15, 0)

    # If the FIXUP_VHIGH and FIXUP_VLOW fixup types are supported
    # then the number of bits in the HIGH part. For example,
    # SPARC will have here 22 because it has HIGH22 and LOW10 relocations.
    # See also: the description of PR_FULL_HIFXP bit
    # (optional)
    #high_fixup_bits = 0

    # only one assembler is supported
    assembler = {
        # flag
        'flag' : ASH_HEXF3 | AS_UNEQU | AS_COLON | ASB_BINF4 | AS_N2CHR,

        # user defined flags (local only for IDP) (optional)
        'uflag' : 0,

        # Assembler name (displayed in menus)
        'name': "GSVM bytecode assembler",

        # array of automatically generated header lines they appear at the start of disassembled text (optional)
        'header': ["Line1", "Line2"],

        # array of unsupported instructions (array of cmd.itype) (optional)
        'badworks': [6, 11],

        # org directive
        'origin': "org",

        # end directive
        'end': "end",

        # comment string (see also cmnt2)
        'cmnt': ";",

        # ASCII string delimiter
        'ascsep': "\"",

        # ASCII char constant delimiter
        'accsep': "'",

        # ASCII special chars (they can't appear in character and ascii constants)
        'esccodes': "\"'",

        #
        #      Data representation (db,dw,...):
        #
        # ASCII string directive
        'a_ascii': "db",

        # byte directive
        'a_byte': "db",

        # word directive
        'a_word': "dw",

        # remove if not allowed
        'a_dword': "dd",

        # remove if not allowed
        #'a_qword': "dq",

        # remove if not allowed
        #'a_oword': "xmmword",

        # remove if not allowed
        #'a_yword': "ymmword",

        # float;  4bytes; remove if not allowed
        'a_float': "dd",

        # double; 8bytes; NULL if not allowed
        #'a_double': "dq",

        # long double;    NULL if not allowed
        #'a_tbyte': "dt",

        # packed decimal real; remove if not allowed (optional)
        #'a_packreal': "",

        # array keyword. the following
        # sequences may appear:
        #      #h - header
        #      #d - size
        #      #v - value
        #      #s(b,w,l,q,f,d,o) - size specifiers
        #                        for byte,word,
        #                            dword,qword,
        #                            float,double,oword
        'a_dups': "#d dup(#v)",

        # uninitialized data directive (should include '%s' for the size of data)
        'a_bss': "%s dup ?",

        # 'equ' Used if AS_UNEQU is set (optional)
        'a_equ': ".equ",

        # 'seg ' prefix (example: push seg seg001)
        'a_seg': "seg",

        #
        # translation to use in character and string constants.
        # usually 1:1, i.e. trivial translation
        # If specified, must be 256 chars long
        # (optional)
        'XlatAsciiOutput': "".join([chr(x) for x in xrange(256)]),

        # current IP (instruction pointer) symbol in assembler
        'a_curip': "$",

        # "public" name keyword. NULL-gen default, ""-do not generate
        'a_public': "public",

        # "weak"   name keyword. NULL-gen default, ""-do not generate
        'a_weak': "weak",

        # "extrn"  name keyword
        'a_extrn': "extrn",

        # "comm" (communal variable)
        'a_comdef': "",

        # "align" keyword
        'a_align': "align",

        # Left and right braces used in complex expressions
        'lbrace': "(",
        'rbrace': ")",

        # %  mod     assembler time operation
        'a_mod': "%",

        # &  bit and assembler time operation
        'a_band': "&",

        # |  bit or  assembler time operation
        'a_bor': "|",

        # ^  bit xor assembler time operation
        'a_xor': "^",

        # ~  bit not assembler time operation
        'a_bnot': "~",

        # << shift left assembler time operation
        'a_shl': "<<",

        # >> shift right assembler time operation
        'a_shr': ">>",

        # size of type (format string) (optional)
        'a_sizeof_fmt': "size %s",

        'flag2': 0,

        # comment close string (optional)
        # this is used to denote a string which closes comments, for example, if the comments are represented with (* ... *)
        # then cmnt = "(*" and cmnt2 = "*)"
        'cmnt2': "",

        # low8 operation, should contain %s for the operand (optional fields)
        'low8': "",
        'high8': "",
        'low16': "",
        'high16': "",

        # the include directive (format string) (optional)
        'a_include_fmt': "include %s",

        # if a named item is a structure and displayed  in the verbose (multiline) form then display the name
        # as printf(a_strucname_fmt, typename)
        # (for asms with type checking, e.g. tasm ideal)
        # (optional)
        'a_vstruc_fmt': "",

        # 3-byte data (optional)
        'a_3byte': "",

        # 'rva' keyword for image based offsets (optional)
        # (see nalt.hpp, REFINFO_RVA)
        'a_rva': "rva"
    } # Assembler

    # ----------------------------------------------------------------------
    # The following callbacks are mandatory
    #

    def emu(self):
        """
        Emulate instruction, create cross-references, plan to analyze
        subsequent instructions, modify flags etc. Upon entrance to this function
        all information about the instruction is in 'cmd' structure.
        If zero is returned, the kernel will delete the instruction.
        """
        feature = self.cmd.get_canon_feature()
        if feature & CF_JUMP:
            QueueSet(Q_jumps, self.cmd.ea)
            target_op = self.cmd.Operands[0 if self.cmd.itype == self.itype_jmp else 1]
            if target_op.type == o_mem:
                ua_add_cref(0, self.cmd.ea + self.cmd.size + target_op.addr, fl_JN)
        if not (feature & CF_STOP):
            ua_add_cref(0, self.cmd.ea + self.cmd.size, fl_F)
        return 1

    def outop(self, op):
        """
        Generate text representation of an instructon operand.
        This function shouldn't change the database, flags or anything else.
        All these actions should be performed only by u_emu() function.
        The output text is placed in the output buffer initialized with init_output_buffer()
        This function uses out_...() functions from ua.hpp to generate the operand text
        Returns: 1-ok, 0-operand is hidden.
        """
        def out_opnd(opnd, imm_src):
            if isinstance(opnd, Expression):
                #out_opnd(opnd.lhs, OOF_ADDR)
                #out_symbol(opnd.operator)
                #out_opnd(opnd.rhs, OOF_ADDR)
                OutLine(opnd.textual())
            elif type(opnd) == Register:
                out_register(self.regNames[opnd.idx])
            elif type(opnd) == Immediate:
                OutValue(op, OOFW_32 | imm_src)
            elif type(opnd) == Reference:
                out_keyword(opnd.prefix())
                for c in '::[':
                    out_symbol(c)
                out_opnd(opnd.expr, OOF_ADDR)
                out_symbol(']')
            else:
                return False
            return True

        try:
           return out_opnd(self.cmd.dec.ops[op.n], OOFW_IMM)
        except IndexError:
            return False

    def out(self):
        """
        Generate text representation of an instruction in 'cmd' structure.
        This function shouldn't change the database, flags or anything else.
        All these actions should be performed only by u_emu() function.
        Returns: nothing
        """
        buf = init_output_buffer(0x400)  # should be more than enough
        OutMnem(13, None)

        for i, cur_op in enumerate(self.cmd.dec.ops):
            out_one_operand(i)
            if i != len(self.cmd.dec.ops) - 1:
                out_symbol(',')
                OutChar(' ')

        term_output_buffer()
        MakeLine(buf)

    def ana(self):
        """
        Decodes an instruction into self.cmd.
        Returns: self.cmd.size (=the size of the decoded instruction) or zero
        """
        insn = ua_next_long()
        dec = InsnDecoder(EncodedInsn(insn)).decode()
        self.cmd.itype = dec.opcode
        self.cmd.size = 4

        op_map = (self.cmd.Op1, self.cmd.Op2, self.cmd.Op3)
        for my_op, ida_op in zip(dec.ops, op_map):
            if type(my_op) == Immediate:
                ida_op.type = o_imm
                ida_op.value = my_op.val
            elif type(my_op) == Register:
                ida_op.type = o_reg
                ida_op.reg = my_op.idx
                ida_op.dtype = dt_dword  # TODO
            elif isinstance(my_op, Expression):
                ida_op.type = o_phrase
                # TODO
            elif type(my_op) == Reference:
                expr = my_op.expr
                if type(expr) == Immediate:
                    ida_op.type = o_mem
                    ida_op.addr = my_op.expr.val
                elif type(expr) == Register:
                    ida_op.type = o_reg
                    ida_op.reg = expr.idx
                elif isinstance(expr, Expression):
                    if Immediate in (type(expr.lhs), type(expr.rhs)):
                        ida_op.type = o_phrase
                    else:
                        ida_op.type = o_displ
                else:
                    raise RuntimeError("unreachable code (2)")
            else:
                raise RuntimeError("unreachable code (1)")

        # We store (hack?) the decoded instruction info into the cmd struct.
        self.cmd.dec = dec

        # Return decoded instruction size
        return self.cmd.size

# ----------------------------------------------------------------------
# Every processor module script must provide this function.
# It should return a new instance of a class derived from idaapi.processor_t
def PROCESSOR_ENTRY():
    return GsVmProcessor()
