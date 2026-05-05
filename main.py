"""
main.py
-------
Punto de entrada de la aplicación CFG Tree Generator.

Verifica los datos requeridos de NLTK y lanza la ventana principal.

Uso:
    python main.py
"""

import sys
import nltk


def _check_nltk_data() -> None:
    """
    Descarga los recursos de NLTK necesarios si no están disponibles.
    Se utiliza: punkt (tokenizador básico, requerido internamente por NLTK).
    """
    resources = [
        ('tokenizers/punkt',    'punkt'),
        ('tokenizers/punkt_tab','punkt_tab'),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"[INFO] Descargando recurso NLTK: '{name}' …")
            nltk.download(name, quiet=True)


def main() -> None:
    """Inicializa dependencias y lanza la ventana principal."""
    _check_nltk_data()

    # Importar tkinter aquí para que el error sea claro si no está disponible
    try:
        import tkinter as tk
    except ImportError:
        print(
            "ERROR: tkinter no está instalado.\n"
            "En Ubuntu/Debian:  sudo apt-get install python3-tk\n"
            "En macOS/Windows:  normalmente viene incluido con Python."
        )
        sys.exit(1)

    from main_window import MainWindow

    root = tk.Tk()
    app  = MainWindow(root)      # noqa: F841  (referencia viva durante mainloop)
    root.mainloop()


if __name__ == '__main__':
    main()
