import pytest

from tiny8.cpu import (
    CPU, InvalidOpcodeError,
    NOP, LDA, LDB, LDM, STA, ADD, SUB, ADDI, SUBI,
    JMP, JZ, JNZ, OUT, TAB, TBA, HLT,
)


def make_cpu(*program):
    """Make a CPU with the given bytes loaded at address 0."""
    cpu = CPU()
    cpu.load_program(list(program))
    return cpu


def test_new_cpu_starts_blank():
    cpu = CPU()
    assert cpu.a == 0
    assert cpu.b == 0
    assert cpu.pc == 0
    assert cpu.zero is False
    assert cpu.carry is False
    assert cpu.halted is False
    assert len(cpu.memory) == 256
    assert all(byte == 0 for byte in cpu.memory)


def test_load_program_copies_bytes_into_memory():
    cpu = make_cpu(LDA, 5, HLT, 0)
    assert cpu.memory[0:4] == [LDA, 5, HLT, 0]


def test_load_program_too_big_raises():
    cpu = CPU()
    with pytest.raises(ValueError):
        cpu.load_program([0] * 257)


def test_nop_only_moves_pc():
    cpu = make_cpu(NOP, 0)
    cpu.step()
    assert cpu.pc == 2
    assert cpu.a == 0


def test_lda_loads_value():
    cpu = make_cpu(LDA, 42)
    cpu.step()
    assert cpu.a == 42
    assert cpu.zero is False
    assert cpu.pc == 2


def test_lda_zero_sets_zero_flag():
    cpu = make_cpu(LDA, 5, LDA, 0)
    cpu.step()
    cpu.step()
    assert cpu.zero is True


def test_ldb_loads_b_and_leaves_flags():
    cpu = make_cpu(LDB, 9)
    cpu.step()
    assert cpu.b == 9
    assert cpu.zero is False


def test_sta_then_ldm_round_trip():
    cpu = make_cpu(LDA, 77, STA, 200, LDA, 0, LDM, 200)
    for _ in range(4):
        cpu.step()
    assert cpu.memory[200] == 77
    assert cpu.a == 77


def test_add_uses_memory_value():
    cpu = make_cpu(LDA, 5, ADD, 200)
    cpu.memory[200] = 3
    cpu.step()
    cpu.step()
    assert cpu.a == 8
    assert cpu.carry is False


def test_add_wraps_and_sets_carry():
    cpu = make_cpu(LDA, 250, ADDI, 10)
    cpu.step()
    cpu.step()
    assert cpu.a == 4
    assert cpu.carry is True


def test_add_to_exactly_256_gives_zero_and_carry():
    cpu = make_cpu(LDA, 255, ADDI, 1)
    cpu.step()
    cpu.step()
    assert cpu.a == 0
    assert cpu.zero is True
    assert cpu.carry is True


def test_sub_uses_memory_value():
    cpu = make_cpu(LDA, 9, SUB, 200)
    cpu.memory[200] = 4
    cpu.step()
    cpu.step()
    assert cpu.a == 5
    assert cpu.carry is False


def test_sub_borrow_wraps_and_sets_carry():
    cpu = make_cpu(LDA, 3, SUBI, 5)
    cpu.step()
    cpu.step()
    assert cpu.a == 254
    assert cpu.carry is True


def test_sub_to_zero_sets_zero_flag():
    cpu = make_cpu(LDA, 5, SUBI, 5)
    cpu.step()
    cpu.step()
    assert cpu.a == 0
    assert cpu.zero is True
    assert cpu.carry is False


def test_jmp_sets_pc():
    cpu = make_cpu(JMP, 100)
    cpu.step()
    assert cpu.pc == 100


def test_jz_jumps_when_zero():
    cpu = make_cpu(LDA, 0, JZ, 100)
    cpu.step()
    cpu.step()
    assert cpu.pc == 100


def test_jz_does_not_jump_when_not_zero():
    cpu = make_cpu(LDA, 1, JZ, 100)
    cpu.step()
    cpu.step()
    assert cpu.pc == 4


def test_jnz_jumps_when_not_zero():
    cpu = make_cpu(LDA, 1, JNZ, 100)
    cpu.step()
    cpu.step()
    assert cpu.pc == 100


def test_jnz_does_not_jump_when_zero():
    cpu = make_cpu(LDA, 0, JNZ, 100)
    cpu.step()
    cpu.step()
    assert cpu.pc == 4


def test_out_records_a():
    cpu = make_cpu(LDA, 7, OUT, 0, LDA, 8, OUT, 0)
    for _ in range(4):
        cpu.step()
    assert cpu.output == [7, 8]


def test_tab_copies_a_to_b():
    cpu = make_cpu(LDA, 6, TAB, 0)
    cpu.step()
    cpu.step()
    assert cpu.b == 6


def test_tba_copies_b_to_a_and_sets_zero():
    cpu = make_cpu(LDB, 0, LDA, 5, TBA, 0)
    for _ in range(3):
        cpu.step()
    assert cpu.a == 0
    assert cpu.zero is True


def test_hlt_stops_the_cpu():
    cpu = make_cpu(HLT, 0, LDA, 9)
    cpu.step()
    assert cpu.halted is True
    cpu.step()  # does nothing once halted
    assert cpu.a == 0
    assert cpu.pc == 2


def test_unknown_opcode_raises():
    cpu = make_cpu(0xFF, 0)
    with pytest.raises(InvalidOpcodeError):
        cpu.step()


def test_pc_wraps_past_255():
    cpu = CPU()
    cpu.pc = 254
    cpu.memory[254] = NOP
    cpu.step()
    assert cpu.pc == 0


def test_step_returns_state():
    cpu = make_cpu(LDA, 5)
    state = cpu.step()
    assert state["a"] == 5
    assert state["pc"] == 2
    assert state["zero"] is False
    assert state["halted"] is False


def test_run_stops_at_halt_and_counts_steps():
    cpu = make_cpu(LDA, 1, OUT, 0, HLT, 0)
    steps = cpu.run()
    assert steps == 3
    assert cpu.output == [1]


def test_run_stops_at_step_limit():
    cpu = make_cpu(JMP, 0)  # loops forever
    steps = cpu.run(max_steps=50)
    assert steps == 50
    assert cpu.halted is False