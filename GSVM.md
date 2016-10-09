GalaxyScript VM
===============

## Opcodes

 Opcode   | Mnemonic           | Notes
----------|--------------------|--------------------------------------
 00h      | add                | Arithmetic addition of two registers
 01h      | add_gc             | Adds two GC objects. 
 02h      | add_i21            | Arithmetic addition of a register and an IMM
 03h      | add_f              | Arithmetic addition of a fixed and an int.  ?
 04h      | and                | Bitwise AND of two registers
 05h      | ckarbnds           | Check array boundaries
 06h      | jz                 | Jump if register is == 0
 07h      | jmp                | Unconditional jump
 08h      | jnz                | Jump if register is != 0
 09h      | not                | Bitwise NOT of a register
 0Ah      | div                | Arithmetic division of two integer operands
 0Bh      | fdiv               | Arithmetic division of two fixed-int operands 
 0Ch      | decref             | TODO
 0Dh      | seteq              | Set if the two register operands are equal
 0Eh      | seteq_gc           | Set if the two GC object operands are equal
 0Fh      | call               | Calls a function
 10h      | setge              | Set if register operand 1 is greater than or equal to operand 2
 11h      | enter              | TODO
 12h      | bp/nop             | Software breakpoint / No operation
 13h      | ld_const_i21       | Loads an 21-bit IMM into a register. 
 14h      | ld_global32i       | Loads 32-bit global pointed to by an 21-bit IMM. 
 15h      | ld_global8i        | Loads 8-bit global pointed to by an 21-bit IMM. Result is zero-padded. 
 16h      | mov_r              | Moves a value from one register to another  TODO: also, some add thingy
 17h      | add_i8             | Arithmetic addition of a register and an 8-bit immediate. Result is zero-padded. 
 18h      | ld_local32b        | Loads 32-bit stack-memory addressed by BP + a 16-bit IMM offset. 
 19h      | ld_local32         | Loads 32-bit stack-memory addressed by reg + a 16-bit IMM offset. 
 1Ah      | ld_local8          | Loads 8-bit stack-memory addressed by reg + a 16-bit IMM offset. Result is zero-padded. 
 1Bh      | ld_global32        | Loads 32-bit global-memory addressed by reg + a 16-bit IMM offset. 
 1Ch      | ld_global8         | Loads 8-bit global-memory addressed by reg + a 16-bit IMM offset. Result is zero-padded. 
 1Dh      | ld_mem32           | Loads 32-bit stack or global-memory addressed by reg + a 16-bit IMM offset. Stack segment is mapped at 0x1000000, global at 0. 
 1Eh      | ld_mem8            | Loads 8-bit stack or global-memory addressed by reg + a 16-bit IMM offset. Stack segment is mapped at 0x1000000, global at 0. 
 1Fh      | mod                | Integer modulo of two registers. 
 20h      | mul                | Integer multiplication of two registers. 
 21h      | mul_i21            | Integer multiplication of a register and a 21-bit IMM. 
 22h      | fmul               | Fixed-int multiplication of two registers. 
 23h      | setneq             | Set if the two register operands are not equal. 
 24h      | neg                | Integer negation of a register operand. 
 25h      | setneq_gc          | Set if the two GC object operands are not equal. 
 26h      | seteq0             | Set if the register operand is zero. 
 27h      | or                 | Bitwise OR of two registers. 
 28h      | pop                | Pops up to 15 values from the stack. 
 29h      | push               | Pushes either a 21-bit IMM or a register value onto the stack. 
 2Ah      | push_local32       | Dereferences 32-bit stack memory addressed by reg + a 16-bit offset and pushes it onto the stack. 
 2Bh      | retn               | Returns from a function. 
 2Ch      | shl_r              | Shift bitwise left using two registers. 
 2Dh      | shl_i8             | Shift bitwise left using a register and a 8-bit IMM. 
 2Eh      | shr_r              | Shift bitwise right using two registers. 
 2Fh      | shr_i8             | Shift bitwise right using a register and a 8-bit IMM. 
 30h      | st_mem32           | Stores a 32-bit value from a register or 0 to either stack or global-memory. 
 31h      | st_mem8            | Stores an 8-bit value from a register or 0 to either stack or global-memory. 
 32h      | st_gc              | Stores a GC-handle from a register or 0 to either stack or global-memory. 
 33h      | mkgc               | Transforms a register value into a GC handle value. 
 34h      | mkstr              | Create a GS string from a VM data pointer IMM. 
 35h      | strcat             | Creates a new GS string by concatenating two existing GS strings. 
 36h      | TODO               | TODO
 37h      | sub                | Arithmetic subtraction of two register values. 
 38h      | sub_gc             | Subtraction of two GC objects. 
 39h      | xor                | Bitwise XOR of two registers. 
 3Ah..3Fh | ud_##              | Undefined.

## Registers
 ID    | Description
-------|------------
 0     | Unknown handle
 1..29 | General purpose
 30    | Base pointer
 31    | Stack pointer

## Instruction encoding
### Basic instruction format
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------------------------------------------------+
| opcode    | arguments                                         |
+-----------+---------------------------------------------------+
```

### Instruction specific encoding
#### add_r, and, div, div64, seteq, setge
Performs an operation with two register operands and stores the into a third
register.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+---------+---------+---------------------+
| opcode    | dst-reg | rhs-reg | lhs-reg | unused            |i|
+-----------+---------+---------+---------+---------------------+

dst-reg => Result destination register
rhs-reg => Right hand side operand register
lhs-reg => Left hand side operand register
i => Invert flag affecting the boolean result. Only valid for setge_r.
```
The performed operation depends on the opcode:

Opcode  | Operation
--------|---------------------------------------------------------
add_r   | Integer addition
and     | Bitwise AND
div     | Integer division
div64   | Integer division with 64-bit operands
seteq_r | Equality-checks LHS and RHS and stores the boolean result
seteq_gc| Equality-checks GC objects referred to by LHS and RHS and stores the boolean result
setge_r | Greater-equal-checks LHS and RHS and stores the boolean result

For `div` and `div64`, division by zero and numeric overflows result in
abortion of the execution with `e_divByZero` or
`e_numericOverflow`, respectively.

#### add_i21
Performs an arithmetic addition with a register and an 21-bit immediate as
operands stores the result back into the register.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+-----------------------------------------+
| opcode    | reg     | immediate                               |
+-----------+---------+-----------------------------------------+

reg => Left hand side of the operation and destination register.
```

#### not
Performs a bitwise NOT operation on a register operand and stores the result
into a second register.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+---------+-------------------------------+
| opcode    | dst-reg | o-reg   | unused                        |
+-----------+---------+---------+-------------------------------+

dst-reg => Result destination register
o-reg => Operand register
```

#### ckarbnds
Checks if a register's value is inside the given array size. In case its not,
execution is aborted returning either `e_arrayIndexUnderflow` or
`e_arrayIndexOverflow`.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+-----------------------------------------+
| opcode    | reg     | array size in elements                  |
+-----------+---------+-----------------------------------------+
```

#### jz, jmp, jnz
Jumps to an address relative from the next instruction.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+-----------------------------------------+
| opcode    | reg     | offset >> 2                             |
+-----------+---------+-----------------------------------------+
```
Usage of `reg` depends on the opcode. For `jz` and `jnz` the register
referred to by `reg` is required to be `== 0` and `!= 0`, respectively,
in order for the jump to be taken. The `jmp` instruction ignores the register
index.

#### ncall
Calls a native function by its index.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------+---------------------------------------+-+
| opcode    | ref-reg | nfunc index                           |r|
+-----------+---------+---------------------------------------+-+
r => When set to 1, inc-ref-hi is performed on result of call
```
If `ref-reg` is set to anything `!= 0`, the register value is used as the
native function index rather than `nfunc index`.

#### bp/nop
If debugging is enabled, this instruction represents a software breakpoint.
If not, no operation is performed and the instruction is simply skipped.
```
_  3                   2                   1                   0
 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
+-----------+---------------------------------------------------+
| opcode    | unused                                            |
+-----------+---------------------------------------------------+
```
