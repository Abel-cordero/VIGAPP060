import hashlib
import tkinter as tk
from tkinter import messagebox

SECRET = "MI_SECRETO_2024"


def _base36(num: int) -> str:
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return "0"
    digits = []
    while num:
        num, rem = divmod(num, 36)
        digits.append(chars[rem])
    return "".join(reversed(digits))


def generar_clave(equipo_id: str) -> str:
    digest = hashlib.sha256((equipo_id + SECRET).encode()).hexdigest()
    return _base36(int(digest, 16))[:6].upper()


class GeneradorLicencia(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Licencia")
        self.geometry("500x200")

        tk.Label(self, text="ID de equipo:").pack(pady=5)
        self.id_entry = tk.Entry(self, width=40)
        self.id_entry.pack(pady=5)

        tk.Label(self, text="Clave generada:").pack(pady=5)
        self.clave_var = tk.StringVar()
        self.clave_entry = tk.Entry(self, textvariable=self.clave_var, width=40, state="readonly")
        self.clave_entry.pack(pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Generar", command=self._generar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Copiar", command=self._copiar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Salir", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _generar(self):
        equipo_id = self.id_entry.get().strip()
        if not equipo_id:
            messagebox.showwarning("Error", "Ingrese el ID")
            return
        self.clave_var.set(generar_clave(equipo_id))

    def _copiar(self):
        clave = self.clave_var.get()
        if clave:
            self.clipboard_clear()
            self.clipboard_append(clave)
            messagebox.showinfo("Copiar", "Clave copiada al portapapeles")


def main():
    GeneradorLicencia().mainloop()


if __name__ == "__main__":
    main()
