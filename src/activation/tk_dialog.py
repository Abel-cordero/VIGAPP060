"""Tkinter-based activation dialog using :mod:`src.activation`."""

import tkinter as tk
from tkinter import messagebox

from . import activate, check_activation, license_counter, machine_code


class VentanaActivacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Activacion")
        self.geometry("400x200")
        self.activated = False

        self.serial = machine_code()
        self.counter = license_counter()

        tk.Label(self, text="ID de equipo:").pack(pady=5)
        self.id_var = tk.StringVar(value=self.serial)
        id_entry = tk.Entry(self, textvariable=self.id_var,
                            width=30, state="readonly")
        id_entry.pack(pady=5)
        tk.Label(self, text=f"Contador: {self.counter}").pack(pady=5)

        tk.Button(self, text="Copiar ID", command=self._copiar).pack(pady=5)

        tk.Label(self, text="Clave de activacion:").pack(pady=5)
        self.clave_entry = tk.Entry(self, width=20)
        self.clave_entry.pack(pady=5)

        tk.Button(self, text="Verificar",
                  command=self._verificar).pack(pady=10)

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.serial)
        messagebox.showinfo("Copiar", "ID copiado al portapapeles")

    def _verificar(self):
        clave = self.clave_entry.get().strip()
        if activate(clave):
            messagebox.showinfo("Licencia", "Programa activado correctamente!")
            self.activated = True
            self.destroy()
        else:
            messagebox.showerror("Licencia", "Clave incorrecta")


def run_activation() -> bool:
    """Show the activation dialog and return ``True`` if validated."""
    if check_activation():
        return True
    win = VentanaActivacion()
    win.mainloop()
    return win.activated


if __name__ == "__main__":
    run_activation()
