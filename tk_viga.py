import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np

# Directory to store progress
PROGRESO_DIR = os.path.join(os.path.dirname(__file__), "progreso")
STATE_FILE = os.path.join(PROGRESO_DIR, "estado.json")

if not os.path.exists(PROGRESO_DIR):
    os.makedirs(PROGRESO_DIR)

# ---------------------------------------------------------------------------
# Calculation helpers taken from existing PyQt implementation.
# ---------------------------------------------------------------------------
def correct_moments(mn, mp, system_type):
    """Apply NTP E.060 rules to moments."""
    mn = np.asarray(mn, dtype=float)
    mp = np.asarray(mp, dtype=float)

    f = 1 / 3 if system_type.lower() == "dual1" else 1 / 2

    min_face_pos = np.zeros(3)
    min_face_pos[[0, 2]] = f * np.abs(mn[[0, 2]])
    m_max = max(np.max(np.abs(mn)), np.max(np.abs(mp)))
    min_global = m_max / 4.0

    mp_corr = np.maximum.reduce([
        np.abs(mp),
        min_face_pos,
        np.full(3, min_global),
    ])

    mn_corr = -np.maximum(np.abs(mn), min_global)

    return mn_corr, mp_corr


def calc_as_req(Mu, fc, b, d, fy, phi):
    """Calculate required steel area for a single moment."""
    Mu_kgcm = abs(Mu) * 100000
    term = 1.7 * fc * b * d / (2 * fy)
    root = (2.89 * (fc * b * d) ** 2) / (fy ** 2) - (
        6.8 * fc * b * Mu_kgcm
    ) / (phi * (fy ** 2))
    root = max(root, 0)
    return term - 0.5 * np.sqrt(root)


def calc_as_limits(fc, fy, b, d):
    beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
    as_min = 0.7 * (np.sqrt(fc) / fy) * b * d
    pmax = 0.75 * ((0.85 * fc * beta1 / fy) * (6000 / (6000 + fy)))
    as_max = pmax * b * d
    return as_min, as_max

# ---------------------------------------------------------------------------
# Helper functions for state management
# ---------------------------------------------------------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as fh:
        json.dump(state, fh)


def reset_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


STATE = load_state()

# ---------------------------------------------------------------------------
# Tkinter frames
# ---------------------------------------------------------------------------
class SplashScreen(tk.Toplevel):
    def __init__(self, master, icon_path):
        super().__init__(master)
        self.overrideredirect(True)
        self.icon_path = icon_path
        img = Image.open(icon_path)
        self.photo = ImageTk.PhotoImage(img)
        label = tk.Label(self, image=self.photo)
        label.pack(expand=True, fill='both')
        self.after(2000, self.destroy)


class BaseFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

    def show(self):
        self.tkraise()


class MenuFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="VIGAPP060", font=("Arial", 18)).pack(pady=10)
        buttons = [
            ("Diagrama de Momentos", lambda: app.show_frame("momentos")),
            ("Diseño de Acero", lambda: app.goto_if_saved("momentos", "acero")),
            ("Desarrollo de Refuerzo", lambda: app.goto_if_saved("acero", "refuerzo")),
            ("Memoria de Cálculo", lambda: app.goto_if_saved("refuerzo", "memoria")),
            ("Limpiar Datos", app.limpiar_datos),
        ]
        for text, cmd in buttons:
            ttk.Button(self, text=text, command=cmd).pack(fill='x', pady=5, padx=20)


class MomentosFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="Diagrama de Momentos", font=("Arial", 14)).pack(pady=10)
        container = ttk.Frame(self)
        container.pack()
        self.entries_neg = []
        self.entries_pos = []
        for idx, lbl in enumerate(["M1-", "M2-", "M3-"]):
            ttk.Label(container, text=lbl).grid(row=0, column=idx)
            e = ttk.Entry(container, width=10)
            e.grid(row=1, column=idx)
            e.insert(0, "0.0")
            self.entries_neg.append(e)
        for idx, lbl in enumerate(["M1+", "M2+", "M3+"]):
            ttk.Label(container, text=lbl).grid(row=2, column=idx)
            e = ttk.Entry(container, width=10)
            e.grid(row=3, column=idx)
            e.insert(0, "0.0")
            self.entries_pos.append(e)
        self.sys_var = tk.StringVar(value="dual2")
        ttk.Radiobutton(self, text="Dual 1", variable=self.sys_var, value="dual1").pack()
        ttk.Radiobutton(self, text="Dual 2", variable=self.sys_var, value="dual2").pack()
        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btns, text="Menú Principal", command=lambda: app.show_frame("menu")).pack(side='left', padx=5)
        ttk.Button(btns, text="Continuar", command=lambda: app.show_next("momentos", "acero")).pack(side='left', padx=5)

    def guardar(self):
        try:
            mn = [-abs(float(e.get())) for e in self.entries_neg]
            mp = [abs(float(e.get())) for e in self.entries_pos]
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos")
            return
        sys_t = self.sys_var.get()
        mn_corr, mp_corr = correct_moments(mn, mp, sys_t)
        STATE['momentos'] = {
            'mn': mn,
            'mp': mp,
            'mn_corr': mn_corr.tolist(),
            'mp_corr': mp_corr.tolist(),
            'sys': sys_t,
        }
        save_state(STATE)
        messagebox.showinfo("Guardado", "Datos de momentos guardados")


class AceroFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="Diseño de Acero", font=("Arial", 14)).pack(pady=10)
        form = ttk.Frame(self)
        form.pack()
        labels = [
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("d (cm)", "40"),
            ("f'c (kg/cm²)", "210"),
            ("fy (kg/cm²)", "4200"),
            ("φ", "0.9"),
        ]
        self.edits = {}
        for i, (text, val) in enumerate(labels):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky='e')
            e = ttk.Entry(form, width=10)
            e.grid(row=i, column=1)
            e.insert(0, val)
            self.edits[text] = e
        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btns, text="Menú Principal", command=lambda: app.show_frame("menu")).pack(side='left', padx=5)
        ttk.Button(btns, text="Continuar", command=lambda: app.show_next("acero", "refuerzo")).pack(side='left', padx=5)

    def guardar(self):
        try:
            b = float(self.edits["b (cm)"].get())
            h = float(self.edits["h (cm)"].get())
            d = float(self.edits["d (cm)"].get())
            fc = float(self.edits["f'c (kg/cm²)"].get())
            fy = float(self.edits["fy (kg/cm²)"].get())
            phi = float(self.edits["φ"].get())
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return
        moments = STATE.get('momentos')
        if not moments:
            messagebox.showerror("Error", "Debe tener momentos guardados")
            return
        mn_c = np.array(moments['mn_corr'])
        mp_c = np.array(moments['mp_corr'])
        as_n = [calc_as_req(m, fc, b, d, fy, phi) for m in mn_c]
        as_p = [calc_as_req(m, fc, b, d, fy, phi) for m in mp_c]
        as_min, as_max = calc_as_limits(fc, fy, b, d)
        STATE['acero'] = {
            'b': b,
            'h': h,
            'd': d,
            'fc': fc,
            'fy': fy,
            'phi': phi,
            'as_n': as_n,
            'as_p': as_p,
            'as_min': as_min,
            'as_max': as_max,
        }
        save_state(STATE)
        messagebox.showinfo("Guardado", "Datos de diseño guardados")


class RefuerzoFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="Desarrollo de Refuerzo", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self, text="(contenido no implementado)").pack(pady=20)
        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btns, text="Menú Principal", command=lambda: app.show_frame("menu")).pack(side='left', padx=5)
        ttk.Button(btns, text="Continuar", command=lambda: app.show_next("refuerzo", "memoria")).pack(side='left', padx=5)

    def guardar(self):
        STATE['refuerzo'] = {'ok': True}
        save_state(STATE)
        messagebox.showinfo("Guardado", "Progreso de refuerzo guardado")


class MemoriaFrame(BaseFrame):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="Memoria de Cálculo", font=("Arial", 14)).pack(pady=10)
        self.text = tk.Text(self, width=60, height=20)
        self.text.pack()
        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btns, text="Menú Principal", command=lambda: app.show_frame("menu")).pack(side='left', padx=5)

    def guardar(self):
        STATE['memoria'] = {'texto': self.text.get('1.0', 'end')}
        save_state(STATE)
        messagebox.showinfo("Guardado", "Memoria almacenada")


class VigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VIGAPP060")
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "vigapp060.png")
        if os.path.exists(icon_path):
            try:
                self.iconphoto(True, tk.PhotoImage(file=icon_path))
            except Exception:
                pass
        self.frames = {}
        for key, FrameCls in {
            "menu": MenuFrame,
            "momentos": MomentosFrame,
            "acero": AceroFrame,
            "refuerzo": RefuerzoFrame,
            "memoria": MemoriaFrame,
        }.items():
            frame = FrameCls(self, self)
            self.frames[key] = frame
        self.show_frame("menu")
        self.after(0, self._maybe_show_splash, icon_path)

    # ------------------------------------------------------------------
    def _maybe_show_splash(self, icon_path):
        splash = SplashScreen(self, icon_path)
        self.wait_window(splash)

    def show_frame(self, key):
        frame = self.frames[key]
        frame.show()

    def goto_if_saved(self, required_key, target_key):
        if required_key not in STATE:
            messagebox.showwarning("Advertencia", "Debe completar el paso previo")
            return
        self.show_frame(target_key)

    def show_next(self, current_key, next_key):
        if current_key not in STATE:
            messagebox.showwarning("Advertencia", "Guarde antes de continuar")
            return
        self.show_frame(next_key)

    def limpiar_datos(self):
        if messagebox.askyesno("Limpiar", "¿Desea borrar todo el progreso?"):
            reset_state()
            STATE.clear()
            messagebox.showinfo("Limpieza", "Datos eliminados")
            self.show_frame("menu")


def main():
    app = VigApp()
    app.mainloop()


if __name__ == "__main__":
    main()
