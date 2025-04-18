import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple


def setup_eye_tab(tab: ttk.Frame, eye_side: str) -> Tuple[
    ttk.Label, ttk.Label, Dict[str, ttk.Label], Dict[str, ttk.Label]]:
    """
    Configura la pestaña de información de un ojo.

    Args:
        tab: Frame de la pestaña
        eye_side: Lado del ojo ('right' o 'left')

    Returns:
        Tupla con etiqueta de diagnóstico, etiqueta de cristalino, diccionario de etiquetas refractivas
        y diccionario de etiquetas de medición
    """
    eye_frame = ttk.LabelFrame(tab, text=f"Datos del Ojo {'Derecho' if eye_side == 'right' else 'Izquierdo'}",
                               padding="10")
    eye_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Sección de diagnóstico
    diag_frame = ttk.Frame(eye_frame)
    diag_frame.pack(fill=tk.X, pady=5)

    ttk.Label(diag_frame, text="Diagnóstico:").pack(side=tk.LEFT, padx=5)
    diagnosis_label = ttk.Label(diag_frame, text="")
    diagnosis_label.pack(side=tk.LEFT, padx=5)

    ttk.Label(diag_frame, text="Estado del Cristalino:").pack(side=tk.LEFT, padx=5)
    crystalline_label = ttk.Label(diag_frame, text="")
    crystalline_label.pack(side=tk.LEFT, padx=5)

    # Sección de error refractivo
    ref_frame = ttk.LabelFrame(eye_frame, text="Error Refractivo", padding="5")
    ref_frame.pack(fill=tk.X, pady=5)

    ref_labels = {}
    ref_fields = ["Esfera", "Cilindro", "Eje"]
    for i, field in enumerate(ref_fields):
        ttk.Label(ref_frame, text=f"{field}:").grid(row=0, column=i * 2, padx=5, sticky=tk.E)
        value_label = ttk.Label(ref_frame, text="")
        value_label.grid(row=0, column=i * 2 + 1, padx=5, sticky=tk.W)
        ref_labels[field.lower()] = value_label

    # Sección de mediciones
    meas_frame = ttk.LabelFrame(eye_frame, text="Mediciones", padding="5")
    meas_frame.pack(fill=tk.X, pady=5)

    meas_labels = {}
    meas_fields = [
        ("IOP Neumático", "pneumatic_iop"),
        ("IOP Perkins", "perkins_iop"),
        ("Paquimetría", "pachymetry"),
        ("Longitud Axial", "axial_length"),
        ("Defecto Medio", "mean_defect"),
        ("Severidad Glaucoma", "severity")
    ]

    for i, (label_text, field) in enumerate(meas_fields):
        row = i // 2
        col = (i % 2) * 2

        ttk.Label(meas_frame, text=f"{label_text}:").grid(row=row, column=col, padx=5, pady=2, sticky=tk.E)
        value_label = ttk.Label(meas_frame, text="")
        value_label.grid(row=row, column=col + 1, padx=5, pady=2, sticky=tk.W)
        meas_labels[field] = value_label

    return diagnosis_label, crystalline_label, ref_labels, meas_labels
