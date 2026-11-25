"""The Tiny8 window. It only talks to the Controller, never to the CPU directly."""

import tkinter as tk

from tiny8.controller import Controller


class App:
    def __init__(self, root):
        self.root = root
        self.controller = Controller()
        root.title("Tiny8 CPU Emulator")

        # Row 0: the program box, with a label above it.
        program_frame = tk.Frame(root)
        program_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tk.Label(program_frame, text="Program").pack(anchor="w")
        self.program_box = tk.Text(program_frame, width=40, height=20, font=("Consolas", 11))
        self.program_box.pack(fill="both", expand=True)
        self.program_box.tag_configure("current", background="gold")

        # Row 1: the four buttons side by side.
        button_frame = tk.Frame(root)
        button_frame.grid(row=1, column=0, sticky="w", padx=8)
        buttons = (
            ("Load", self.on_load),
            ("Step", self.on_step),
            ("Run", self.on_run),
            ("Reset", self.on_reset),
        )
        for name, callback in buttons:
            tk.Button(button_frame, text=name, width=8, command=callback).pack(side="left", padx=2)

        # Row 2: the status bar.
        self.status = tk.Label(root, text="No program loaded", anchor="w")
        self.status.grid(row=2, column=0, sticky="ew", padx=8, pady=8)

        # Let the program area grow when the window is resized.
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Right-hand side: registers, flags and output.
        info_frame = tk.Frame(root)
        info_frame.grid(row=0, column=1, sticky="n", padx=8, pady=8)

        tk.Label(info_frame, text="CPU").pack(anchor="w")
        self.cpu_label = tk.Label(
            info_frame, text="", font=("Consolas", 11), justify="left", anchor="w"
        )
        self.cpu_label.pack(anchor="w", pady=(0, 12))

        tk.Label(info_frame, text="Output").pack(anchor="w")
        self.output_box = tk.Text(info_frame, width=24, height=8, font=("Consolas", 11))
        self.output_box.config(state="disabled")
        self.output_box.pack()

        # Memory grid: 16 rows x 16 columns, one cell per address.
        memory_frame = tk.Frame(root)
        memory_frame.grid(row=0, column=2, sticky="n", padx=8, pady=8)
        tk.Label(memory_frame, text="Memory (hex)").grid(row=0, column=0, columnspan=17, sticky="w")

        # Column headings 0..F across the top.
        for col in range(16):
            tk.Label(memory_frame, text=f"{col:X}", font=("Consolas", 9), fg="gray").grid(
                row=1, column=col + 1
            )

        self.memory_cells = []
        for row in range(16):
            # Row heading 0..F down the left side.
            tk.Label(memory_frame, text=f"{row:X}", font=("Consolas", 9), fg="gray").grid(
                row=row + 2, column=0
            )
            for col in range(16):
                cell = tk.Label(
                    memory_frame, text="00", font=("Consolas", 9), width=3, relief="flat"
                )
                cell.grid(row=row + 2, column=col + 1)
                self.memory_cells.append(cell)
        
        self.refresh()

    def on_load(self):
        source = self.program_box.get("1.0", "end")
        self.controller.load(source)
        self.refresh()

    def on_step(self):
        self.controller.step()
        self.refresh()

    def on_run(self):
        self.controller.run()
        self.refresh()

    def on_reset(self):
        self.controller.reset()
        self.refresh()

    def refresh(self):
        """Redraw everything that depends on the controller's state."""
        state = self.controller.state()
        self.status.config(text=self.controller.status())
        self.cpu_label.config(
            text=(
                f"A  = {state['a']:>3}  (0x{state['a']:02X})\n"
                f"B  = {state['b']:>3}  (0x{state['b']:02X})\n"
                f"PC = {state['pc']:>3}  (0x{state['pc']:02X})\n"
                f"Zero  = {int(state['zero'])}\n"
                f"Carry = {int(state['carry'])}"
            )
        )
        
        # Program box: highlight the source line that is about to run.
        self.program_box.tag_remove("current", "1.0", "end")
        line = self.controller.current_line()
        if line is not None:
            self.program_box.tag_add("current", f"{line}.0", f"{line}.end")
            self.program_box.see(f"{line}.0")

        # A disabled text box must be switched on briefly before we can change it.
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", "\n".join(str(v) for v in state["output"]))
        self.output_box.config(state="disabled")

        # Memory grid: show each byte in hex, and highlight where the PC points.
        pc = state["pc"]
        for address, cell in enumerate(self.memory_cells):
            cell.config(text=f"{state['memory'][address]:02X}", bg="SystemButtonFace")
        if self.controller.can_step():
            self.memory_cells[pc].config(bg="gold")
            self.memory_cells[(pc + 1) % 256].config(bg="khaki")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()