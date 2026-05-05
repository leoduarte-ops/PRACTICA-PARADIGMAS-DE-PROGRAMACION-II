"""
grammar.py
----------
Define la Gramática Libre de Contexto (GLC) usada por la aplicación.
Encapsula la gramática, las reglas de producción y el tokenizador de expresiones.

G = (N, Σ, P, E) donde:
  N  = {E, T, F, ID, NUM}             ← No terminales
  Σ  = {+, -, *, /, (, ), a-z, 0-9}  ← Terminales
  P  = reglas de producción BNF       ← Producciones
  E  = símbolo inicial (expresión)    ← Start symbol
"""

from nltk import CFG


class Grammar:
    """
    Clase que encapsula la Gramática Libre de Contexto (GLC) para
    expresiones aritméticas con operadores y agrupación con paréntesis.

    Jerarquía de precedencia de operadores (de menor a mayor):
      E  →  suma / resta
      T  →  multiplicación / división
      F  →  factor (paréntesis, identificador o número)
    """

    # ------------------------------------------------------------------ #
    # Definición de la gramática en formato BNF (compatible con NLTK CFG) #
    # ------------------------------------------------------------------ #
    GRAMMAR_STRING = """
        E  -> E '+' T | E '-' T | T
        T  -> T '*' F | T '/' F | F
        F  -> '(' E ')' | ID | NUM
        ID -> 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' |
              'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' |
              's' | 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z'
        NUM -> '0' | '1' | '2' | '3' | '4' | '5' |
               '6' | '7' | '8' | '9'
    """

    def __init__(self):
        """Inicializa la gramática a partir del string BNF."""
        self._cfg: CFG = CFG.fromstring(self.GRAMMAR_STRING)

    # ------------------------------------------------------------------ #
    # Propiedades públicas                                                 #
    # ------------------------------------------------------------------ #

    @property
    def cfg(self) -> CFG:
        """Retorna el objeto CFG de NLTK."""
        return self._cfg

    @property
    def start_symbol(self) -> str:
        """Retorna el símbolo inicial de la gramática."""
        return str(self._cfg.start())

    # ------------------------------------------------------------------ #
    # Métodos públicos                                                     #
    # ------------------------------------------------------------------ #

    def format_rules(self) -> str:
        """
        Retorna las reglas de producción agrupadas en formato legible.
        Ejemplo:
            E  -> E '+' T | E '-' T | T
            T  -> T '*' F | T '/' F | F
            ...
        """
        groups: dict[str, list[str]] = {}
        for prod in self._cfg.productions():
            lhs = str(prod.lhs())
            rhs = ' '.join(f"'{s}'" if isinstance(s, str) else str(s)
                           for s in prod.rhs())
            groups.setdefault(lhs, []).append(rhs)

        lines = []
        for lhs, rhs_list in groups.items():
            lines.append(f"{lhs:<3} -> {' | '.join(rhs_list)}")
        return '\n'.join(lines)

    @staticmethod
    def tokenize(expression: str) -> list[str]:
        """
        Convierte una expresión de texto en lista de terminales (tokens).

        Reglas:
          - Los espacios se ignoran.
          - Cada carácter válido (dígito, letra, operador, paréntesis)
            se convierte en un token individual.
          - Los caracteres no reconocidos lanzan ValueError.

        Parámetros:
            expression (str): Expresión aritmética como string.

        Retorna:
            list[str]: Lista de tokens terminales.
        """
        valid = set('abcdefghijklmnopqrstuvwxyz'
                    '0123456789'
                    '+-*/() ')
        tokens = []
        for ch in expression:
            if ch == ' ':
                continue
            if ch not in valid:
                raise ValueError(
                    f"Carácter no válido en la expresión: '{ch}'\n"
                    f"Caracteres permitidos: letras minúsculas, dígitos 0-9, "
                    f"operadores +  -  *  /  y paréntesis ( )"
                )
            tokens.append(ch)
        return tokens
