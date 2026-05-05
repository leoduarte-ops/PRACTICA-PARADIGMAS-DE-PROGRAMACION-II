"""
main_window.py
--------------
Ventana principal de la aplicación CFG Tree Generator.

Organiza la interfaz en tres paneles:
  ┌───────────────┬─────────────────────┬──────────────────────────────┐
  │  Panel Izq.   │   Panel Central     │       Panel Derecho          │
  │  Configuración│  Derivación paso a  │  Árbol de Derivación / AST  │
  │  y entrada    │  paso               │  (pestañas)                  │
  └───────────────┴─────────────────────┴──────────────────────────────┘
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from grammar import Grammar
from parser_engine import Parser, Derivation
from ast_builder import ASTBuilder
from tree_visualizer import TreeVisualizer


class MainWindow:
    """
    Clase principal de la interfaz gráfica.

    Orquesta:
      - Grammar    → definición de la GLC
      - Parser     → análisis sintáctico (NLTK EarleyChartParser)
      - Derivation → generación de pasos de derivación izq./der.
      - ASTBuilder → construcción del AST simplificado
      - TreeVisualizer → renderizado gráfico de los árboles
    """

    # Colores de la paleta de la aplicación
    _BG          = '#F5F5F5'
    _ACCENT      = '#2E7D57'   # Verde principal
    _BTN_GEN     = '#2E7D57'
    _BTN_CLEAR   = '#C0392B'
    _PARSE_COLOR = '#4CAF90'   # Verde-teal para parse tree
    _AST_COLOR   = '#2E6BA8'   # Azul para AST

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("CFG Tree Generator  –  ST0244 EAFIT")
        self._root.geometry("1380x720")
        self._root.resizable(True, True)
        self._root.configure(bg=self._BG)

        # ── Componentes del dominio ────────────────────────────────────
        self._grammar    = Grammar()
        self._parser     = Parser(self._grammar)
        self._deriv_mode = tk.StringVar(value='left')   # 'left' | 'right'

        # ── Construir la UI ───────────────────────────────────────────
        self._build_ui()

    # ═══════════════════════════════════════════════════════════════════ #
    #  Construcción de la interfaz                                        #
    # ═══════════════════════════════════════════════════════════════════ #

    def _build_ui(self) -> None:
        """Construye todos los widgets de la ventana."""
        root_frame = ttk.Frame(self._root, padding=6)
        root_frame.pack(fill=tk.BOTH, expand=True)

        self._build_left_panel(root_frame)
        self._build_middle_panel(root_frame)
        self._build_right_panel(root_frame)

    # ── Panel izquierdo (gramática + entrada + opciones) ─────────────

    def _build_left_panel(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text=" Configuración ", padding=8)
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        # Gramática
        ttk.Label(frame, text="Gramática (GLC – BNF):",
                  font=('Arial', 9, 'bold')).pack(anchor=tk.W)

        grammar_box = scrolledtext.ScrolledText(
            frame, height=10, width=34,
            font=('Courier New', 8),
            bg='#ECEFF1', relief=tk.FLAT,
            state='normal'
        )
        grammar_box.insert(tk.END, self._grammar.format_rules())
        grammar_box.config(state='disabled')
        grammar_box.pack(fill=tk.X, pady=(2, 10))

        # Expresión
        ttk.Label(frame, text="Expresión de entrada:",
                  font=('Arial', 9, 'bold')).pack(anchor=tk.W)

        self._expr_var = tk.StringVar(value="4 + ( a - b ) * x")
        expr_entry = ttk.Entry(frame, textvariable=self._expr_var,
                               width=34, font=('Courier New', 11))
        expr_entry.pack(fill=tk.X, pady=(2, 10))
        # Atajo de teclado: Enter ejecuta la derivación
        expr_entry.bind('<Return>', lambda _: self._on_generate())

        # Opciones de derivación
        opt_frame = ttk.LabelFrame(frame, text=" Seleccionar Derivación ", padding=6)
        opt_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(opt_frame, text="Derivación por la Izquierda",
                        variable=self._deriv_mode, value='left').pack(anchor=tk.W)
        ttk.Radiobutton(opt_frame, text="Derivación por la Derecha",
                        variable=self._deriv_mode, value='right').pack(anchor=tk.W)

        # Botón Generar
        tk.Button(
            frame, text="▶  Generar Derivación",
            command=self._on_generate,
            bg=self._BTN_GEN, fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT, cursor='hand2',
            padx=10, pady=6,
        ).pack(fill=tk.X, pady=(0, 4))

        # Botón Limpiar
        tk.Button(
            frame, text="✕  Limpiar",
            command=self._on_clear,
            bg=self._BTN_CLEAR, fg='white',
            font=('Arial', 9),
            relief=tk.FLAT, cursor='hand2',
            padx=10, pady=4,
        ).pack(fill=tk.X)

        # Nota
        ttk.Label(
            frame,
            text="Tip: usa letras minúsculas,\ndígitos 0-9 y oper. + - * / ( )",
            font=('Arial', 8), foreground='#777777'
        ).pack(anchor=tk.W, pady=(10, 0))

    # ── Panel central (pasos de derivación) ──────────────────────────

    def _build_middle_panel(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text=" Derivación Paso a Paso ", padding=8)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5), ipadx=2)
        frame.configure(width=270)

        self._deriv_box = scrolledtext.ScrolledText(
            frame, width=28, font=('Courier New', 9),
            bg='#FAFAFA', relief=tk.FLAT, state='disabled'
        )
        self._deriv_box.pack(fill=tk.BOTH, expand=True)

    # ── Panel derecho (visualizadores con pestañas) ───────────────────

    def _build_right_panel(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text=" Visualización de Árboles ", padding=5)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # ── Pestaña 1: Parse Tree ─────────────────────────────────────
        pt_frame = ttk.Frame(notebook)
        notebook.add(pt_frame, text="  Árbol de Derivación (Parse Tree)  ")

        self._parse_fig = Figure(figsize=(5.5, 5), dpi=96)
        self._parse_ax  = self._parse_fig.add_subplot(111)
        self._parse_ax.axis('off')
        parse_canvas = FigureCanvasTkAgg(self._parse_fig, master=pt_frame)
        parse_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._parse_canvas    = parse_canvas
        self._parse_visualizer = TreeVisualizer(self._parse_ax)

        # ── Pestaña 2: AST ───────────────────────────────────────────
        ast_frame = ttk.Frame(notebook)
        notebook.add(ast_frame, text="  Árbol Sintáctico Abstracto (AST)  ")

        self._ast_fig = Figure(figsize=(5.5, 5), dpi=96)
        self._ast_ax  = self._ast_fig.add_subplot(111)
        self._ast_ax.axis('off')
        ast_canvas = FigureCanvasTkAgg(self._ast_fig, master=ast_frame)
        ast_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._ast_canvas    = ast_canvas
        self._ast_visualizer = TreeVisualizer(self._ast_ax)
        self._ast_visualizer.node_color = self._AST_COLOR

    # ═══════════════════════════════════════════════════════════════════ #
    #  Manejadores de eventos                                             #
    # ═══════════════════════════════════════════════════════════════════ #

    def _on_generate(self) -> None:
        """Ejecuta el pipeline completo: tokenizar → parsear → derivar → visualizar."""
        expression = self._expr_var.get().strip()

        if not expression:
            messagebox.showwarning("Campo vacío",
                                   "Por favor ingresa una expresión aritmética.")
            return

        try:
            # ── 1. Tokenizar ───────────────────────────────────────────
            tokens = Grammar.tokenize(expression)

            # ── 2. Parsear (obtener parse tree) ────────────────────────
            self._parser = Parser(self._grammar)
            parse_tree   = self._parser.parse(tokens)

            # ── 3. Generar pasos de derivación ─────────────────────────
            derivation = Derivation(parse_tree)

            if self._deriv_mode.get() == 'left':
                steps  = derivation.left_steps()
                header = "DERIVACIÓN POR LA IZQUIERDA\n"
            else:
                steps  = derivation.right_steps()
                header = "DERIVACIÓN POR LA DERECHA\n"

            # ── 4. Mostrar pasos en el panel central ────────────────────
            self._show_derivation_steps(expression, header, steps)

            # ── 5. Dibujar parse tree ──────────────────────────────────
            self._parse_visualizer.draw(
                parse_tree,
                title="Árbol de Derivación  (Parse Tree)",
                node_color=self._PARSE_COLOR,
            )
            self._parse_canvas.draw()

            # ── 6. Construir y dibujar AST ─────────────────────────────
            ast = ASTBuilder(parse_tree).build()
            self._ast_visualizer.draw(
                ast,
                title="Árbol Sintáctico Abstracto  (AST)",
                node_color=self._AST_COLOR,
                leaf_color='#D4830A',
            )
            self._ast_canvas.draw()

        except ValueError as exc:
            messagebox.showerror("Error de análisis", str(exc))
        except Exception as exc:
            messagebox.showerror("Error inesperado",
                                 f"Ocurrió un error no esperado:\n{exc}")

    def _on_clear(self) -> None:
        """Limpia la entrada, los pasos y los gráficos."""
        self._expr_var.set("")

        self._deriv_box.config(state='normal')
        self._deriv_box.delete('1.0', tk.END)
        self._deriv_box.config(state='disabled')

        for ax, canvas in ((self._parse_ax, self._parse_canvas),
                           (self._ast_ax,   self._ast_canvas)):
            ax.clear()
            ax.axis('off')
            canvas.draw()

    # ═══════════════════════════════════════════════════════════════════ #
    #  Auxiliares                                                         #
    # ═══════════════════════════════════════════════════════════════════ #

    def _show_derivation_steps(self, expression: str,
                                header: str, steps: list[str]) -> None:
        """Escribe los pasos de derivación en el panel central."""
        self._deriv_box.config(state='normal')
        self._deriv_box.delete('1.0', tk.END)

        self._deriv_box.insert(tk.END, f"{'═'*30}\n")
        self._deriv_box.insert(tk.END, f"{header}")
        self._deriv_box.insert(tk.END, f"{'─'*30}\n")
        self._deriv_box.insert(tk.END, f"Expresión: {expression}\n")
        self._deriv_box.insert(tk.END, f"Pasos: {len(steps)}\n")
        self._deriv_box.insert(tk.END, f"{'─'*30}\n\n")

        for i, step in enumerate(steps):
            if i == 0:
                prefix = "  E  ⟹"
            else:
                prefix = "     ⟹"
            self._deriv_box.insert(tk.END, f"{prefix} {step}\n")

        self._deriv_box.insert(tk.END, f"\n{'═'*30}\n")
        self._deriv_box.config(state='disabled')
        self._deriv_box.see(tk.END)
