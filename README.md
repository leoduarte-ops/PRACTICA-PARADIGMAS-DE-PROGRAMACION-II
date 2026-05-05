# CFG Tree Generator

> Herramienta educativa para el estudio de la sintaxis en **Gramáticas Libres de Contexto (GLC)**, derivaciones y árboles sintácticos.  
> Desarrollada como práctica de la asignatura **ST0244 – Lenguajes y Paradigmas de Programación** de la **Universidad EAFIT**.

---

## 🗂️ Información del Proyecto

| Campo | Detalle |
|---|---|
| **Nombre del programa** | CFG Tree Generator |
| **Lenguaje de programación** | Python 3.11.9 |
| **IDE de desarrollo** | Google Colab / Antigravity |
| **Paradigma aplicado** | Programación Orientada a Objetos (POO) |
| **Librerías principales** | `nltk`, `matplotlib`, `tkinter` |

---

## 📋 Descripción del Programa

**CFG Tree Generator** es una aplicación de escritorio con interfaz gráfica que recibe como entrada una **gramática libre de contexto (GLC)** y una **expresión aritmética**, y produce tres salidas:

1. La **derivación paso a paso** (por izquierda o por derecha)
2. El **árbol de derivación** (*Parse Tree*) dibujado visualmente
3. El **Árbol Sintáctico Abstracto** (*AST*) simplificado

---

## 🔧 Gramática incluida (GLC)

La gramática integrada en la aplicación define expresiones aritméticas con la siguiente jerarquía de precedencia de operadores:

```
E  ->  E '+' T  |  E '-' T  |  T
T  ->  T '*' F  |  T '/' F  |  F
F  ->  '(' E ')'  |  ID  |  NUM
ID ->  'a' | 'b' | ... | 'z'
NUM->  '0' | '1' | ... | '9'
```

Donde:

- **E** (Expression) maneja sumas y restas
- **T** (Term) maneja multiplicaciones y divisiones
- **F** (Factor) maneja agrupación con paréntesis, identificadores y dígitos
- **ID** representa variables de una sola letra minúscula
- **NUM** representa dígitos del 0 al 9

Esta gramática es **libre de contexto** con recursión izquierda, lo que permite representar correctamente la asociatividad izquierda de los operadores aritméticos.

**Expresiones válidas de ejemplo:**

```
4 + ( a - b ) * x
a + b
3 * ( x + y ) - z
( a + b ) * ( c - d )
x
```

---

## 🏗️ Arquitectura del Programa (POO)

El programa está organizado en **6 módulos**, cada uno con una única responsabilidad (principio SRP):

```
cfg_tree_generator/
├── main.py              ← Punto de entrada: inicializa NLTK y lanza la ventana
├── grammar.py           ← Clase Grammar: define la GLC y el tokenizador
├── parser_engine.py     ← Clases Parser y Derivation: análisis y derivaciones
├── ast_builder.py       ← Clase ASTBuilder: construcción del AST simplificado
├── tree_visualizer.py   ← Clase TreeVisualizer: renderizado gráfico de árboles
├── main_window.py       ← Clase MainWindow: interfaz gráfica (tkinter + matplotlib)
└── requirements.txt     ← Dependencias del proyecto
```

### Descripción de cada clase

#### `Grammar` — `grammar.py`
Define la GLC en formato BNF compatible con NLTK, expone el objeto `CFG` y provee el método estático `tokenize(expression)` que convierte una cadena de texto en una lista de terminales para el parser.

#### `Parser` — `parser_engine.py`
Usa `EarleyChartParser` de NLTK para analizar la lista de tokens contra la gramática. El algoritmo de **Earley** soporta gramáticas con recursión izquierda (a diferencia del `ChartParser` estándar), lo que lo hace adecuado para la gramática de expresiones aritméticas definida. Retorna un `nltk.Tree` con el primer árbol de análisis encontrado.

#### `Derivation` — `parser_engine.py`
Reconstruye la secuencia de **formas sentenciales** a partir del árbol de análisis.

- **Derivación por Izquierda (`left_steps()`):**  
  En cada paso se localiza el **no-terminal más a la izquierda** de la forma sentencial actual y se expande usando los hijos del árbol de análisis. Esto reproduce la estrategia *leftmost derivation*, equivalente a un recorrido en pre-orden del árbol.

- **Derivación por Derecha (`right_steps()`):**  
  Igual, pero expandiendo siempre el **no-terminal más a la derecha** (*rightmost derivation*), equivalente a un recorrido en post-orden inverso.

El algoritmo interno representa la forma sentencial como una **lista mixta** de objetos `Tree` (no-terminales) y `str` (terminales). En cada iteración reemplaza el nodo `Tree` seleccionado por sus hijos directos, avanzando un paso en la derivación.

#### `ASTBuilder` — `ast_builder.py`
Transforma el *parse tree* completo en un **AST simplificado** aplicando las siguientes reglas de forma recursiva:

| Regla | Descripción |
|---|---|
| Colapso de cadenas | Si un nodo `E`, `T`, `F`, `ID` o `NUM` tiene un único hijo, se reemplaza directamente por ese hijo |
| Eliminación de paréntesis | `F → '(' E ')'` se reduce al subárbol de `E` descartando los paréntesis |
| Nodo binario con operador | `E → E op T` o `T → T op F` se convierte en `Tree(op, [izq, der])`, donde la etiqueta del nodo es el operador |

El resultado es un árbol donde los **nodos internos son operadores** y las **hojas son operandos** (letras o dígitos), eliminando toda la estructura intermedia gramatical.

#### `TreeVisualizer` — `tree_visualizer.py`
Renderiza cualquier `nltk.Tree` (o string simple) sobre un `Axes` de **matplotlib** usando:

- **Algoritmo de layout:** posiciona las hojas en coordenadas x enteras consecutivas y centra cada nodo interno sobre el promedio de las x de sus hijos. La profundidad determina el eje y.
- **Nodos internos:** círculos de color verde-teal para el *parse tree* o azul para el AST.
- **Nodos hoja (terminales):** círculos de color ámbar.
- **Aristas:** líneas grises que conectan cada nodo con sus hijos.

#### `MainWindow` — `main_window.py`
Ventana principal construida con **tkinter**. Organiza la interfaz en tres paneles:

| Panel | Contenido |
|---|---|
| **Izquierdo** | Reglas de la GLC, campo de entrada, opciones de derivación, botones |
| **Central** | Pasos de derivación numerados con el símbolo `⟹` |
| **Derecho** | Pestañas con el *Parse Tree* y el AST renderizados con matplotlib |

---

## ▶️ Cómo ejecutar

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

### 3. Usar la aplicación

1. Escribe una expresión aritmética en el campo de entrada (p. ej. `4 + ( a - b ) * x`)
2. Selecciona **Derivación por la Izquierda** o **Derivación por la Derecha**
3. Haz clic en **▶ Generar Derivación** (o presiona Enter)
4. Revisa los pasos en el panel central y los árboles en las pestañas de la derecha

---

## 📦 Dependencias

| Librería | Versión mínima | Uso |
|---|---|---|
| `nltk` | 3.8 | CFG, EarleyChartParser, estructura Tree |
| `matplotlib` | 3.7 | Renderizado visual de los árboles |
| `tkinter` | (incluida en Python) | Interfaz gráfica de la aplicación |

---

## 👥 Integrantes del Equipo

| Nombre | Rol |
|---|---|
| **Samuel José Martínez Torres** | Desarrollador |
| **José Leonardo Duarte Foronda** | Desarrollador |

---

## 📚 Información Académica

| Campo | Detalle |
|---|---|
| **Docente** | Alexánder Narváez Berrío |
| **Curso** | Lenguajes y Paradigmas de Programación |
| **Universidad** | Universidad EAFIT |
| **Periodo** | Abril 2026 |

---

## 📄 Licencia

Proyecto académico — Universidad EAFIT. Solo para fines educativos.
