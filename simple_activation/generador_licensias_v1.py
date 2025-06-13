import hashlib
import tkinter as tk
from tkinter import ttk

SECRET = "MI_SECRETO_2024"


def generate_activation(request_id: str) -> str:
    data = (request_id + SECRET).encode()
    return hashlib.sha256(data).hexdigest()


class LicenseGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("License Generator v1")
        self.geometry("500x200")
        self.configure(bg="#2b2b2b")

        self._build_ui()

    def _build_ui(self):
        padding = {"padx": 10, "pady": 5}

        ttk.Style().configure("TLabel", background="#2b2b2b", foreground="white")
        ttk.Style().configure("TButton", padding=5)

        req_label = ttk.Label(self, text="Request:")
        req_label.grid(row=0, column=0, sticky="w", **padding)
        self.request_entry = ttk.Entry(self, width=50)
        self.request_entry.grid(row=0, column=1, **padding)

        act_label = ttk.Label(self, text="Activation:")
        act_label.grid(row=1, column=0, sticky="w", **padding)
        self.activation_var = tk.StringVar()
        self.activation_entry = ttk.Entry(
            self,
            textvariable=self.activation_var,
            width=50,
            state="readonly",
        )
        self.activation_entry.grid(row=1, column=1, **padding)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, **padding)

        gen_btn = ttk.Button(btn_frame, text="Generate", command=self._on_generate)
        gen_btn.grid(row=0, column=0, padx=5)
        copy_btn = ttk.Button(btn_frame, text="Copy", command=self._on_copy)
        copy_btn.grid(row=0, column=1, padx=5)
        quit_btn = ttk.Button(btn_frame, text="Quit", command=self.destroy)
        quit_btn.grid(row=0, column=2, padx=5)

    def _on_generate(self):
        request = self.request_entry.get().strip()
        activation = generate_activation(request)
        self.activation_var.set(activation)

    def _on_copy(self):
        activation = self.activation_var.get()
        if activation:
            self.clipboard_clear()
            self.clipboard_append(activation)


def main():
    app = LicenseGenerator()
    app.mainloop()


if __name__ == "__main__":
    main()
