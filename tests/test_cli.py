from tiny8.cli import main


def write_program(tmp_path, text):
    path = tmp_path / "program.asm"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_run_prints_output_and_step_count(tmp_path, capsys):
    path = write_program(tmp_path, "LDA 7\nOUT\nHLT")
    code = main([path])
    out = capsys.readouterr().out
    assert code == 0
    assert "Output: 7" in out
    assert "Halted after 3 steps" in out
    assert "pc=" not in out  # no trace unless asked


def test_trace_prints_one_line_per_instruction(tmp_path, capsys):
    path = write_program(tmp_path, "LDA 5\nOUT\nHLT")
    code = main([path, "--trace"])
    lines = capsys.readouterr().out.splitlines()
    trace_lines = [line for line in lines if "pc=" in line]
    assert code == 0
    assert len(trace_lines) == 3
    assert "pc=000" in trace_lines[0]
    assert "LDA 5" in trace_lines[0]
    assert "A=5" in trace_lines[0]
    assert "OUT" in trace_lines[1]


def test_assembler_error_returns_1(tmp_path, capsys):
    path = write_program(tmp_path, "FOO 1")
    code = main([path])
    assert code == 1
    assert "line 1" in capsys.readouterr().err


def test_missing_file_returns_1(tmp_path, capsys):
    code = main([str(tmp_path / "nope.asm")])
    assert code == 1
    assert "cannot read" in capsys.readouterr().err


def test_step_limit_returns_2(tmp_path, capsys):
    path = write_program(tmp_path, "loop: JMP loop")
    code = main([path, "--max-steps", "20"])
    assert code == 2
    assert "step limit" in capsys.readouterr().out


def test_invalid_opcode_at_runtime_returns_1(tmp_path, capsys):
    # The program overwrites its own third instruction (address 4) with 255.
    path = write_program(tmp_path, "LDA 255\nSTA 4\nNOP\nHLT")
    code = main([path])
    assert code == 1
    assert "unknown opcode" in capsys.readouterr().err