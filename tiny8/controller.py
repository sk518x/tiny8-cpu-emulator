"""The controller: sits between the CPU and any user interface.

It knows nothing about windows. A window asks it to load, step, run or reset,
and asks it what to display. Because it is plain Python, it can be tested.
"""

from tiny8.assembler import AssemblerError, assemble_with_lines
from tiny8.cpu import CPU, InvalidOpcodeError


class Controller:
    def __init__(self):
        self.cpu = CPU()
        self.program = []
        self.line_numbers = []
        self.loaded = False
        self.error = None
        self.limit_reached = False

    def load(self, source):
        """Assemble the text and get ready to run it. Returns True if it worked."""
        try:
            program, line_numbers = assemble_with_lines(source)
        except AssemblerError as error:
            self.loaded = False
            self.cpu.reset()
            self.error = str(error)
            return False
        self.program = program
        self.line_numbers = line_numbers
        self.loaded = True
        self.reset()
        return True

    def reset(self):
        """Go back to the start of the loaded program, with blank registers."""
        self.cpu.reset()
        self.error = None
        self.limit_reached = False
        if self.loaded:
            self.cpu.load_program(self.program)

    def can_step(self):
        """True when there is a program, nothing has gone wrong, and it hasn't halted."""
        return self.loaded and self.error is None and not self.cpu.halted

    def step(self):
        """Run one instruction (if possible) and return the CPU state."""
        self.limit_reached = False
        if self.can_step():
            try:
                self.cpu.step()
            except InvalidOpcodeError as error:
                self.error = str(error)
        return self.cpu.state()

    def run(self, max_steps=100_000):
        """Step until halted, an error, or max_steps. Returns the steps taken."""
        steps = 0
        while self.can_step() and steps < max_steps:
            self.step()
            steps += 1
        # If we can still step, the loop ended because of the limit.
        self.limit_reached = self.can_step()
        return steps

    def state(self):
        return self.cpu.state()

    def current_line(self):
        """The source line number of the instruction about to run, or None."""
        if not self.can_step():
            return None
        pc = self.cpu.pc
        index = pc // 2
        if pc % 2 == 0 and index < len(self.line_numbers):
            return self.line_numbers[index]
        return None

    def status(self):
        """A short message for a status bar."""
        if self.error:
            return f"Error: {self.error}"
        if not self.loaded:
            return "No program loaded"
        if self.cpu.halted:
            return "Halted"
        if self.limit_reached:
            return "Stopped at the step limit"
        return "Ready"