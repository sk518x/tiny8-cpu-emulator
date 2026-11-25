from tiny8.controller import Controller

# Source lines:  1 LDA 2 / 2 loop: / 3 OUT / 4 SUBI 1 / 5 JNZ loop / 6 HLT
COUNTDOWN = "LDA 2\nloop:\nOUT\nSUBI 1\nJNZ loop\nHLT"


def test_new_controller_has_no_program():
    controller = Controller()
    assert controller.status() == "No program loaded"
    assert controller.current_line() is None


def test_step_does_nothing_without_a_program():
    controller = Controller()
    state = controller.step()
    assert state["pc"] == 0


def test_load_good_program():
    controller = Controller()
    assert controller.load(COUNTDOWN) is True
    assert controller.error is None
    assert controller.status() == "Ready"
    assert controller.current_line() == 1


def test_load_bad_program_reports_error():
    controller = Controller()
    assert controller.load("FOO 1") is False
    assert "line 1" in controller.error
    assert controller.status().startswith("Error")
    assert controller.current_line() is None


def test_step_does_nothing_after_failed_load():
    controller = Controller()
    controller.load("FOO 1")
    state = controller.step()
    assert state["pc"] == 0


def test_step_moves_the_highlighted_line():
    controller = Controller()
    controller.load(COUNTDOWN)
    state = controller.step()
    assert state["a"] == 2
    assert controller.current_line() == 3  # the label line is skipped; OUT is next


def test_run_goes_to_halt():
    controller = Controller()
    controller.load(COUNTDOWN)
    steps = controller.run()
    assert steps == 8
    assert controller.state()["output"] == [2, 1]
    assert controller.status() == "Halted"
    assert controller.current_line() is None


def test_run_stops_at_step_limit():
    controller = Controller()
    controller.load("loop: JMP loop")
    steps = controller.run(max_steps=10)
    assert steps == 10
    assert "step limit" in controller.status()


def test_reset_puts_the_program_back_at_the_start():
    controller = Controller()
    controller.load(COUNTDOWN)
    controller.run()
    controller.reset()
    state = controller.state()
    assert state["pc"] == 0
    assert state["output"] == []
    assert controller.status() == "Ready"
    assert controller.current_line() == 1
    controller.run()  # the program is still loaded, so it runs again
    assert controller.state()["output"] == [2, 1]


def test_runtime_error_is_caught_and_reported():
    # The program overwrites its own third instruction (address 4) with 255.
    controller = Controller()
    controller.load("LDA 255\nSTA 4\nNOP\nHLT")
    controller.run()
    assert "unknown opcode" in controller.error
    assert controller.status().startswith("Error")


def test_reset_clears_a_runtime_error():
    controller = Controller()
    controller.load("LDA 255\nSTA 4\nNOP\nHLT")
    controller.run()
    controller.reset()
    assert controller.error is None
    assert controller.status() == "Ready"