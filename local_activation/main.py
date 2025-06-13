import hashlib
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

SECRET = "MI_SECRETO_2024"


def obtener_serial() -> str:
    if os.name != "nt":
        return ""
    try:
        out = subprocess.check_output([
            "wmic",
            "diskdrive",
            "get",
            "SerialNumber",
        ], stderr=subprocess.DEVNULL, text=True)
        lines = [line.strip() for line in out.splitlines() if line.strip()][1:]
        return lines[0] if lines else ""
    except Exception:
        return ""


def _base36(num: int) -> str:
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return "0"
    digits = []
    while num:
        num, rem = divmod(num, 36)
        digits.append(chars[rem])
    return "".join(reversed(digits))


def clave_para(serial: str) -> str:
    digest = hashlib.sha256((serial + SECRET).encode()).hexdigest()
    return _base36(int(digest, 16))[:6].upper()


class VentanaActivacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Activacion")
        self.geometry("400x200")

        self.serial = obtener_serial()

        tk.Label(self, text="ID de equipo:").pack(pady=5)
        self.id_var = tk.StringVar(value=self.serial)
        id_entry = tk.Entry(self, textvariable=self.id_var, width=30, state="readonly")
        id_entry.pack(pady=5)

        tk.Button(self, text="Copiar ID", command=self._copiar).pack(pady=5)

        tk.Label(self, text="Clave de activacion:").pack(pady=5)
        self.clave_entry = tk.Entry(self, width=20)
        self.clave_entry.pack(pady=5)

        tk.Button(self, text="Verificar", command=self._verificar).pack(pady=10)

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.serial)
        messagebox.showinfo("Copiar", "ID copiado al portapapeles")

    def _verificar(self):
        clave = self.clave_entry.get().strip().upper()
        expected = clave_para(self.serial)
        if clave == expected:
            messagebox.showinfo("Licencia", "Clave correcta! Programa activado.")
            self.destroy()
            # Aqui continuaria el programa principal
            print("Programa principal...")
        else:
            messagebox.showerror("Licencia", "Clave incorrecta")


def main():
    VentanaActivacion().mainloop()


if __name__ == "__main__":
    main()
