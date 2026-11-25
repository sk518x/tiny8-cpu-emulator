"""The Tiny8 CPU. It knows nothing about windows or files."""

MEMORY_SIZE = 256

# Opcodes: the number that identifies each instruction.
NOP, LDA, LDB, LDM, STA, ADD, SUB, ADDI, SUBI, JMP, JZ, JNZ, OUT, TAB, TBA, HLT = range(16)


class InvalidOpcodeError(Exception):
    """Raised when the CPU meets an opcode it doesn't know."""


class CPU:
    def __init__(self):
        self.reset()

    def reset(self):
        """Put everything back to blank, including memory."""
        self.a = 0
        self.b = 0
        self.pc = 0
        self.zero = False
        self.carry = False
        self.halted = False
        self.memory = [0] * MEMORY_SIZE
        self.output = []

    def load_program(self, program, start=0):
        """Copy a list of bytes into memory, beginning at `start`."""
        if start + len(program) > MEMORY_SIZE:
            raise ValueError("program does not fit in memory")
        for offset, byte in enumerate(program):
            self.memory[start + offset] = byte

    def _set_a(self, value):
        """Store a result in A, keep it to 8 bits, and update the Zero flag."""
        self.a = value & 0xFF
        self.zero = self.a == 0

    def step(self):
        """Run exactly one instruction and return the CPU's state."""
        if self.halted:
            return self.state()

        opcode = self.memory[self.pc]
        operand = self.memory[(self.pc + 1) % MEMORY_SIZE]

        if opcode > HLT:
            raise InvalidOpcodeError(f"unknown opcode {opcode:#04x} at address {self.pc}")

        # Move the PC first, so jump instructions can overwrite it below.
        self.pc = (self.pc + 2) % MEMORY_SIZE

        if opcode == NOP:
            pass
        elif opcode == LDA:
            self._set_a(operand)
        elif opcode == LDB:
            self.b = operand
        elif opcode == LDM:
            self._set_a(self.memory[operand])
        elif opcode == STA:
            self.memory[operand] = self.a
        elif opcode == ADD or opcode == ADDI:
            amount = self.memory[operand] if opcode == ADD else operand
            total = self.a + amount
            self.carry = total > 255
            self._set_a(total)
        elif opcode == SUB or opcode == SUBI:
            amount = self.memory[operand] if opcode == SUB else operand
            difference = self.a - amount
            self.carry = difference < 0
            self._set_a(difference)
        elif opcode == JMP:
            self.pc = operand
        elif opcode == JZ:
            if self.zero:
                self.pc = operand
        elif opcode == JNZ:
            if not self.zero:
                self.pc = operand
        elif opcode == OUT:
            self.output.append(self.a)
        elif opcode == TAB:
            self.b = self.a
        elif opcode == TBA:
            self._set_a(self.b)
        elif opcode == HLT:
            self.halted = True

        return self.state()

    def run(self, max_steps=100_000):
        """Step until halted or until max_steps. Returns the steps taken."""
        steps = 0
        while not self.halted and steps < max_steps:
            self.step()
            steps += 1
        return steps

    def state(self):
        """A snapshot of the CPU as a plain dictionary (copies, so it's safe to keep)."""
        return {
            "a": self.a,
            "b": self.b,
            "pc": self.pc,
            "zero": self.zero,
            "carry": self.carry,
            "halted": self.halted,
            "memory": list(self.memory),
            "output": list(self.output),
        }