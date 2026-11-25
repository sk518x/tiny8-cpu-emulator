"""The Tiny8 window. It only talks to the Controller, never to the CPU directly."""

import tkinter as tk


class App:
    def __init__(self, root):
        self.root = root
        root.title("Tiny8 CPU Emulator")

        # Row 0: the program box, with a label above it.
        program_frame = tk.Frame(root)
        program_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tk.Label(program_frame, text="Program").pack(anchor="w")
        self.program_box = tk.Text(program_frame, width=40, height=20, font=("Consolas", 11))
        self.program_box.pack(fill="both", expand=True)

        # Row 1: the four buttons side by side.
        button_frame = tk.Frame(root)
        button_frame.grid(row=1, column=0, sticky="w", padx=8)
        for name in ("Load", "Step", "Run", "Reset"):
            tk.Button(button_frame, text=name, width=8).pack(side="left", padx=2)

        # Row 2: the status bar.
        self.status = tk.Label(root, text="No program loaded", anchor="w")
        self.status.grid(row=2, column=0, sticky="ew", padx=8, pady=8)

        # Let the program area grow when the window is resized.
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()