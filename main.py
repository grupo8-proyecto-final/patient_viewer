import sys
import tkinter as tk
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Importar la aplicación principal
from ui.app import PatientViewer

def main():
    # Configurar la aplicación
    root = tk.Tk()
    app = PatientViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()