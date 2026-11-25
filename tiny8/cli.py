"""Command-line tool: assemble a .asm file, run it, optionally print a trace."""

import argparse
import sys

from tiny8.assembler import MNEMONICS, NO_OPERAND, AssemblerError, assemble
from tiny8.cpu import CPU, MEMORY_SIZE, InvalidOpcodeError

# The assembler's table backwards: opcode number -> name.
NAMES = {opcode: name for name, opcode in MNEMONICS.items()}


def describe(opcode, operand):
    """Write an instruction the way a person would, e.g. 'LDA 5' or 'HLT'."""
    name = NAMES[opcode]
    if name in NO_OPERAND:
        return name
    return f"{name} {operand}"


def format_trace_line(step_number, pc, text, state):
    """One trace line: step number, where the instruction was, what it was, the state after it."""
    return (
        f"{step_number:>4}  pc={pc:03d}  {text:<10}"
        f"A={state['a']:<3} B={state['b']:<3} "
        f"Z={int(state['zero'])} C={int(state['carry'])}"
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tiny8", description="Assemble and run a Tiny8 program."
    )
    parser.add_argument("file", help="path to a .asm file")
    parser.add_argument("--trace", action="store_true", help="print one line per instruction")
    parser.add_argument(
        "--max-steps", type=int, default=100_000,
        help="stop after this many steps (default 100000)",
    )
    return parser


def main(argv=None):
    """Run the tool. Returns the exit code: 0 ok, 1 error, 2 step limit reached."""
    args = build_parser().parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as handle:
            source = handle.read()
    except OSError:
        print(f"error: cannot read file '{args.file}'", file=sys.stderr)
        return 1

    try:
        program = assemble(source)
    except AssemblerError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    cpu = CPU()
    cpu.load_program(program)

    steps = 0
    try:
        while not cpu.halted and steps < args.max_steps:
            # Look at the instruction BEFORE it runs, because step() moves the PC.
            pc = cpu.pc
            opcode = cpu.memory[pc]
            operand = cpu.memory[(pc + 1) % MEMORY_SIZE]
            state = cpu.step()
            steps += 1
            if args.trace:
                print(format_trace_line(steps, pc, describe(opcode, operand), state))
    except InvalidOpcodeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("Output: " + (" ".join(str(value) for value in cpu.output) or "(none)"))
    if cpu.halted:
        print(f"Halted after {steps} steps.")
        return 0
    print(f"Stopped at the step limit ({args.max_steps} steps) without halting.")
    return 2