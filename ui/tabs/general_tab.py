import tkinter as tk
from tkinter import ttk
from typing import Dict


def setup_general_tab(general_tab: ttk.Frame) -> Dict[str, ttk.Label]:
    """
    Configura la pestaña de información general del paciente.

    Args:
        general_tab: Frame de la pestaña general

    Returns:
        Diccionario con las etiquetas de los campos
    """
    gen_frame = ttk.LabelFrame(general_tab, text="Datos del Paciente", padding="10")
    gen_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    gen_labels = {}
    fields = [
        ("ID del Paciente", "patient_id"),
        ("Edad", "age"),
        ("Género", "gender"),
        ("Diagnóstico General", "diagnosis")
    ]

    for i, (label_text, field) in enumerate(fields):
        label = ttk.Label(gen_frame, text=f"{label_text}:", font=('Arial', 10, 'bold'))
        label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

        value_label = ttk.Label(gen_frame, text="")
        value_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)

        gen_labels[field] = value_label

    return gen_labels
