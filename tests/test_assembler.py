import pytest

from tiny8.assembler import assemble, AssemblerError
from tiny8.cpu import CPU, NOP, LDA, SUBI, JMP, JNZ, OUT, HLT


def test_single_instruction():
    assert assemble("LDA 5") == [LDA, 5]


def test_no_operand_instruction_gets_a_zero_byte():
    assert assemble("HLT") == [HLT, 0]


def test_mnemonics_are_not_case_sensitive():
    assert assemble("lda 5") == [LDA, 5]


def test_hex_operand():
    assert assemble("LDA 0x1F") == [LDA, 31]


def test_comments_and_blank_lines_are_ignored():
    source = """
    ; a whole-line comment
    LDA 1   ; a trailing comment

    HLT
    """
    assert assemble(source) == [LDA, 1, HLT, 0]


def test_backward_label():
    source = """
    start:
        OUT
        JMP start
    """
    assert assemble(source) == [OUT, 0, JMP, 0]


def test_forward_label():
    source = """
        JMP end
        NOP
    end:
        HLT
    """
    assert assemble(source) == [JMP, 4, NOP, 0, HLT, 0]


def test_label_on_the_same_line_as_an_instruction():
    assert assemble("loop: SUBI 1\nJNZ loop") == [SUBI, 1, JNZ, 0]


def test_unknown_mnemonic():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("FOO 1")


def test_missing_operand():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("LDA")


def test_operand_given_to_instruction_that_takes_none():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("HLT 5")


def test_too_many_operands():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("LDA 1 2")


def test_undefined_label():
    with pytest.raises(AssemblerError, match="nowhere"):
        assemble("JMP nowhere")


def test_duplicate_label():
    with pytest.raises(AssemblerError, match="line 2"):
        assemble("a: NOP\na: NOP")


def test_bad_number():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("LDA 12abc")


def test_operand_out_of_range():
    with pytest.raises(AssemblerError, match="line 1"):
        assemble("LDA 256")


def test_error_reports_the_right_line_number():
    with pytest.raises(AssemblerError, match="line 3"):
        assemble("NOP\nNOP\nFOO")


def test_program_too_big_for_memory():
    with pytest.raises(AssemblerError):
        assemble("NOP\n" * 129)  # 129 instructions x 2 bytes = 258 bytes


def test_assembled_program_runs_on_the_cpu():
    source = """
        LDA 3
    loop:
        OUT
        SUBI 1
        JNZ loop
        HLT
    """
    cpu = CPU()
    cpu.load_program(assemble(source))
    cpu.run()
    assert cpu.output == [3, 2, 1]