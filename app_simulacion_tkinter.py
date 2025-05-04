# File: app_simulacion_bordo.py
"""
Aplicación GUI moderna en Tkinter con paleta de colores burdeos:
Interfaz para elegir distribución, parámetros, generar muestras,
visualizar histograma, tabla de frecuencias y valores (con índice).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from distributions import generar_uniforme, generar_exponencial, generar_normal

class SimulacionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulación de Distribuciones")
        self.geometry("1200x800")
        self.style = ttk.Style(self)
        self._configure_style()
        self.datos = []  # Lista de datos generados
        self._create_widgets()

    def _configure_style(self):
        self.primary_color = '#8E0D3C'
        secondary_color = '#CD1329' 
        neutral_color = '#EAE7DD'   
        text_color = '#FFFFFF'      

        self.style.theme_use('clam')

        self.style.configure('TLabel', foreground=self.primary_color, font=('Segoe UI', 10), background=neutral_color)
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), background=neutral_color, foreground='black')
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), background=secondary_color, foreground=text_color)
        self.style.configure('TMenubutton', font=('Segoe UI', 10), background=neutral_color, foreground='black')
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background=neutral_color, foreground=self.primary_color)
        self.style.configure('Treeview', font=('Segoe UI', 9))
        self.style.configure('TFrame', background=neutral_color)
        self.style.configure('TLabelframe', foreground=self.primary_color, font=('Segoe UI', 10, 'bold'), background=neutral_color)
        self.style.configure('TLabelframe.Label', foreground=self.primary_color, font=('Segoe UI', 10, 'bold'), background=neutral_color)
        

    def _create_widgets(self):
        # Marco principal con layout de grid
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)

        # Marco de parámetros (superior)
        param_frame = ttk.LabelFrame(main_frame, text="Parámetros de Simulación", padding=10)
        param_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        param_frame.columnconfigure(0, weight=0)
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(2, weight=0)
        param_frame.columnconfigure(3, weight=1)

        # Selección de distribución
        ttk.Label(param_frame, text="Distribución:", font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dist_var = tk.StringVar(value="Uniforme")
        dist_menu = ttk.OptionMenu(
            param_frame, self.dist_var, "Uniforme",
            "Uniforme", "Exponencial", "Normal",
            command=self._update_params,
            style='TMenubutton'
        )
        dist_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Parámetros específicos (dinámicos)
        self.params_frame = ttk.Frame(param_frame)
        self.params_frame.grid(row=0, column=2, columnspan=2, padx=10, pady=5, sticky="ew")
        self._update_params(self.dist_var.get()) # Inicializa los parámetros

        # Tamaño de muestra
        ttk.Label(param_frame, text="Tamaño muestra:", font=('Segoe UI', 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.n_entry = ttk.Entry(param_frame, width=15, font=('Segoe UI', 10))
        self.n_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Número de intervalos (bins)
        ttk.Label(param_frame, text="Intervalos:", font=('Segoe UI', 10)).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.bins_var = tk.IntVar(value=10)
        bins_menu = ttk.OptionMenu(param_frame, self.bins_var, 10, 10, 15, 20, 25, style='TMenubutton')
        bins_menu.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Botones principales
        button_frame = ttk.Frame(param_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")
        ttk.Button(button_frame, text="Generar", command=self._generar, style='Accent.TButton').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="Limpiar", command=self._limpiar, style='TButton').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Marco de contenido principal (inferior)
        content_container = ttk.Panedwindow(main_frame, orient=tk.HORIZONTAL)
        content_container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Marco para el gráfico
        graph_frame = ttk.Frame(content_container, padding=5)
        content_container.add(graph_frame, weight=1)
        fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Marco para la información (tabla y lista)
        info_frame = ttk.Frame(content_container, padding=5)
        content_container.add(info_frame, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)

        # Tabla de frecuencias
        freq_frame = ttk.LabelFrame(info_frame, text="Tabla de Frecuencias", padding=5)
        freq_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.table = ttk.Treeview(
            freq_frame,
            columns=("Intervalo", "Frecuencia"),
            show="headings",
            height=10,
            style='Treeview'
        )
        self.table.heading("Intervalo", text="Intervalo", anchor=tk.CENTER)
        self.table.heading("Frecuencia", text="Frecuencia", anchor=tk.CENTER)
        self.table.column("Intervalo", stretch=tk.YES, anchor=tk.CENTER)
        self.table.column("Frecuencia", stretch=tk.NO, width=100, anchor=tk.CENTER)
        self.table.pack(fill=tk.BOTH, expand=True)

        # Lista de valores generados
        var_frame = ttk.LabelFrame(info_frame, text="Valores Generados", padding=5)
        var_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.var_scrollbar = ttk.Scrollbar(var_frame)
        self.var_listbox = tk.Listbox(var_frame, yscrollcommand=self.var_scrollbar.set, font=('Consolas', 9), foreground=self.primary_color)
        self.var_scrollbar.config(command=self.var_listbox.yview)
        self.var_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.var_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _update_params(self, distribucion):
        """Actualiza los campos de entrada según la distribución seleccionada."""
        for w in self.params_frame.winfo_children():
            w.destroy()
        if distribucion == "Uniforme":
            ttk.Label(self.params_frame, text="a:", font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.a_entry = ttk.Entry(self.params_frame, width=10, font=('Segoe UI', 10))
            self.a_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            ttk.Label(self.params_frame, text="b:", font=('Segoe UI', 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.b_entry = ttk.Entry(self.params_frame, width=10, font=('Segoe UI', 10))
            self.b_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        elif distribucion == "Exponencial":
            ttk.Label(self.params_frame, text="λ:", font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.lam_entry = ttk.Entry(self.params_frame, width=10, font=('Segoe UI', 10))
            self.lam_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        else: # Normal
            ttk.Label(self.params_frame, text="μ:", font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.mu_entry = ttk.Entry(self.params_frame, width=10, font=('Segoe UI', 10))
            self.mu_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            ttk.Label(self.params_frame, text="σ:", font=('Segoe UI', 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.sigma_entry = ttk.Entry(self.params_frame, width=10, font=('Segoe UI', 10))
            self.sigma_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def _generar(self):
        """Genera la muestra según parámetros y actualiza componentes."""
        try:
            n = int(self.n_entry.get())
        except ValueError:
            return messagebox.showerror("Error", "Tamaño de muestra inválido")
        if not (1 <= n <= 1000000):
            return messagebox.showerror("Error", "La muestra debe ser entre 1 y 1,000,000")

        dist = self.dist_var.get()
        try:
            if dist == "Uniforme":
                a, b = float(self.a_entry.get()), float(self.b_entry.get())
                self.datos = generar_uniforme(n, a, b)
            elif dist == "Exponencial":
                lam = float(self.lam_entry.get())
                self.datos = generar_exponencial(n, lam)
            else: # Normal
                mu, sigma = float(self.mu_entry.get()), float(self.sigma_entry.get())
                self.datos = generar_normal(n, mu, sigma)
        except ValueError:
            return messagebox.showerror("Error", "Parámetros inválidos")

        self._actualizar_histograma()
        self._actualizar_tabla()
        self._mostrar_valores()

    def _actualizar_histograma(self):
        """Dibuja el histograma con intervalos, barras y anotaciones más estéticas."""
        self.ax.clear()
        k = self.bins_var.get()
        counts, bins = np.histogram(self.datos, bins=k)
        width = (bins[1] - bins[0]) * 0.9
        # Añadir grid para mejorar estética
        self.ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7, color=self.style.lookup('TLabel', 'foreground'))
        bars = self.ax.bar(bins[:-1], counts, width=width, align='edge', edgecolor='black', alpha=0.7, color=self.style.lookup('Accent.TButton', 'background'))
        # Añadir etiquetas a las barras
        for bar in bars:
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, yval + max(counts)*0.01, round(yval), ha='center', va='bottom', fontsize=8, color='black')
        # Mejorar fuentes y márgenes
        self.ax.set_title(f"Histograma - {self.dist_var.get()}", fontsize=14, pad=12, fontweight='bold', color=self.style.lookup('TLabel', 'foreground'))
        self.ax.set_xlabel("Intervalos", fontsize=12, labelpad=10, color=self.style.lookup('TLabel', 'foreground'))
        self.ax.set_ylabel("Frecuencia", fontsize=12, labelpad=10, color=self.style.lookup('TLabel', 'foreground'))
        self.ax.tick_params(axis='both', which='major', labelsize=10, color=self.style.lookup('TLabel', 'foreground'), labelcolor=self.style.lookup('TLabel', 'foreground'))
        self.ax.set_xlim(bins[0], bins[-1])

        # *** Agregar estas líneas para mostrar cada límite de intervalo ***
        self.ax.set_xticks(bins)
        self.ax.set_xticklabels([f"{round(b, 4)}" for b in bins], rotation=45, fontsize=8, ha='right')
        self.ax.tick_params(axis='x', which='major', pad=7) # Ajustar el padding si es necesario

        self.canvas.draw()

    def _actualizar_tabla(self):
        """Llena la tabla de frecuencias con intervalos y conteos."""
        for r in self.table.get_children():
            self.table.delete(r)
        counts, bins = np.histogram(self.datos, bins=self.bins_var.get())
        for i in range(len(counts)):
            intervalo = f"[{round(bins[i], 4)}, {round(bins[i+1], 4)})"
            self.table.insert("", 'end', values=(intervalo, int(counts[i])))

    def _mostrar_valores(self):
        """Muestra directamente los valores generados en el Listbox con índice."""
        self.var_listbox.delete(0, tk.END)
        for idx, val in enumerate(self.datos, start=1):
            self.var_listbox.insert(tk.END, f"{idx}: {val:.4f}") # Formatear a 4 decimales

    def _limpiar(self):
        """Limpia todos los campos, gráfico, tabla y valores."""
        # Limpia entradas de parámetros
        self.n_entry.delete(0, tk.END)
        for widget in self.params_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
        # Limpia gráfico
        self.ax.clear()
        self.canvas.draw()
        # Limpia tabla
        for r in self.table.get_children():
            self.table.delete(r)
        # Limpia lista de valores
        self.var_listbox.delete(0, tk.END)
        # Resetea datos

if __name__ == "__main__":
    app = SimulacionApp()
    app.mainloop()
