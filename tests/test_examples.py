from pathlib import Path

from tiny8.assembler import assemble
from tiny8.cpu import CPU

EXAMPLES = Path(__file__).parent.parent / "examples"


def run_example(name):
    source = (EXAMPLES / name).read_text(encoding="utf-8")
    cpu = CPU()
    cpu.load_program(assemble(source))
    cpu.run()
    return cpu


def test_countdown():
    cpu = run_example("countdown.asm")
    assert cpu.halted is True
    assert cpu.output == [5, 4, 3, 2, 1]


def test_multiply():
    cpu = run_example("multiply.asm")
    assert cpu.halted is True
    assert cpu.output == [42]


def test_fibonacci():
    cpu = run_example("fibonacci.asm")
    assert cpu.halted is True
    assert cpu.output == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]