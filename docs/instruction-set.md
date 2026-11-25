# Tiny8 instruction set

## The machine

- Registers: A (accumulator, does the arithmetic) and B (scratch), both 8-bit (0 to 255)
- Program counter (PC): 8-bit address of the next instruction
- Flags: Zero (Z) and Carry (C)
- Memory: 256 bytes, addresses 0 to 255. Program and data share it.
- Every instruction is 2 bytes: an opcode byte, then an operand byte.
  Instructions that need no operand still take 2 bytes (the operand is ignored).
- Convention: programs start at address 0. Keep your data at address 128 or above.

## Rules

1. **Zero flag:** after any instruction that changes A, Z = 1 if A is now 0, else 0.
   Other instructions leave Z alone.
2. **Carry flag:** ADD and ADDI set C = 1 if the true sum is above 255, else 0.
   SUB and SUBI set C = 1 if A was smaller than the number taken away (a "borrow"), else 0.
   Other instructions leave C alone.
3. **Wrap-around:** results are kept to 8 bits. 250 + 10 gives 4, and 3 - 5 gives 254.
4. **PC past 255:** the PC wraps back to 0.
5. **Unknown opcode:** the CPU stops with an error (`InvalidOpcodeError`).

## Instructions

| Opcode | Name | Operand | What it does            | Flags |
| ------ | ---- | ------- | ----------------------- | ----- |
| 0x00   | NOP  | ignored | does nothing            | none  |
| 0x01   | LDA  | value   | A = value               | Z     |
| 0x02   | LDB  | value   | B = value               | none  |
| 0x03   | LDM  | address | A = memory[address]     | Z     |
| 0x04   | STA  | address | memory[address] = A     | none  |
| 0x05   | ADD  | address | A = A + memory[address] | Z, C  |
| 0x06   | SUB  | address | A = A - memory[address] | Z, C  |
| 0x07   | ADDI | value   | A = A + value           | Z, C  |
| 0x08   | SUBI | value   | A = A - value           | Z, C  |
| 0x09   | JMP  | address | PC = address            | none  |
| 0x0A   | JZ   | address | if Z is 1, PC = address | none  |
| 0x0B   | JNZ  | address | if Z is 0, PC = address | none  |
| 0x0C   | OUT  | ignored | send A to the output    | none  |
| 0x0D   | TAB  | ignored | B = A                   | none  |
| 0x0E   | TBA  | ignored | A = B                   | Z     |
| 0x0F   | HLT  | ignored | stop the CPU            | none  |
