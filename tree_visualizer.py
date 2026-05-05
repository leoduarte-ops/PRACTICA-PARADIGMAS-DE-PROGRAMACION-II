"""
tree_visualizer.py
------------------
Renderiza árboles (parse tree y AST) sobre un Axes de matplotlib.

Clase:
    TreeVisualizer – calcula posiciones de nodos con un algoritmo de
                     layout centrado-en-hijos y dibuja nodos/aristas.
"""

import matplotlib.pyplot as plt
from nltk import Tree


class TreeVisualizer:
    """
    Dibuja cualquier árbol (nltk.Tree o string simple) sobre un objeto
    matplotlib.Axes mediante círculos coloreados y líneas de conexión.

    Algoritmo de layout:
      - Las hojas se colocan en posiciones x enteras consecutivas (0, 1, 2 …).
      - Cada nodo interno se centra sobre el promedio de las x de sus hijos.
      - La profundidad controla el eje y (y = -profundidad).

    Esto produce un árbol balanceado y fácil de leer.
    """

    # Paleta por defecto
    _DEFAULT_NODE_COLOR = '#4CAF90'    # Verde-teal  → parse tree
    _DEFAULT_LEAF_COLOR = '#E8A020'    # Ámbar       → terminales
    _EDGE_COLOR         = '#444444'

    def __init__(self, ax) -> None:
        """
        Parámetros:
            ax: matplotlib.axes.Axes donde se renderizará el árbol.
        """
        self._ax = ax
        self.node_color: str = self._DEFAULT_NODE_COLOR
        self.leaf_color: str = self._DEFAULT_LEAF_COLOR

    # ------------------------------------------------------------------ #
    # Interfaz pública                                                     #
    # ------------------------------------------------------------------ #

    def draw(self, tree, title: str = "",
             node_color: str | None = None,
             leaf_color: str | None = None) -> None:
        """
        Dibuja el árbol en el Axes asociado.

        Parámetros:
            tree       : nltk.Tree o string (expresión de un solo token).
            title      : título que aparece sobre la visualización.
            node_color : color de nodos internos (hex o nombre CSS).
            leaf_color : color de nodos hoja (terminales).
        """
        self._ax.clear()
        self._ax.axis('off')
        self._ax.set_title(title, fontsize=10, fontweight='bold', pad=8)

        if node_color:
            self.node_color = node_color
        if leaf_color:
            self.leaf_color = leaf_color

        # Si el AST es solo un string (expresión de un token), envolverlo
        if isinstance(tree, str):
            tree = Tree(tree, [])

        if tree is None:
            return

        # Paso 1 – Construir lista plana de nodos con IDs únicos
        self._nodes: list[dict] = []
        self._id_map: dict[int, dict] = {}
        self._counter: int = 0
        self._build_nodes(tree, parent_id=None)

        if not self._nodes:
            return

        # Paso 2 – Calcular posiciones (x, y) para cada nodo
        self._compute_positions()

        # Paso 3 – Renderizar aristas y luego nodos
        self._draw_edges()
        self._draw_nodes()

        # Paso 4 – Ajustar los límites de la vista
        self._fit_view()

    # ------------------------------------------------------------------ #
    # Construcción de la lista plana de nodos                              #
    # ------------------------------------------------------------------ #

    def _new_id(self) -> int:
        uid = self._counter
        self._counter += 1
        return uid

    def _build_nodes(self, node, parent_id: int | None) -> int:
        """
        Recorre el árbol en pre-orden y construye una lista plana de dicts.
        Cada dict contiene: id, label, parent_id, is_leaf, child_ids, x, y.
        """
        uid = self._new_id()
        is_leaf = (not isinstance(node, Tree)) or (len(list(node)) == 0)
        label = str(node) if not isinstance(node, Tree) else node.label()

        entry = {
            'id'        : uid,
            'label'     : label,
            'parent_id' : parent_id,
            'is_leaf'   : is_leaf,
            'child_ids' : [],
            'x'         : 0.0,
            'y'         : 0.0,
        }
        self._nodes.append(entry)
        self._id_map[uid] = entry

        if parent_id is not None:
            self._id_map[parent_id]['child_ids'].append(uid)

        if isinstance(node, Tree):
            for child in node:
                self._build_nodes(child, uid)

        return uid

    # ------------------------------------------------------------------ #
    # Cálculo de posiciones                                                #
    # ------------------------------------------------------------------ #

    def _compute_positions(self) -> None:
        """
        Asigna coordenadas (x, y) a cada nodo:
          - x: posición horizontal (centrada sobre hijos o consecutiva para hojas)
          - y: profundidad negativa (-depth)
        """
        root_id: int = self._nodes[0]['id']
        leaf_cursor = [0]

        def assign_x(uid: int) -> float:
            node = self._id_map[uid]
            if not node['child_ids']:          # hoja
                node['x'] = float(leaf_cursor[0])
                leaf_cursor[0] += 1
                return node['x']
            child_xs = [assign_x(cid) for cid in node['child_ids']]
            node['x'] = sum(child_xs) / len(child_xs)
            return node['x']

        def assign_y(uid: int, depth: int = 0) -> None:
            node = self._id_map[uid]
            node['y'] = float(-depth)
            for cid in node['child_ids']:
                assign_y(cid, depth + 1)

        assign_x(root_id)
        assign_y(root_id)

    # ------------------------------------------------------------------ #
    # Renderizado                                                          #
    # ------------------------------------------------------------------ #

    def _draw_edges(self) -> None:
        """Dibuja las aristas entre cada nodo y su padre."""
        for node in self._nodes:
            if node['parent_id'] is not None:
                parent = self._id_map[node['parent_id']]
                self._ax.plot(
                    [parent['x'], node['x']],
                    [parent['y'], node['y']],
                    color=self._EDGE_COLOR,
                    linewidth=1.3,
                    zorder=1,
                )

    def _draw_nodes(self) -> None:
        """Dibuja cada nodo como un círculo con su etiqueta centrada."""
        radius = 0.32
        for node in self._nodes:
            x, y = node['x'], node['y']
            color = self.leaf_color if node['is_leaf'] else self.node_color

            circle = plt.Circle((x, y), radius, color=color, zorder=2)
            self._ax.add_patch(circle)

            label = node['label']
            fontsize = 7 if len(label) > 2 else 9
            self._ax.text(
                x, y, label,
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold',
                color='white', zorder=3,
            )

    def _fit_view(self) -> None:
        """Ajusta xlim e ylim para que el árbol quede bien centrado."""
        xs = [n['x'] for n in self._nodes]
        ys = [n['y'] for n in self._nodes]

        margin_x = max(0.8, (max(xs) - min(xs)) * 0.08) + 0.8
        margin_y = 0.7

        self._ax.set_xlim(min(xs) - margin_x, max(xs) + margin_x)
        self._ax.set_ylim(min(ys) - margin_y, max(ys) + margin_y)
        self._ax.set_aspect('equal', adjustable='box')
