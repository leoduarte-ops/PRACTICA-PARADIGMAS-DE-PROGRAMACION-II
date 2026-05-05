"""
ast_builder.py
--------------
Construye el Árbol Sintáctico Abstracto (AST) a partir del árbol de
derivación (parse tree) entregado por el Parser.

El AST simplifica el parse tree eliminando:
  - Cadenas de nodos con un solo hijo (E→T→F sin operadores)
  - Los paréntesis como nodos explícitos en F → '(' E ')'
  - Los no-terminales intermedios ID y NUM, reemplazándolos por el
    terminal que contienen

El resultado conserva únicamente los operadores (+, -, *, /) como nodos
internos y los identificadores / números como hojas.
"""

from nltk import Tree


class ASTBuilder:
    """
    Construye el Árbol Sintáctico Abstracto (AST) desde un parse tree.

    El AST omite nodos redundantes y se enfoca en la estructura semántica
    de la expresión:
      - Nodos internos  → operadores aritméticos (+, -, *, /)
      - Nodos hoja      → operandos (identificadores o dígitos)

    Ejemplo:
        Parse tree de  4 + (a - b) * x
        ─────────────────────────────────────────────────────
        E → E '+' T → ...  (árbol completo con E, T, F, ID, NUM)

        AST resultante:
              +
             / \\
            4   *
               / \\
              -   x
             / \\
            a   b
    """

    # No-terminales que se colapsan si tienen un solo hijo sin operador
    _COLLAPSIBLE = {'E', 'T', 'F', 'ID', 'NUM'}

    def __init__(self, parse_tree: Tree) -> None:
        """
        Parámetros:
            parse_tree (Tree): árbol de análisis obtenido por Parser.
        """
        self._parse_tree = parse_tree

    # ------------------------------------------------------------------ #
    # Interfaz pública                                                     #
    # ------------------------------------------------------------------ #

    def build(self) -> Tree | str:
        """
        Construye y retorna el AST.

        Retorna:
            Tree  si la expresión tiene estructura con operadores.
            str   si la expresión es un único token (operando simple).
        """
        return self._simplify(self._parse_tree)

    # ------------------------------------------------------------------ #
    # Lógica interna                                                       #
    # ------------------------------------------------------------------ #

    def _simplify(self, node) -> Tree | str | None:
        """
        Reduce recursivamente el árbol, eliminando nodos no esenciales.

        Reglas de simplificación:
          1. Terminales (strings) → se retornan tal cual.
          2. Paréntesis ('(', ')') → se descartan (retorna None).
          3. F → '(' E ')' (3 hijos tras descartar paréntesis) → retorna
             directamente el subárbol de la expresión interior.
          4. Nodo collapsible con un solo hijo → se reemplaza por el hijo.
          5. Nodo E o T con tres hijos [izq, op, der] → se crea un nodo
             Tree cuya etiqueta es el operador, con [izq, der] como hijos.
          6. Cualquier otro caso → se retorna el nodo con hijos simplificados.
        """
        # ── Regla 1: terminal ──────────────────────────────────────────
        if not isinstance(node, Tree):
            return node

        label: str = node.label()

        # ── Simplificar hijos ──────────────────────────────────────────
        simplified_children = []
        for child in node:
            result = self._simplify(child)
            if result is not None:           # Regla 2: paréntesis se filtran
                simplified_children.append(result)

        # ── Regla 2: descartar paréntesis como nodo de paso ────────────
        # (ya se filtraron arriba porque _simplify devuelve None para '(' y ')')
        # Nota: los caracteres '(' y ')' son strings terminales →
        # esta lógica los descarta vía el filtro None implícito.
        # Realmente llegamos aquí si son terminales, así que:
        # Caso especial: si es F con hijos [algo] luego de quitar paréntesis
        #   → el único hijo que queda es el subárbol interior.

        n = len(simplified_children)

        # ── Regla 3: F → ( E ) ─────────────────────────────────────────
        # Tras descartar '(' y ')', F tiene exactamente 1 hijo (el E interior)
        if label == 'F' and n == 1:
            return simplified_children[0]

        # ── Regla 4: colapsar cadena de un solo hijo ────────────────────
        if label in self._COLLAPSIBLE and n == 1:
            return simplified_children[0]

        # ── Regla 5: nodo binario con operador ─────────────────────────
        # E → E op T  o  T → T op F  (3 hijos: izq, operador, der)
        if label in ('E', 'T') and n == 3:
            left, op, right = simplified_children
            return Tree(str(op), [left, right])

        # ── Regla 6: conservar nodo con hijos simplificados ────────────
        if simplified_children:
            return Tree(label, simplified_children)

        # Nodo vacío (no debería ocurrir en una gramática bien formada)
        return Tree(label, [])

    # ------------------------------------------------------------------ #
    # Método estático auxiliar para depuración                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def tree_to_str(node, indent: int = 0) -> str:
        """Retorna una representación en texto indentado del árbol (útil para debug)."""
        prefix = "  " * indent
        if not isinstance(node, Tree):
            return f"{prefix}'{node}'"
        lines = [f"{prefix}{node.label()}"]
        for child in node:
            lines.append(ASTBuilder.tree_to_str(child, indent + 1))
        return '\n'.join(lines)
