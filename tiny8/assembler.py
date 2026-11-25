"""The Tiny8 assembler: turns assembly text into a list of bytes."""

import re

from tiny8.cpu import (
    MEMORY_SIZE,
    NOP, LDA, LDB, LDM, STA, ADD, SUB, ADDI, SUBI,
    JMP, JZ, JNZ, OUT, TAB, TBA, HLT,
)

MNEMONICS = {
    "NOP": NOP, "LDA": LDA, "LDB": LDB, "LDM": LDM, "STA": STA,
    "ADD": ADD, "SUB": SUB, "ADDI": ADDI, "SUBI": SUBI,
    "JMP": JMP, "JZ": JZ, "JNZ": JNZ,
    "OUT": OUT, "TAB": TAB, "TBA": TBA, "HLT": HLT,
}

# These instructions ignore their operand byte, so we don't allow one to be written.
NO_OPERAND = {"NOP", "OUT", "TAB", "TBA", "HLT"}

LABEL_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class AssemblerError(Exception):
    """Raised when the assembly text has a mistake. The message names the line."""

def assemble(source):
    """Turn assembly text into a list of bytes the CPU can load."""
    return assemble_with_lines(source)[0]


def assemble_with_lines(source):
    """Like assemble, but also returns the source line number of each instruction.

    Returns (program, lines). lines[n] is the line of the n-th instruction,
    which starts at address n * 2. A window uses this to highlight the line
    that is about to run.
    """

    labels = {}
    instructions = []  # each item: (line number, mnemonic, operand text or None)

    # Pass 1: read every line, remember where each label points.
    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        text = raw_line.split(";")[0].strip()

        if ":" in text:
            name, text = text.split(":", 1)
            name = name.strip()
            text = text.strip()
            if not LABEL_PATTERN.match(name):
                raise AssemblerError(f"line {line_number}: bad label name '{name}'")
            if name in labels:
                raise AssemblerError(f"line {line_number}: label '{name}' is already defined")
            labels[name] = len(instructions) * 2

        if not text:
            continue

        parts = text.split()
        mnemonic = parts[0].upper()
        operands = parts[1:]

        if mnemonic not in MNEMONICS:
            raise AssemblerError(f"line {line_number}: unknown instruction '{parts[0]}'")
        if len(operands) > 1:
            raise AssemblerError(f"line {line_number}: too many operands")
        if mnemonic in NO_OPERAND and operands:
            raise AssemblerError(f"line {line_number}: {mnemonic} takes no operand")
        if mnemonic not in NO_OPERAND and not operands:
            raise AssemblerError(f"line {line_number}: {mnemonic} needs an operand")

        operand_text = operands[0] if operands else None
        instructions.append((line_number, mnemonic, operand_text))

    if len(instructions) * 2 > MEMORY_SIZE:
        raise AssemblerError(f"program is too big: {len(instructions) * 2} bytes, memory holds {MEMORY_SIZE}")

    # Pass 2: now every label is known, so produce the bytes.
    program = []
    for line_number, mnemonic, operand_text in instructions:
        program.append(MNEMONICS[mnemonic])
        program.append(_resolve_operand(operand_text, labels, line_number))
    return program, [line_number for line_number, _, _ in instructions]


def _resolve_operand(text, labels, line_number):
    """Turn operand text (a label, decimal or hex) into a number from 0 to 255."""
    if text is None:
        return 0
    if text in labels:
        return labels[text]
    try:
        value = int(text, 0)  # base 0 means: understand 0x1F as hex, 31 as decimal
    except ValueError:
        if LABEL_PATTERN.match(text):
            raise AssemblerError(f"line {line_number}: unknown label '{text}'") from None
        raise AssemblerError(f"line {line_number}: '{text}' is not a valid number") from None
    if not 0 <= value <= 255:
        raise AssemblerError(f"line {line_number}: {value} does not fit in one byte (0 to 255)")
    return value