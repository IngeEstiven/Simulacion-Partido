
"""
SIMULADOR DINÁMICO DEL PRIMER TIEMPO · BRASIL vs ALEMANIA
==========================================================
Qué hace
  * Reproduce, evento por evento, los datos que tomaste (lista EVENTOS_REALES).
  * El balón se mueve, los 22 jugadores se desplazan y se ve quién tiene el balón.
  * Cada tipo de evento tiene su color y su animación (tiro, gol, córner,
    saque de banda, falta, fuera de juego, etc.).
  * Cuando el balón sale (banda / línea de fondo) cambia a naranja y se
    resalta el borde por donde salió.
  * Usa también tus variables continuas (posesión, zona de control, intensidad).
  * Modo "Aleatorio": genera un partido nuevo con la distribución exponencial
    y las probabilidades ajustadas en tu notebook.

Atajos: ESPACIO = iniciar / pausar      R = reiniciar
"""
import math
import random
import time
import tkinter as tk
from tkinter import ttk

# DATOS 

LOCAL = "BRASIL"
VISITANTE = "ALEMANIA"

# (minuto, código, equipo)
EVENTOS_REALES = [
    (0, 'INI', '-'),
    (1, 'COR', 'BRASIL'),
    (2, 'REC', 'BRASIL'),
    (2, 'SAB', 'BRASIL'),
    (2, 'TIR', 'BRASIL'),
    (3, 'SAB', 'ALEMANIA'),
    (3, 'SAB', 'ALEMANIA'),
    (4, 'SAB', 'ALEMANIA'),
    (4, 'SAB', 'ALEMANIA'),
    (5, 'PER', 'ALEMANIA'),
    (5, 'SAB', 'BRASIL'),
    (6, 'SAB', 'ALEMANIA'),
    (6, 'SAB', 'BRASIL'),
    (7, 'FAL', 'BRASIL'),
    (9, 'FAL', 'BRASIL'),
    (9, 'FAL', 'BRASIL'),
    (10, 'COR', 'ALEMANIA'),
    (10, 'TIR', 'ALEMANIA'),
    (10, 'GOL', 'ALEMANIA'),
    (12, 'SAP', 'ALEMANIA'),
    (13, 'PER', 'BRASIL'),
    (13, 'FAL', 'BRASIL'),
    (14, 'SAB', 'BRASIL'),
    (15, 'FAL', 'ALEMANIA'),
    (17, 'COR', 'ALEMANIA'),
    (19, 'FAL', 'BRASIL'),
    (19, 'SAB', 'BRASIL'),
    (20, 'SAB', 'ALEMANIA'),
    (20, 'COR', 'ALEMANIA'),   # ⚠ minuto estimado: pon el real
    (22, 'TIR', 'ALEMANIA'),
    (22, 'TIR', 'ALEMANIA'),
    (22, 'GOL', 'ALEMANIA'),
    (24, 'TIR', 'ALEMANIA'),
    (24, 'GOL', 'ALEMANIA'),
    (25, 'TIR', 'ALEMANIA'),
    (25, 'GOL', 'ALEMANIA'),
    (27, 'SAB', 'BRASIL'),
    (28, 'SAB', 'BRASIL'),
    (28, 'SAP', 'ALEMANIA'),
    (28, 'SAB', 'ALEMANIA'),
    (29, 'TIR', 'ALEMANIA'),
    (29, 'GOL', 'ALEMANIA'),
    (31, 'FAL', 'ALEMANIA'),
    (32, 'TIR', 'ALEMANIA'),
    (32, 'COR', 'ALEMANIA'),
    (33, 'FAL', 'ALEMANIA'),
    (33, 'SAB', 'ALEMANIA'),
    (34, 'SAB', 'BRASIL'),
    (35, 'FDJ', 'BRASIL'),
    (36, 'SAB', 'ALEMANIA'),
    (37, 'FAL', 'ALEMANIA'),
    (38, 'TIR', 'ALEMANIA'),
    (38, 'SAP', 'BRASIL'),
    (39, 'SAB', 'BRASIL'),
    (40, 'COR', 'BRASIL'),     # ⚠ minuto estimado: pon el real
    (42, 'SAB', 'BRASIL'),
    (42, 'SAB', 'ALEMANIA'),
    (43, 'FAL', 'BRASIL'),
    (44, 'SAB', 'BRASIL'),
    (45, 'PER', 'BRASIL'),
    (46, 'SAP', 'ALEMANIA'),
]

# (minuto, posesión_A(Brasil), posesión_B(Alemania), zona_control, intensidad)
VARIABLES = [
    (0, 55, 45, 'Medio', 'Media'),
    (5, 52, 48, 'Brasil', 'Media'),
    (10, 50, 50, 'Medio', 'Alta'),
    (15, 48, 52, 'Alemania', 'Alta'),
    (20, 45, 55, 'Alemania', 'Muy alta'),
    (25, 40, 60, 'Alemania', 'Muy alta'),
    (30, 42, 58, 'Alemania', 'Alta'),
    (35, 45, 55, 'Alemania', 'Media'),
    (40, 47, 53, 'Medio', 'Media'),
    (45, 48, 52, 'Medio', 'Baja'),
]

# Para el modo aleatorio: (eventos de Brasil, eventos de Alemania)
FRECUENCIAS = {
    'GOL': (0, 5), 'TIR': (1, 8), 'PER': (2, 1), 'REC': (1, 0), 'FAL': (6, 4),
    'SAB': (11, 10), 'COR': (2, 4), 'FDJ': (1, 0), 'SAP': (1, 3),
}
ESCALA_EXP = 0.7931          # escala de la exponencial ajustada (min entre eventos)
SUAVIZADO = 0.5              # modo aleatorio: se suma a los conteos por equipo para que un
                             # evento que un equipo nunca tuvo (p. ej. gol de Brasil) sea
                             # posible pero raro. Pon 0 para usar tus frecuencias exactas.

# Nombres de jugadores {equipo: {número: "Nombre"}} (alineación titular, 4-2-3-1)
NOMBRES = {
    LOCAL: {12: 'Júlio César', 23: 'Maicon', 4: 'David Luiz', 13: 'Dante', 6: 'Marcelo',
            5: 'Fernandinho', 17: 'Luiz Gustavo', 20: 'Bernard', 11: 'Oscar', 7: 'Hulk',
            9: 'Fred'},
    VISITANTE: {1: 'Neuer', 4: 'Höwedes', 20: 'Boateng', 5: 'Hummels', 16: 'Lahm',
                6: 'Khedira', 7: 'Schweinsteiger', 8: 'Özil', 18: 'Kroos', 13: 'Müller',
                11: 'Klose'},
}

# ============================================================================
# 2. ESTILO
# ============================================================================
BG = '#0b1220'
PANEL = '#111a2e'
TXT = '#e5edf9'
MUTED = '#7f8ea8'
GRASS_A = '#1f8a4c'
GRASS_B = '#1a7b43'
LINEA = '#e9fff0'
NARANJA = '#ff5a1f'

COLOR_EVENTO = {
    'INI': '#cbd5e1', 'GOL': '#ffd60a', 'TIR': '#a78bfa', 'COR': '#22d3ee',
    'SAB': '#fb923c', 'FAL': '#ef4444', 'PER': '#f472b6', 'REC': '#34d399',
    'SAP': '#60a5fa', 'FDJ': '#f0abfc', 'TAR-A': '#facc15', 'TAR-R': '#dc2626',
    'SUS': '#94a3b8', 'PEN': '#fb7185',
}
DESC = {
    'INI': 'Inicio del partido', 'GOL': 'Gol', 'TIR': 'Tiro', 'COR': 'Tiro de esquina',
    'SAB': 'Saque de banda', 'FAL': 'Falta', 'PER': 'Pérdida de balón',
    'REC': 'Recuperación', 'SAP': 'Saque de puerta', 'FDJ': 'Fuera de juego',
    'TAR-A': 'Tarjeta amarilla', 'TAR-R': 'Tarjeta roja', 'SUS': 'Sustitución',
    'PEN': 'Penal',
}
COL_EQ = {LOCAL: '#facc15', VISITANTE: '#e2e8f0'}
KIT = {
    LOCAL: dict(fill='#facc15', borde='#15803d', num='#14532d', gk='#38bdf8'),
    VISITANTE: dict(fill='#f8fafc', borde='#111827', num='#111827', gk='#a78bfa'),
}
INTENSIDAD = {'Baja': 0.6, 'Media': 1.0, 'Alta': 1.35, 'Muy alta': 1.7}
ZONA_DESP = {'Brasil': 0.05, 'Medio': 0.0, 'Alemania': -0.05}
MODOS = ("Datos reales (tu toma)", "Aleatorio (distribución ajustada)")

# (número, rol, x relativo a su propia portería, y)  ·  4-2-3-1 los dos equipos
# El último de cada lista debe ser el delantero (es quien saca del centro).
FORMACION_LOCAL = [
    (12, 'POR', 0.05, 0.50),
    (23, 'DEF', 0.20, 0.88), (4, 'DEF', 0.17, 0.63), (13, 'DEF', 0.17, 0.37), (6, 'DEF', 0.20, 0.12),
    (5, 'MED', 0.33, 0.62), (17, 'MED', 0.33, 0.38),
    (20, 'MED', 0.50, 0.80), (11, 'MED', 0.50, 0.50), (7, 'MED', 0.50, 0.20),
    (9, 'DEL', 0.62, 0.50),
]
FORMACION_VISIT = [
    (1, 'POR', 0.05, 0.50),
    (4, 'DEF', 0.20, 0.88), (20, 'DEF', 0.17, 0.63), (5, 'DEF', 0.17, 0.37), (16, 'DEF', 0.20, 0.12),
    (6, 'MED', 0.33, 0.62), (7, 'MED', 0.33, 0.38),
    (8, 'MED', 0.50, 0.80), (18, 'MED', 0.50, 0.50), (13, 'MED', 0.50, 0.20),
    (11, 'DEL', 0.62, 0.50),
]

MIN_POR_SEG = 0.5            # minutos de partido por segundo (velocidad x1)
ASPECTO = 105 / 68           # largo / ancho de la cancha


# ============================================================================
# 3. UTILIDADES
# ============================================================================
def mezclar(c1, c2, t):
    """Mezcla dos colores hex (t=0 -> c1, t=1 -> c2). Sirve para desvanecer."""
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dist(a, b):
    return math.hypot((a[0] - b[0]) * ASPECTO, a[1] - b[1])


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Jugador:
    __slots__ = ('equipo', 'num', 'rol', 'base', 'pos', 'override', 'fase', 'nombre')

    def __init__(self, equipo, num, rol, bx, by):
        self.equipo, self.num, self.rol = equipo, num, rol
        self.base = (bx, by)
        self.pos = [bx, by]
        self.override = None
        self.fase = random.random() * 6.28
        self.nombre = NOMBRES.get(equipo, {}).get(num, f"Jugador {num}")


# ============================================================================
# 4. APLICACIÓN
# ============================================================================
class Simulador:
    def __init__(self, root):
        self.root = root
        root.title("Simulador del primer tiempo · Brasil vs Alemania")
        root.configure(bg=BG)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{min(1420, sw - 60)}x{min(880, sh - 100)}+20+20")
        root.minsize(1100, 660)

        self.PW = None
        self.speed = 1.5
        self.eventos = []
        self.t_total = 45.0
        self.tl_geom = None
        self.modo = tk.StringVar(value=MODOS[0])
        self.var_vel = tk.DoubleVar(value=self.speed)
        self._txt_balon = None
        self._frame = 0

        self.crear_equipos()
        self.construir_ui()
        self.reiniciar()
        self.ultimo_t = time.perf_counter()
        self.tick()

    # ------------------------------------------------------------------ equipos
    def crear_equipos(self):
        self.equipos = {LOCAL: [], VISITANTE: []}
        for num, rol, x, y in FORMACION_LOCAL:
            self.equipos[LOCAL].append(Jugador(LOCAL, num, rol, x, y))
        for num, rol, x, y in FORMACION_VISIT:
            self.equipos[VISITANTE].append(Jugador(VISITANTE, num, rol, 1 - x, y))

    def jugador(self, eq, num):
        for p in self.equipos[eq]:
            if p.num == num:
                return p
        return self.equipos[eq][-1]

    # ----------------------------------------------------------------------- UI
    def construir_ui(self):
        est = ttk.Style()
        try:
            est.theme_use('clam')
        except tk.TclError:
            pass
        fuente = ('Segoe UI', 10, 'bold')
        est.configure('Acc.TButton', background='#22c55e', foreground='#052e16',
                      font=fuente, padding=(16, 8), borderwidth=0, focuscolor='#22c55e')
        est.map('Acc.TButton', background=[('active', '#4ade80')])
        est.configure('Dk.TButton', background='#1e293b', foreground=TXT,
                      font=fuente, padding=(16, 8), borderwidth=0, focuscolor='#1e293b')
        est.map('Dk.TButton', background=[('active', '#334155')])
        est.configure('Horizontal.TScale', background=BG, troughcolor='#1e293b')
        est.configure('TCombobox', fieldbackground='#1e293b', background='#1e293b',
                      foreground=TXT, arrowcolor=TXT)
        est.map('TCombobox', fieldbackground=[('readonly', '#1e293b')],
                foreground=[('readonly', TXT)])

        # ---- encabezado / marcador
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill='x', padx=18, pady=(10, 2))
        tk.Label(head, text="SIMULADOR DEL PRIMER TIEMPO", bg=BG, fg=MUTED,
                 font=('Segoe UI', 10, 'bold')).pack()
        fila = tk.Frame(head, bg=BG)
        fila.pack(pady=(2, 0))
        tk.Label(fila, text=LOCAL, fg=COL_EQ[LOCAL], bg=BG,
                 font=('Segoe UI', 22, 'bold')).grid(row=0, column=0, padx=18)
        self.lbl_marcador = tk.Label(fila, text="0  -  0", fg='white', bg=PANEL,
                                     font=('Consolas', 30, 'bold'), padx=24, pady=2)
        self.lbl_marcador.grid(row=0, column=1)
        tk.Label(fila, text=VISITANTE, fg=COL_EQ[VISITANTE], bg=BG,
                 font=('Segoe UI', 22, 'bold')).grid(row=0, column=2, padx=18)
        sub = tk.Frame(head, bg=BG)
        sub.pack()
        self.lbl_reloj = tk.Label(sub, text="00:00", fg='#38bdf8', bg=BG,
                                  font=('Consolas', 16, 'bold'))
        self.lbl_reloj.pack(side='left', padx=10)
        self.lbl_estado = tk.Label(sub, text="", fg=MUTED, bg=BG, font=('Segoe UI', 10))
        self.lbl_estado.pack(side='left', padx=10)

        cuerpo = tk.Frame(self.root, bg=BG)
        cuerpo.pack(fill='both', expand=True, padx=14, pady=(4, 12))

        # ---- barra lateral
        lat = tk.Frame(cuerpo, bg=BG, width=370)
        lat.pack(side='right', fill='y', padx=(10, 0))
        lat.pack_propagate(False)

        tarjeta = tk.Frame(lat, bg=PANEL)
        tarjeta.pack(fill='x', pady=(0, 8))
        tk.Label(tarjeta, text="CON EL BALÓN", bg=PANEL, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(8, 0))
        self.lbl_balon = tk.Label(tarjeta, text="-", bg=PANEL, fg=TXT,
                                  font=('Segoe UI', 13, 'bold'))
        self.lbl_balon.pack(anchor='w', padx=12)
        tk.Label(tarjeta, text="ÚLTIMO EVENTO", bg=PANEL, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=12, pady=(6, 0))
        self.lbl_ultimo = tk.Label(tarjeta, text="-", bg=PANEL, fg=TXT,
                                   font=('Segoe UI', 13, 'bold'))
        self.lbl_ultimo.pack(anchor='w', padx=12)
        self.lbl_fase = tk.Label(tarjeta, text="", bg=PANEL, fg=MUTED, font=('Segoe UI', 9))
        self.lbl_fase.pack(anchor='w', padx=12, pady=(4, 8))

        self.st_cv = tk.Canvas(lat, height=232, bg=PANEL, highlightthickness=0)
        self.st_cv.pack(fill='x', pady=(0, 8))

        tk.Label(lat, text="HISTORIAL DE EVENTOS", bg=BG, fg=MUTED,
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        caja = tk.Frame(lat, bg=PANEL)
        caja.pack(fill='both', expand=True)
        sb = tk.Scrollbar(caja)
        sb.pack(side='right', fill='y')
        self.txt = tk.Text(caja, bg=PANEL, fg=TXT, bd=0, highlightthickness=0,
                           font=('Consolas', 10), wrap='none', state='disabled',
                           yscrollcommand=sb.set, padx=8, pady=6, cursor='arrow')
        self.txt.pack(fill='both', expand=True)
        sb.config(command=self.txt.yview)
        for cod, col in COLOR_EVENTO.items():
            self.txt.tag_configure(cod, foreground=col, font=('Consolas', 10, 'bold'))
        for eq in (LOCAL, VISITANTE):
            self.txt.tag_configure('eq_' + eq, foreground=COL_EQ[eq])
        self.txt.tag_configure('eq_-', foreground=MUTED)
        self.txt.tag_configure('min', foreground=MUTED)
        self.txt.tag_configure('desc', foreground='#9fb0cc')

        leyenda = tk.Frame(lat, bg=BG)
        leyenda.pack(fill='x', pady=(8, 0))
        for i, cod in enumerate(['GOL', 'TIR', 'COR', 'SAB', 'FAL', 'PER', 'REC', 'SAP', 'FDJ']):
            tk.Label(leyenda, text=cod, bg=COLOR_EVENTO[cod], fg='#0b1220',
                     font=('Segoe UI', 8, 'bold'), padx=6, pady=1
                     ).grid(row=i // 5, column=i % 5, padx=2, pady=2, sticky='w')
        tk.Label(leyenda, text="●", fg=NARANJA, bg=BG, font=('Segoe UI', 10, 'bold')
                 ).grid(row=1, column=4, sticky='e')
        tk.Label(leyenda, text="Balón naranja = fuera", fg=MUTED, bg=BG,
                 font=('Segoe UI', 8)).grid(row=2, column=0, columnspan=5, sticky='w', padx=2)

        # ---- zona izquierda: cancha + línea de tiempo + controles
        izq = tk.Frame(cuerpo, bg=BG)
        izq.pack(side='left', fill='both', expand=True)

        self.cv = tk.Canvas(izq, bg=BG, highlightthickness=0)
        self.cv.pack(fill='both', expand=True)
        self.cv.bind('<Configure>', self.al_redimensionar)

        self.tl = tk.Canvas(izq, height=58, bg=BG, highlightthickness=0)
        self.tl.pack(fill='x', pady=(4, 0))
        self.tl.bind('<Configure>', lambda e: self.dibujar_linea_tiempo())

        ctrl = tk.Frame(izq, bg=BG)
        ctrl.pack(fill='x', pady=(6, 0))
        self.btn_ini = ttk.Button(ctrl, text="▶  Iniciar simulación", style='Acc.TButton',
                                  command=self.iniciar)
        self.btn_ini.pack(side='left', padx=(0, 8))
        ttk.Button(ctrl, text="⏸  Pausar", style='Dk.TButton',
                   command=self.pausar).pack(side='left', padx=(0, 8))
        ttk.Button(ctrl, text="↺  Reiniciar", style='Dk.TButton',
                   command=self.reiniciar).pack(side='left', padx=(0, 18))
        tk.Label(ctrl, text="Velocidad", bg=BG, fg=MUTED,
                 font=('Segoe UI', 9)).pack(side='left')
        ttk.Scale(ctrl, from_=0.5, to=6.0, variable=self.var_vel, length=150,
                  command=self.cambiar_vel).pack(side='left', padx=6)
        self.lbl_vel = tk.Label(ctrl, text="x1.5", bg=BG, fg=TXT, width=5,
                                font=('Consolas', 10, 'bold'))
        self.lbl_vel.pack(side='left')
        cmb = ttk.Combobox(ctrl, textvariable=self.modo, values=MODOS,
                           state='readonly', width=31)
        cmb.pack(side='right')
        cmb.bind('<<ComboboxSelected>>', lambda e: (self.reiniciar(), self.root.focus_set()))
        tk.Label(ctrl, text="Modo", bg=BG, fg=MUTED, font=('Segoe UI', 9)
                 ).pack(side='right', padx=6)

        self.root.bind('<space>', lambda e: self.alternar())
        self.root.bind('<r>', lambda e: self.reiniciar())

    def cambiar_vel(self, _=None):
        self.speed = round(float(self.var_vel.get()), 1)
        self.lbl_vel.config(text=f"x{self.speed:.1f}")

    # ------------------------------------------------------------ geometría
    def al_redimensionar(self, ev):
        m = 40
        aw, ah = ev.width - 2 * m, ev.height - 2 * m
        if aw < 100 or ah < 60:
            return
        if aw / ah > ASPECTO:
            ph = ah
            pw = ph * ASPECTO
        else:
            pw = aw
            ph = pw / ASPECTO
        self.PW, self.PH = pw, ph
        self.X0 = (ev.width - pw) / 2
        self.Y0 = (ev.height - ph) / 2 + 6
        self.PR = max(8.0, pw * 0.0125)
        self.dibujar_cancha()

    def px(self, x):
        return self.X0 + x * self.PW

    def py(self, y):
        return self.Y0 + y * self.PH

    def dibujar_cancha(self):
        c = self.cv
        c.delete('static')
        x0, y0, pw, ph = self.X0, self.Y0, self.PW, self.PH
        cx, cy = x0 + pw / 2, y0 + ph / 2
        c.create_rectangle(x0 - 12, y0 - 12, x0 + pw + 12, y0 + ph + 12,
                           fill='#0f1b33', outline='#1e2d4d', tags='static')
        n = 14
        for i in range(n):
            c.create_rectangle(x0 + pw * i / n, y0, x0 + pw * (i + 1) / n, y0 + ph,
                               fill=GRASS_A if i % 2 == 0 else GRASS_B, outline='',
                               tags='static')
        L = dict(outline=LINEA, width=2, tags='static')
        c.create_rectangle(x0, y0, x0 + pw, y0 + ph, **L)
        c.create_line(cx, y0, cx, y0 + ph, fill=LINEA, width=2, tags='static')
        r = pw * 9.15 / 105
        c.create_oval(cx - r, cy - r, cx + r, cy + r, **L)
        c.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=LINEA, outline='', tags='static')
        pa_w, pa_h = pw * 16.5 / 105, ph * 40.32 / 68
        ga_w, ga_h = pw * 5.5 / 105, ph * 18.32 / 68
        gd, gh = pw * 2.4 / 105, ph * 7.32 / 68
        for lado in (0, 1):
            sg = 1 if lado == 0 else -1
            xb = x0 if lado == 0 else x0 + pw
            c.create_rectangle(xb, cy - pa_h / 2, xb + sg * pa_w, cy + pa_h / 2, **L)
            c.create_rectangle(xb, cy - ga_h / 2, xb + sg * ga_w, cy + ga_h / 2, **L)
            xs = xb + sg * pw * 11 / 105
            c.create_oval(xs - 2.5, cy - 2.5, xs + 2.5, cy + 2.5, fill=LINEA, outline='',
                          tags='static')
            c.create_arc(xs - r, cy - r, xs + r, cy + r, start=-53 if lado == 0 else 127,
                         extent=106, style='arc', outline=LINEA, width=2, tags='static')
            c.create_rectangle(xb, cy - gh / 2, xb - sg * gd, cy + gh / 2,
                               fill='#0d1526', outline='#cbd5e1', width=2, tags='static')
        c.create_text(x0 + 4, y0 - 24, text=f"{LOCAL}  ▶", anchor='w', fill=COL_EQ[LOCAL],
                      font=('Segoe UI', 12, 'bold'), tags='static')
        c.create_text(x0 + pw - 4, y0 - 24, text=f"◀  {VISITANTE}", anchor='e',
                      fill=COL_EQ[VISITANTE], font=('Segoe UI', 12, 'bold'), tags='static')
        c.tag_lower('static')

    # --------------------------------------------------------- línea de tiempo
    def dibujar_linea_tiempo(self):
        c = self.tl
        c.delete('all')
        w = c.winfo_width()
        if w < 80 or not self.eventos:
            return
        x0, x1, y = 26, w - 26, 36
        self.tl_geom = (x0, x1, y)
        c.create_line(x0, y, x1, y, fill='#22304f', width=4, capstyle='round')
        for mm in (0, 15, 30, 45):
            x = x0 + (x1 - x0) * mm / self.t_total
            c.create_text(x, y + 16, text=f"{mm}'", fill=MUTED, font=('Segoe UI', 8))
        for e in self.eventos:
            x = x0 + (x1 - x0) * e['t'] / self.t_total
            col = COLOR_EVENTO.get(e['codigo'], MUTED)
            if e['codigo'] == 'GOL':
                c.create_oval(x - 6, y - 20, x + 6, y - 8, fill=col, outline='white', width=2)
            else:
                c.create_line(x, y - 10, x, y - 3, fill=col, width=2)
        self.actualizar_linea_tiempo()

    def actualizar_linea_tiempo(self):
        if not self.tl_geom:
            return
        c = self.tl
        c.delete('tl_dyn')
        x0, x1, y = self.tl_geom
        x = x0 + (x1 - x0) * min(self.clock, self.t_total) / self.t_total
        c.create_line(x0, y, x, y, fill='#38bdf8', width=4, capstyle='round', tags='tl_dyn')
        c.create_oval(x - 6, y - 6, x + 6, y + 6, fill='white', outline='#38bdf8', width=2,
                      tags='tl_dyn')

    # --------------------------------------------------------------- datos
    def cargar_eventos(self):
        ev = []
        if self.modo.get() == MODOS[0]:
            por_min = {}
            for m, cod, eq in EVENTOS_REALES:
                por_min.setdefault(m, []).append((cod, eq))
            for m in sorted(por_min):
                grupo = por_min[m]
                for i, (cod, eq) in enumerate(grupo):
                    ev.append(dict(t=m + i / len(grupo), min=m, codigo=cod, equipo=eq))
            self.t_total = max(45.0, ev[-1]['t'] + 0.8)
        else:
            ev.append(dict(t=0.0, min=0, codigo='INI', equipo='-'))
            codigos = list(FRECUENCIAS)
            pesos = [sum(FRECUENCIAS[k]) for k in codigos]
            t = 0.0
            while True:
                t += max(0.05, random.expovariate(1 / ESCALA_EXP))
                if t > 45:
                    break
                cod = random.choices(codigos, weights=pesos)[0]
                a, b = FRECUENCIAS[cod]
                eq = (LOCAL if random.random() < (a + SUAVIZADO) / (a + b + 2 * SUAVIZADO)
                      else VISITANTE)
                ev.append(dict(t=t, min=int(t), codigo=cod, equipo=eq))
            self.t_total = 45.0
        self.eventos = ev

    def fila_var(self, m):
        ult = VARIABLES[0]
        for f in VARIABLES:
            if f[0] <= m:
                ult = f
        return ult

    def posesion_local(self, m):
        pts = VARIABLES
        if m <= pts[0][0]:
            return pts[0][1]
        for a, b in zip(pts, pts[1:]):
            if a[0] <= m <= b[0]:
                return a[1] + (b[1] - a[1]) * (m - a[0]) / (b[0] - a[0])
        return pts[-1][1]

    # ---------------------------------------------------------------- control
    def reiniciar(self):
        self.running = False
        self.finished = False
        self.cargar_eventos()
        self.clock = 0.0
        self.idx = 0
        self.gen = None
        self.amb = None
        self.dt = 0.0
        self.t_sim = 0.0
        self.score = {LOCAL: 0, VISITANTE: 0}
        self.stats = {eq: {k: 0 for k in ('Goles', 'Tiros', 'Faltas', 'Córners',
                                          'Saques de banda', 'Saques de puerta',
                                          'Fuera de juego', 'Pérdidas', 'Recuperaciones')}
                      for eq in (LOCAL, VISITANTE)}
        self.efectos = []
        self.trail = []
        self.ball = [0.5, 0.5]
        self.ball_z = 0.0
        self.ball_out = None
        for lista in self.equipos.values():
            for p in lista:
                p.pos = list(p.base)
                p.override = None
        self.holder = self.jugador(LOCAL, 9)
        self.txt.config(state='normal')
        self.txt.delete('1.0', 'end')
        self.txt.config(state='disabled')
        self.lbl_marcador.config(text="0  -  0")
        self.lbl_ultimo.config(text="-", fg=TXT)
        self.btn_ini.config(text="▶  Iniciar simulación")
        self.lbl_estado.config(
            text="Estado: listo · partido ALEATORIO nuevo" if self.modo.get() == MODOS[1]
            else "Estado: listo · reproduciendo tus datos", fg=MUTED)
        self.dibujar_linea_tiempo()

    def iniciar(self):
        if self.finished:
            self.reiniciar()
        self.running = True
        self.btn_ini.config(text="▶  Reanudar")
        self.lbl_estado.config(text="Estado: simulación en curso", fg='#34d399')

    def pausar(self):
        if self.running:
            self.running = False
            self.lbl_estado.config(text="Estado: en pausa", fg='#fbbf24')

    def alternar(self):
        self.pausar() if self.running else self.iniciar()

    def terminar(self):
        self.running = False
        self.finished = True
        self.efectos.append(dict(tipo='banner', texto='FIN DEL PRIMER TIEMPO',
                                 color='#38bdf8', age=0, dur=1, fijo=True))
        self.btn_ini.config(text="↺  Jugar de nuevo")
        self.lbl_estado.config(text="Estado: simulación terminada", fg='#38bdf8')

    # ------------------------------------------------------------ bucle
    def tick(self):
        ahora = time.perf_counter()
        dt_real = min(ahora - self.ultimo_t, 0.05)
        self.ultimo_t = ahora
        if self.running:
            self.actualizar(dt_real * self.speed)
        self.dibujar()
        self.root.after(16, self.tick)

    def actualizar(self, dt):
        self.dt = dt
        self.t_sim += dt
        adv = dt * MIN_POR_SEG
        siguiente = self.eventos[self.idx]['t'] if self.idx < len(self.eventos) else None

        # el reloj espera si hay una animación en curso y ya toca el siguiente evento
        if self.gen is not None:
            limite = siguiente if siguiente is not None else self.clock
            self.clock = min(self.clock + adv, limite)
        else:
            self.clock = min(self.clock + adv, self.t_total)

        if self.gen is None and siguiente is not None and self.clock >= siguiente:
            ev = self.eventos[self.idx]
            self.idx += 1
            self.amb = None
            self.iniciar_evento(ev)

        if self.gen is not None:
            try:
                next(self.gen)
            except StopIteration:
                self.gen = None
                self.liberar()
        elif self.amb is None:
            self.amb = self.pase_ambiente()
        if self.amb is not None and self.gen is None:
            try:
                next(self.amb)
            except StopIteration:
                self.amb = None

        self.actualizar_jugadores(dt)
        if self.holder:
            h = self.holder
            self.ball = [h.pos[0] + self.dir(h.equipo) * 0.012, h.pos[1] + 0.004]
        for t in self.trail:
            t[2] += dt
        self.trail = [t for t in self.trail if t[2] < 0.35]
        for e in self.efectos:
            e['age'] += dt
        self.efectos = [e for e in self.efectos if e.get('fijo') or e['age'] < e['dur']]

        if (self.gen is None and self.idx >= len(self.eventos)
                and self.clock >= self.t_total):
            self.terminar()

    # ------------------------------------------------------ movimiento jugadores
    def actualizar_jugadores(self, dt):
        fila = self.fila_var(self.clock)
        inten = INTENSIDAD[fila[4]]
        zona = ZONA_DESP[fila[3]]
        bx, by = self.ball
        for eq, lista in self.equipos.items():
            d = self.dir(eq)
            posee = self.holder is not None and self.holder.equipo == eq
            presiona = None if posee else self.mas_cercano(eq, self.ball)
            for p in lista:
                if p.override is not None:
                    tx, ty = p.override
                    k = 5.0
                else:
                    k = 2.2 * inten
                    b0, b1 = p.base
                    if p.rol == 'POR':
                        tx = b0
                        ty = 0.5 + (by - 0.5) * 0.22
                    else:
                        tx = (b0 + (bx - 0.5) * 0.42 + zona + (0.04 if posee else -0.03) * d
                              + 0.012 * math.sin(self.t_sim * 0.9 * inten + p.fase))
                        ty = (b1 + (by - 0.5) * 0.22
                              + 0.015 * math.cos(self.t_sim * 0.7 * inten + p.fase))
                        if p is self.holder:
                            tx += d * 0.03
                        if p is presiona:
                            tx, ty = bx - d * 0.015, by
                tx, ty = clamp(tx, 0.02, 0.98), clamp(ty, 0.03, 0.97)
                f = min(1.0, dt * k)
                p.pos[0] += (tx - p.pos[0]) * f
                p.pos[1] += (ty - p.pos[1]) * f

    def liberar(self):
        for lista in self.equipos.values():
            for p in lista:
                p.override = None
        self.ball_out = None

    # ---------------------------------------------------------------- helpers
    def dir(self, eq):
        return 1 if eq == LOCAL else -1

    def rival(self, eq):
        return VISITANTE if eq == LOCAL else LOCAL

    def x_rival(self, eq):          # x de la portería que ataca "eq"
        return 1.0 if eq == LOCAL else 0.0

    def x_propia(self, eq):
        return 0.0 if eq == LOCAL else 1.0

    def portero(self, eq):
        return self.equipos[eq][0]

    def mas_cercano(self, eq, punto, excluir=(), roles=None, sin_portero=True):
        mejor, md = None, 1e9
        for p in self.equipos[eq]:
            if p in excluir or (sin_portero and p.rol == 'POR') or (roles and p.rol not in roles):
                continue
            dd = dist(p.pos, punto)
            if dd < md:
                mejor, md = p, dd
        return mejor or self.equipos[eq][1]

    def fx(self, tipo, **kw):
        kw.setdefault('dur', 1.2)
        self.efectos.append(dict(tipo=tipo, age=0.0, **kw))

    def actualizar_marcador(self):
        self.lbl_marcador.config(text=f"{self.score[LOCAL]}  -  {self.score[VISITANTE]}")

    # ------------------------------------------------- primitivas de animación
    def esperar(self, seg):
        t = 0.0
        while t < seg:
            t += self.dt
            yield

    def esperar_llegada(self, jug, timeout=1.2, tol=0.02):
        t = 0.0
        while jug.override is not None and t < timeout and dist(jug.pos, jug.override) > tol:
            t += self.dt
            yield

    def mover_balon(self, destino, dur, arco=0.0, recibir=False):
        self.holder = None
        o = list(self.ball)
        vivo = isinstance(destino, Jugador)
        t = 0.0
        while True:
            t += self.dt
            k = min(1.0, t / dur)
            e = 1 - (1 - k) ** 2
            if vivo:
                d = (destino.pos[0] + self.dir(destino.equipo) * 0.012, destino.pos[1] + 0.004)
            else:
                d = destino
            self.ball = [o[0] + (d[0] - o[0]) * e, o[1] + (d[1] - o[1]) * e]
            self.ball_z = arco * 4 * k * (1 - k)
            self.trail.append([self.ball[0], self.ball[1], 0.0])
            if k >= 1.0:
                break
            yield
        self.ball_z = 0.0
        if recibir and vivo:
            self.holder = destino

    def dur_pase(self, a, b):
        return 0.3 + dist(a, b) * 0.8

    # --------------------------------------------------------- pases ambiente
    def pase_ambiente(self):
        """Mientras no hay evento, el equipo con balón hace pases entre jugadores."""
        while True:
            if self.holder is None:
                pA = self.posesion_local(self.clock) / 100
                eq = LOCAL if random.random() < pA else VISITANTE
                j = self.mas_cercano(eq, self.ball)
                yield from self.mover_balon(j, self.dur_pase(self.ball, j.pos), recibir=True)
            yield from self.esperar(random.uniform(0.5, 1.1))
            h = self.holder
            if h is None:
                continue
            if random.random() < 0.10:           # cambio de posesión según tu % de posesión
                pA = self.posesion_local(self.clock) / 100
                deseado = LOCAL if random.random() < pA else VISITANTE
                if deseado != h.equipo:
                    ladron = self.mas_cercano(deseado, self.ball)
                    yield from self.mover_balon(ladron, 0.4, recibir=True)
                    continue
            d = self.dir(h.equipo)
            comp = [p for p in self.equipos[h.equipo]
                    if p is not h and p.rol != 'POR' and dist(p.pos, h.pos) > 0.05]
            if not comp:
                continue
            comp.sort(key=lambda p: dist(p.pos, h.pos))
            comp = comp[:4]
            pesos = [1 + 2.5 * max(0.0, (p.pos[0] - h.pos[0]) * d) for p in comp]
            r = random.choices(comp, weights=pesos)[0]
            dd = dist(h.pos, r.pos)
            yield from self.mover_balon(r, 0.3 + dd * 0.8, arco=0.35 if dd > 0.25 else 0.0,
                                        recibir=True)

    # ------------------------------------------------------------- eventos
    def iniciar_evento(self, ev):
        cod, eq = ev['codigo'], ev['equipo']
        self.registrar(ev)
        self.ball_out = None
        self.ball_z = 0.0
        manejadores = {
            'INI': self.ev_ini, 'TIR': self.ev_tiro, 'GOL': lambda e: self.ev_tiro(e, True),
            'COR': self.ev_cor, 'SAB': self.ev_sab, 'FAL': self.ev_fal, 'PER': self.ev_per,
            'REC': self.ev_rec, 'SAP': self.ev_sap, 'FDJ': self.ev_fdj,
            'TAR-A': lambda e: self.ev_tarjeta(e, 'TAR-A'),
            'TAR-R': lambda e: self.ev_tarjeta(e, 'TAR-R'),
            'SUS': self.ev_sus, 'PEN': self.ev_pen,
        }
        self.gen = manejadores.get(cod, self.ev_sus)(eq)

    def registrar(self, ev):
        cod, eq = ev['codigo'], ev['equipo']
        t = self.txt
        t.config(state='normal')
        t.insert('end', f"{ev['min']:>2}'  ", 'min')
        t.insert('end', f"{cod:<6}", cod)
        t.insert('end', f"{eq:<10}", 'eq_' + eq)
        t.insert('end', f"{DESC.get(cod, '')}\n", 'desc')
        t.config(state='disabled')
        t.see('end')
        self.lbl_ultimo.config(text=f"{cod} · {DESC.get(cod, '')} · {eq.title() if eq != '-' else ''}",
                               fg=COLOR_EVENTO.get(cod, TXT))
        if eq in self.stats:
            mapa = {'TIR': 'Tiros', 'GOL': 'Tiros', 'FAL': 'Faltas', 'COR': 'Córners',
                    'SAB': 'Saques de banda', 'SAP': 'Saques de puerta',
                    'FDJ': 'Fuera de juego', 'PER': 'Pérdidas', 'REC': 'Recuperaciones'}
            if cod in mapa:
                self.stats[eq][mapa[cod]] += 1

    # ---- INI
    def ev_ini(self, eq):
        self.ball = [0.5, 0.5]
        kick = self.jugador(LOCAL, 9)
        kick.override = (0.5, 0.5)
        self.holder = None
        self.fx('banner', texto='¡PITAZO INICIAL!', color=COLOR_EVENTO['INI'], dur=1.8)
        yield from self.esperar_llegada(kick, 1.2, 0.015)
        self.holder = kick
        yield from self.esperar(0.9)

    # ---- TIR / GOL
    def ev_tiro(self, eq, gol=False):
        d, gx, riv = self.dir(eq), self.x_rival(eq), self.rival(eq)
        zona_ref = (gx - d * 0.22, 0.5)
        cand = []
        for p in self.equipos[eq]:
            if p.rol in ('DEL', 'MED'):
                cand.append(p)
        cand.sort(key=lambda p: dist(p.pos, zona_ref))
        tirador = random.choice(cand[:3])
        if self.holder is not tirador:
            yield from self.mover_balon(tirador, self.dur_pase(self.ball, tirador.pos),
                                        arco=0.3, recibir=True)
        zona = (gx - d * random.uniform(0.17, 0.25),
                clamp(tirador.pos[1] + random.uniform(-0.1, 0.1), 0.28, 0.72))
        tirador.override = zona
        otros = sorted([p for p in cand if p is not tirador], key=lambda p: dist(p.pos, zona))
        for p in otros[:2]:
            p.override = (gx - d * random.uniform(0.08, 0.15), random.uniform(0.28, 0.72))
        for p in self.equipos[riv]:
            if p.rol == 'DEF':
                p.override = (gx - d * random.uniform(0.05, 0.12), 0.25 + p.base[1] * 0.5)
        yield from self.esperar_llegada(tirador, 1.3, 0.03)

        gk = self.portero(riv)
        col = COLOR_EVENTO['GOL' if gol else 'TIR']
        bx, by = self.ball
        if gol:
            destino = (gx + d * 0.012, 0.5 + random.uniform(-0.045, 0.045))
            gk.override = (gk.pos[0], clamp(destino[1] + random.choice((-1, 1)) * 0.06, 0.4, 0.6))
            resultado = 'gol'
        elif random.random() < 0.6:
            destino = gk
            gk.override = (gk.pos[0], clamp(by, 0.42, 0.58))
            resultado = 'atajada'
        else:
            destino = (gx + d * 0.035, 0.5 + random.choice((-1, 1)) * random.uniform(0.07, 0.14))
            resultado = 'desviado'
        p2 = destino if not isinstance(destino, Jugador) else tuple(destino.pos)
        self.fx('disparo', p1=(bx, by), p2=p2, color=col, dur=0.8)
        self.fx('anillo', x=bx, y=by, color=col, texto='¡DISPARO!', dur=1.1)
        yield from self.mover_balon(destino, 0.42, arco=0.12, recibir=(resultado == 'atajada'))

        if resultado == 'gol':
            self.score[eq] += 1
            self.stats[eq]['Goles'] += 1
            self.actualizar_marcador()
            self.fx('banner', texto=f"¡GOOOL!  {eq}", color=col, dur=2.8)
            self.fx('anillo', x=p2[0], y=p2[1], color=col, texto=None, dur=1.6)
            esquina = (gx - d * 0.07, 0.12 if tirador.pos[1] < 0.5 else 0.88)
            tirador.override = esquina
            for p in otros[:3]:
                p.override = (esquina[0] - d * random.uniform(0.0, 0.06),
                              esquina[1] + random.uniform(-0.1, 0.1))
            yield from self.esperar(2.2)
            self.liberar()
            kick = self.equipos[riv][-1]
            kick.override = (0.5, 0.5)
            yield from self.mover_balon((0.5, 0.5), 0.8)
            yield from self.esperar_llegada(kick, 1.2, 0.02)
            self.holder = kick
        elif resultado == 'atajada':
            self.fx('anillo', x=gk.pos[0], y=gk.pos[1], color='#ffffff', texto='ATAJADA', dur=1.0)
            yield from self.esperar(0.5)
        else:
            lado = 'right' if gx == 1 else 'left'
            self.ball_out = dict(lado=lado, p=destino[1], texto='FUERA')
            self.fx('anillo', x=destino[0], y=destino[1], color=NARANJA, texto='DESVIADO', dur=1.1)
            yield from self.esperar(0.5)
            self.ball_out = None
            yield from self.mover_balon(gk, 0.6, recibir=True)

    # ---- SAB
    def ev_sab(self, eq):
        bx, by = self.ball
        lado = 'top' if by < 0.5 else 'bottom'
        if random.random() < 0.2:
            lado = 'bottom' if lado == 'top' else 'top'
        ys = 0.0 if lado == 'top' else 1.0
        x = clamp(bx + random.uniform(-0.06, 0.06), 0.07, 0.93)
        yield from self.mover_balon((x, ys + (-0.022 if ys == 0 else 0.022)), 0.45, arco=0.25)
        self.ball_out = dict(lado=lado, p=x, texto='FUERA')
        self.fx('anillo', x=x, y=ys, color=COLOR_EVENTO['SAB'],
                texto=f"SAQUE DE BANDA · {eq}", dur=1.4)
        yield from self.esperar(0.25)
        sacador = self.mas_cercano(eq, (x, ys))
        sacador.override = (x, ys)
        apoyos = sorted([p for p in self.equipos[eq] if p is not sacador and p.rol != 'POR'],
                        key=lambda p: dist(p.pos, (x, ys)))[:2]
        for p in apoyos:
            p.override = (clamp(x + random.uniform(-0.14, 0.14), 0.05, 0.95),
                          (0.12 if ys == 0 else 0.88) + random.uniform(-0.04, 0.04))
        yield from self.esperar_llegada(sacador, 0.9, 0.025)
        self.ball = [x, ys]
        self.ball_out = None
        receptor = min(apoyos, key=lambda p: dist(p.pos, (x, ys)))
        yield from self.mover_balon(receptor, 0.5, arco=0.3, recibir=True)

    # ---- COR
    def ev_cor(self, eq):
        d, gx, riv = self.dir(eq), self.x_rival(eq), self.rival(eq)
        ys = random.choice((0.0, 1.0))
        lado = 'right' if gx == 1 else 'left'
        yy = random.uniform(0.3, 0.7)
        yield from self.mover_balon((gx + d * 0.025, yy), self.dur_pase(self.ball, (gx, yy)),
                                    arco=0.3)
        self.ball_out = dict(lado=lado, p=yy, texto='FUERA')
        self.fx('anillo', x=gx, y=yy, color=COLOR_EVENTO['COR'],
                texto=f"TIRO DE ESQUINA · {eq}", dur=1.5)
        yield from self.esperar(0.3)
        cobrador = self.mas_cercano(eq, (gx, ys), roles=('MED', 'DEL'))
        cobrador.override = (gx - d * 0.012, ys + (0.012 if ys == 0 else -0.012))
        self.ball_out = dict(lado=lado, p=ys, texto='ESQUINA')
        yield from self.mover_balon((gx, ys), 0.5)
        atacantes = sorted([p for p in self.equipos[eq]
                            if p is not cobrador and p.rol in ('DEL', 'MED', 'DEF')],
                           key=lambda p: dist(p.pos, (gx - d * 0.08, 0.5)))[:4]
        for p in atacantes:
            p.override = (gx - d * random.uniform(0.04, 0.14), random.uniform(0.3, 0.7))
        for p in [q for q in self.equipos[riv] if q.rol in ('DEF', 'MED')][:5]:
            p.override = (gx - d * random.uniform(0.03, 0.12), random.uniform(0.3, 0.7))
        yield from self.esperar_llegada(cobrador, 1.0, 0.03)
        yield from self.esperar(0.45)
        self.ball_out = None
        yield from self.mover_balon(random.choice(atacantes), 0.75, arco=1.0, recibir=True)

    # ---- FAL
    def ev_fal(self, eq):
        riv = self.rival(eq)
        h = self.holder
        victima = h if (h and h.equipo == riv and h.rol != 'POR') else self.mas_cercano(riv, self.ball)
        if self.holder is not victima:
            yield from self.mover_balon(victima, self.dur_pase(self.ball, victima.pos), recibir=True)
        infractor = self.mas_cercano(eq, victima.pos, excluir=(victima,))
        infractor.override = tuple(victima.pos)
        yield from self.esperar_llegada(infractor, 0.9, 0.04)
        self.holder = None
        self.fx('anillo', x=self.ball[0], y=self.ball[1], color=COLOR_EVENTO['FAL'],
                texto=f"FALTA · {eq}", dur=1.5)
        victima.override = tuple(victima.pos)
        infractor.override = tuple(infractor.pos)
        yield from self.esperar(1.0)
        infractor.override = (clamp(infractor.pos[0] - self.dir(eq) * 0.05, 0.03, 0.97),
                              infractor.pos[1])
        victima.override = None
        yield from self.esperar(0.4)
        self.holder = victima
        yield from self.esperar(0.2)
        r = self.mas_cercano(riv, victima.pos, excluir=(victima,))
        yield from self.mover_balon(r, self.dur_pase(self.ball, r.pos), recibir=True)

    # ---- PER
    def ev_per(self, eq):
        riv = self.rival(eq)
        h = self.holder
        pos = h if (h and h.equipo == eq and h.rol != 'POR') else self.mas_cercano(eq, self.ball)
        if self.holder is not pos:
            yield from self.mover_balon(pos, self.dur_pase(self.ball, pos.pos), recibir=True)
        yield from self.esperar(0.25)
        ladron = self.mas_cercano(riv, pos.pos)
        ladron.override = tuple(pos.pos)
        self.fx('anillo', x=pos.pos[0], y=pos.pos[1], color=COLOR_EVENTO['PER'],
                texto=f"PÉRDIDA · {eq}", dur=1.3)
        yield from self.esperar_llegada(ladron, 0.6, 0.05)
        yield from self.mover_balon(ladron, 0.3, recibir=True)
        yield from self.esperar(0.2)

    # ---- REC
    def ev_rec(self, eq):
        j = self.mas_cercano(eq, self.ball)
        self.fx('anillo', x=self.ball[0], y=self.ball[1], color=COLOR_EVENTO['REC'],
                texto=f"RECUPERACIÓN · {eq}", dur=1.3)
        j.override = tuple(self.ball)
        yield from self.esperar_llegada(j, 0.5, 0.05)
        yield from self.mover_balon(j, 0.25, recibir=True)
        yield from self.esperar(0.3)

    # ---- SAP
    def ev_sap(self, eq):
        d, own = self.dir(eq), self.x_propia(eq)
        gk = self.portero(eq)
        lado = 'left' if own == 0 else 'right'
        if abs(self.ball[0] - own) > 0.12:
            yy = random.uniform(0.3, 0.7)
            yield from self.mover_balon((own - d * 0.025, yy),
                                        self.dur_pase(self.ball, (own, yy)), arco=0.25)
            self.ball_out = dict(lado=lado, p=yy, texto='FUERA')
        self.fx('anillo', x=own, y=0.5, color=COLOR_EVENTO['SAP'],
                texto=f"SAQUE DE PUERTA · {eq}", dur=1.5)
        yield from self.esperar(0.3)
        spot = (own + d * 0.065, 0.5 + random.uniform(-0.08, 0.08))
        gk.override = spot
        yield from self.mover_balon(spot, 0.4)
        self.ball_out = None
        yield from self.esperar_llegada(gk, 0.7, 0.03)
        self.holder = gk
        yield from self.esperar(0.35)
        objetivo = (0.5 + d * random.uniform(0.0, 0.15), random.uniform(0.25, 0.75))
        rec = self.mas_cercano(eq, objetivo, roles=('MED', 'DEL'))
        yield from self.mover_balon(rec, 0.9, arco=1.1, recibir=True)

    # ---- FDJ
    def ev_fdj(self, eq):
        d, gx, riv = self.dir(eq), self.x_rival(eq), self.rival(eq)
        linea = gx - d * random.uniform(0.2, 0.3)
        atac = self.mas_cercano(eq, (linea, 0.5), roles=('DEL',))
        pasador = self.mas_cercano(eq, self.ball, excluir=(atac,))
        if self.holder is not pasador:
            yield from self.mover_balon(pasador, self.dur_pase(self.ball, pasador.pos), recibir=True)
        for p in self.equipos[riv]:
            if p.rol == 'DEF':
                p.override = (linea + random.uniform(-0.006, 0.006), p.base[1])
        atac.override = (linea + d * 0.04, clamp(atac.pos[1], 0.2, 0.8))
        yield from self.esperar(0.4)
        yield from self.esperar_llegada(atac, 0.9, 0.03)
        yield from self.mover_balon(atac, 0.45, arco=0.4, recibir=True)
        self.fx('offside', x=linea, color=COLOR_EVENTO['FDJ'], texto=f"FUERA DE JUEGO · {eq}",
                dur=2.2)
        atac.override = tuple(atac.pos)
        yield from self.esperar(1.4)
        r = self.mas_cercano(riv, (linea, 0.5), roles=('DEF',))
        yield from self.mover_balon(r, 0.5, arco=0.3, recibir=True)

    # ---- extras (no aparecen en tus datos, pero quedan listos)
    def ev_tarjeta(self, eq, cod):
        j = self.mas_cercano(eq, self.ball)
        self.fx('tarjeta', x=j.pos[0], y=j.pos[1], color=COLOR_EVENTO[cod], dur=1.8)
        self.fx('anillo', x=j.pos[0], y=j.pos[1], color=COLOR_EVENTO[cod],
                texto=DESC[cod].upper() + f" · {eq}", dur=1.6)
        yield from self.esperar(1.6)

    def ev_sus(self, eq):
        self.fx('banner', texto=f"CAMBIO · {eq}", color=COLOR_EVENTO['SUS'], dur=1.6)
        yield from self.esperar(1.4)

    def ev_pen(self, eq):
        self.fx('banner', texto=f"¡PENAL PARA {eq}!", color=COLOR_EVENTO['PEN'], dur=1.6)
        yield from self.esperar(1.2)
        yield from self.ev_tiro(eq)

    # ============================================================== DIBUJO
    def etiqueta(self, x, y, texto, color, tam=9, fondo=BG):
        c = self.cv
        t = c.create_text(x, y, text=texto, fill=color, font=('Segoe UI', tam, 'bold'),
                          tags='dyn')
        bb = c.bbox(t)
        if bb:
            r = c.create_rectangle(bb[0] - 7, bb[1] - 3, bb[2] + 7, bb[3] + 3, fill=fondo,
                                   outline=color, width=1, tags='dyn')
            c.tag_lower(r, t)

    def dib_fuera(self):
        f = self.ball_out
        if not f:
            return
        c = self.cv
        x0, y0, pw, ph = self.X0, self.Y0, self.PW, self.PH
        grosor = 5 + 3 * math.sin(self.t_sim * 10)
        p = f['p']
        kw = dict(fill=NARANJA, width=grosor, capstyle='round', tags='dyn')
        if f['lado'] in ('top', 'bottom'):
            y = y0 if f['lado'] == 'top' else y0 + ph
            c.create_line(x0 + pw * clamp(p - 0.12, 0, 1), y, x0 + pw * clamp(p + 0.12, 0, 1), y, **kw)
            ty = y - 16 if f['lado'] == 'top' else y + 16
            c.create_text(x0 + pw * p, ty, text=f['texto'], fill=NARANJA,
                          font=('Segoe UI', 9, 'bold'), tags='dyn')
        else:
            x = x0 if f['lado'] == 'left' else x0 + pw
            c.create_line(x, y0 + ph * clamp(p - 0.12, 0, 1), x, y0 + ph * clamp(p + 0.12, 0, 1), **kw)
            tx = x - 34 if f['lado'] == 'left' else x + 34
            c.create_text(tx, y0 + ph * clamp(p, 0.06, 0.94), text=f['texto'], fill=NARANJA,
                          font=('Segoe UI', 9, 'bold'), tags='dyn')

    def dib_efecto(self, e):
        c = self.cv
        t = e['tipo']
        k = min(1.0, e['age'] / e['dur'])
        if t == 'anillo':
            x, y = self.px(e['x']), self.py(e['y'])
            r = self.PR * (0.8 + 2.6 * k)
            c.create_oval(x - r, y - r, x + r, y + r, outline=mezclar(e['color'], GRASS_A, k * k),
                          width=3, tags='dyn')
            if e.get('texto'):
                col = mezclar(e['color'], BG, max(0.0, (k - 0.65) / 0.35) * 0.9)
                self.etiqueta(x, y - self.PR * 2.4 - 20 * k, e['texto'], col, tam=9)
        elif t == 'disparo':
            a = (self.px(e['p1'][0]), self.py(e['p1'][1]))
            b = (self.px(e['p2'][0]), self.py(e['p2'][1]))
            c.create_line(*a, *b, fill=mezclar(e['color'], GRASS_A, k), width=4 * (1 - k) + 1,
                          dash=(8, 5), tags='dyn')
        elif t == 'offside':
            x = self.px(e['x'])
            col = mezclar(e['color'], GRASS_A, max(0.0, (k - 0.7) / 0.3))
            c.create_line(x, self.Y0, x, self.Y0 + self.PH, fill=col, width=3, dash=(10, 6),
                          tags='dyn')
            self.etiqueta(x, self.Y0 + 18, e['texto'], col, tam=9)
        elif t == 'tarjeta':
            x, y = self.px(e['x']), self.py(e['y']) - self.PR * 2.2 - 14 * k
            col = mezclar(e['color'], GRASS_A, max(0.0, (k - 0.7) / 0.3))
            c.create_rectangle(x - 7, y - 10, x + 7, y + 10, fill=col, outline='white', width=1,
                               tags='dyn')
        elif t == 'banner':
            fijo = e.get('fijo')
            s = 1.0 if fijo else min(1.0, k / 0.12)
            fade = 0.0 if fijo else max(0.0, (k - 0.8) / 0.2)
            cx, cy = self.X0 + self.PW / 2, self.Y0 + self.PH / 2
            tam = max(10, int(self.PH * 0.075 * (0.6 + 0.4 * s)))
            col = mezclar(e['color'], GRASS_A, fade)
            self.etiqueta(cx, cy, e['texto'], col, tam=tam, fondo=mezclar(BG, GRASS_A, fade))

    def dibujar(self):
        if self.PW is None:
            return
        c = self.cv
        c.delete('dyn')
        self.dib_fuera()
        for e in self.efectos:
            if e['tipo'] in ('offside', 'disparo'):
                self.dib_efecto(e)

        r = self.PR
        t = self.t_sim
        for eq, lista in self.equipos.items():
            kit = KIT[eq]
            for p in lista:
                x, y = self.px(p.pos[0]), self.py(p.pos[1])
                col = kit['gk'] if p.rol == 'POR' else kit['fill']
                c.create_oval(x - r + 2, y - r + 4, x + r + 2, y + r + 4, fill='#0a3d22',
                              outline='', tags='dyn')
                c.create_oval(x - r, y - r, x + r, y + r, fill=col, outline=kit['borde'],
                              width=2, tags='dyn')
                c.create_text(x, y, text=str(p.num), fill=kit['num'],
                              font=('Segoe UI', int(max(7, r * 0.78)), 'bold'), tags='dyn')
        h = self.holder
        if h:
            x, y = self.px(h.pos[0]), self.py(h.pos[1])
            rr = r + 5 + 2 * math.sin(t * 8)
            c.create_oval(x - rr, y - rr, x + rr, y + rr, outline='#ffffff', width=2, tags='dyn')
            self.etiqueta(x, y - r - 16, f"#{h.num} {h.nombre}", COL_EQ[h.equipo], tam=8)

        # balón
        out = self.ball_out is not None
        bx, by = self.px(self.ball[0]), self.py(self.ball[1])
        br = max(4.5, r * 0.42)
        cb = NARANJA if out else '#ffffff'
        n = len(self.trail)
        for i, (tx, ty, edad) in enumerate(self.trail):
            f = 1 - edad / 0.35
            rr = br * (0.3 + 0.6 * f)
            c.create_oval(self.px(tx) - rr, self.py(ty) - rr, self.px(tx) + rr, self.py(ty) + rr,
                          fill=mezclar(cb, GRASS_A, 1 - f * 0.7), outline='', tags='dyn')
        z = self.ball_z * self.PH * 0.14
        c.create_oval(bx - br + 2, by - br * 0.5 + 3, bx + br + 2, by + br * 0.5 + 3,
                      fill='#0a3d22', outline='', tags='dyn')
        if out:
            hr = br + 5 + 3 * math.sin(t * 10)
            c.create_oval(bx - hr, by - z - hr, bx + hr, by - z + hr, outline=NARANJA, width=2,
                          tags='dyn')
        c.create_oval(bx - br, by - z - br, bx + br, by - z + br, fill=cb, outline=BG, width=2,
                      tags='dyn')

        for e in self.efectos:
            if e['tipo'] not in ('offside', 'disparo'):
                self.dib_efecto(e)

        # paneles
        self.lbl_reloj.config(text=f"{int(self.clock):02d}:{int((self.clock % 1) * 60):02d}")
        txt_b = (f"#{h.num} · {h.nombre} · {h.equipo.title()}" if h else "balón libre")
        if txt_b != self._txt_balon:
            self._txt_balon = txt_b
            self.lbl_balon.config(text=txt_b, fg=COL_EQ[h.equipo] if h else NARANJA)
        fila = self.fila_var(self.clock)
        self.lbl_fase.config(text=f"Zona de control: {fila[3]}  ·  Intensidad: {fila[4]}")
        self.actualizar_linea_tiempo()
        self._frame += 1
        if self._frame % 10 == 0:
            self.dibujar_stats()

    def dibujar_stats(self):
        c = self.st_cv
        c.delete('all')
        w = c.winfo_width()
        if w < 50:
            w = 370
        pA = self.posesion_local(self.clock)
        a, b = self.stats[LOCAL], self.stats[VISITANTE]
        filas = [('Posesión', pA, 100 - pA, True), ('Goles', self.score[LOCAL], self.score[VISITANTE], False)]
        for k in ('Tiros', 'Faltas', 'Córners', 'Saques de banda', 'Saques de puerta',
                  'Fuera de juego', 'Pérdidas', 'Recuperaciones'):
            filas.append((k, a[k], b[k], False))
        y = 8
        for nombre, va, vb, pct in filas:
            c.create_text(w / 2, y + 6, text=nombre, fill=MUTED, font=('Segoe UI', 8, 'bold'))
            c.create_text(14, y + 6, anchor='w', fill=COL_EQ[LOCAL], font=('Consolas', 10, 'bold'),
                          text=f"{va:.0f}%" if pct else str(va))
            c.create_text(w - 14, y + 6, anchor='e', fill=COL_EQ[VISITANTE],
                          font=('Consolas', 10, 'bold'), text=f"{vb:.0f}%" if pct else str(vb))
            bw = w - 28
            by = y + 16
            tot = va + vb
            c.create_rectangle(14, by, 14 + bw, by + 5, fill='#1e2a44', outline='')
            if tot:
                fa = va / tot
                c.create_rectangle(14, by, 14 + bw * fa, by + 5, fill=COL_EQ[LOCAL], outline='')
                c.create_rectangle(14 + bw * fa, by, 14 + bw, by + 5, fill='#94a3b8', outline='')
            y += 22


if __name__ == '__main__':
    try:                                   # imagen más nítida en Windows
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    ventana = tk.Tk()
    Simulador(ventana)
    ventana.mainloop()