"""
parser_engine.py
----------------
Motor de análisis y generación de derivaciones.

Clases:
    Parser       – analiza una lista de tokens con la GLC usando EarleyChartParser.
    Derivation   – reconstruye los pasos de derivación izquierda o derecha
                   a partir del árbol de análisis (parse tree) entregado por Parser.
"""

from nltk import Tree
from nltk.parse import EarleyChartParser

from grammar import Grammar


# ═══════════════════════════════════════════════════════════════════════ #
#  Parser                                                                 #
# ═══════════════════════════════════════════════════════════════════════ #

class Parser:
    """
    Analiza una secuencia de tokens usando la GLC y el algoritmo de Earley
    (EarleyChartParser de NLTK), que soporta gramáticas con recursión izquierda.

    El resultado es un árbol de análisis sintáctico (NLTK Tree) que representa
    la primera derivación válida encontrada.
    """

    def __init__(self, grammar: Grammar) -> None:
        """
        Parámetros:
            grammar (Grammar): instancia de la gramática a utilizar.
        """
        self._grammar = grammar
        self._earley = EarleyChartParser(grammar.cfg, trace=0)
        self._parse_tree: Tree | None = None

    # ------------------------------------------------------------------ #
    # Interfaz pública                                                     #
    # ------------------------------------------------------------------ #

    def parse(self, tokens: list[str]) -> Tree:
        """
        Parsea la lista de tokens y almacena el primer árbol resultante.

        Parámetros:
            tokens (list[str]): tokens terminales de la expresión.

        Retorna:
            Tree: árbol de análisis sintáctico (parse tree) de NLTK.

        Lanza:
            ValueError: si la expresión no es válida para la gramática.
        """
        if not tokens:
            raise ValueError("La expresión no puede estar vacía.")

        results = list(self._earley.parse(tokens))

        if not results:
            raise ValueError(
                "La expresión ingresada no puede derivarse con la gramática.\n\n"
                "Comprueba que uses solo letras minúsculas, dígitos (0-9) y\n"
                "los operadores:  +  -  *  /  con paréntesis ( ) correctos."
            )

        self._parse_tree = results[0]
        return self._parse_tree

    @property
    def parse_tree(self) -> Tree | None:
        """Árbol de análisis del último parseo realizado (o None si no hubo)."""
        return self._parse_tree


# ═══════════════════════════════════════════════════════════════════════ #
#  Derivation                                                             #
# ═══════════════════════════════════════════════════════════════════════ #

class Derivation:
    """
    Genera los pasos de derivación a partir de un árbol de análisis sintáctico.

    Derivación por Izquierda (leftmost):
        En cada paso se expande el no-terminal más a la izquierda de la
        forma sentencial actual.

    Derivación por Derecha (rightmost):
        En cada paso se expande el no-terminal más a la derecha.

    Algoritmo:
        Se parte de la forma sentencial [raíz] (un único nodo Tree) y,
        en cada iteración, se reemplaza el nodo Tree encontrado (izquierda
        o derecha) por sus hijos directos dentro del árbol de análisis,
        reproduciendo así el orden de expansión de la gramática.
    """

    def __init__(self, parse_tree: Tree) -> None:
        """
        Parámetros:
            parse_tree (Tree): árbol de análisis obtenido por Parser.parse().
        """
        if parse_tree is None:
            raise ValueError("Se requiere un árbol de análisis válido.")
        self._tree = parse_tree

    # ------------------------------------------------------------------ #
    # Interfaz pública                                                     #
    # ------------------------------------------------------------------ #

    def left_steps(self) -> list[str]:
        """
        Retorna la lista de formas sentenciales de la derivación por izquierda.
        Cada elemento es un string con los símbolos separados por espacios.
        """
        return self._generate(leftmost=True)

    def right_steps(self) -> list[str]:
        """
        Retorna la lista de formas sentenciales de la derivación por derecha.
        Cada elemento es un string con los símbolos separados por espacios.
        """
        return self._generate(leftmost=False)

    # ------------------------------------------------------------------ #
    # Lógica interna                                                       #
    # ------------------------------------------------------------------ #

    def _generate(self, leftmost: bool) -> list[str]:
        """
        Genera la secuencia de formas sentenciales.

        La forma sentencial se representa como una lista que puede contener:
          - Objetos Tree (no-terminales pendientes de expandir)
          - Strings        (terminales ya fijos)

        En cada paso se ubica el nodo Tree según la dirección elegida y se
        sustituye por sus hijos, avanzando un paso en la derivación.
        """
        # Forma sentencial inicial: solo el símbolo de inicio
        sentential: list = [self._tree]
        steps: list[str] = [self._to_str(sentential)]

        while True:
            idx = self._find_nonterminal(sentential, leftmost)
            if idx == -1:
                break   # No quedan no-terminales → derivación completa
            node: Tree = sentential[idx]
            # Expandir: sustituir el nodo por sus hijos directos
            children = list(node)
            sentential = sentential[:idx] + children + sentential[idx + 1:]
            steps.append(self._to_str(sentential))

        return steps

    @staticmethod
    def _find_nonterminal(sentential: list, leftmost: bool) -> int:
        """
        Busca el índice del primer (leftmost=True) o último (leftmost=False)
        nodo Tree dentro de la forma sentencial.

        Retorna -1 si no hay no-terminales (todos son terminales).
        """
        indices = range(len(sentential))
        if not leftmost:
            indices = reversed(indices)   # type: ignore[arg-type]

        for i in indices:
            if isinstance(sentential[i], Tree):
                return i
        return -1

    @staticmethod
    def _to_str(sentential: list) -> str:
        """Convierte la forma sentencial en una cadena de texto legible."""
        parts = []
        for node in sentential:
            if isinstance(node, Tree):
                parts.append(node.label())   # No-terminal: mostrar etiqueta
            else:
                parts.append(str(node))      # Terminal: mostrar valor
        return ' '.join(parts)
