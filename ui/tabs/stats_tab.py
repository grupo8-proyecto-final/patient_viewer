import tkinter as tk
from tkinter import ttk
from core.models import PapilaDataset


def setup_stats_tab(stats_tab: ttk.Frame, dataset: PapilaDataset) -> None:
    """
    Configura la pestaña de estadísticas del conjunto de datos.

    Args:
        stats_tab: Frame de la pestaña de estadísticas
        dataset: Dataset con los datos
    """
    # Limpiar pestaña antes de reconstruirla
    for widget in stats_tab.winfo_children():
        widget.destroy()

    # Obtener estadísticas del dataset
    stats = dataset.get_statistics()

    # Crear frame principal
    stats_frame = ttk.LabelFrame(stats_tab, text="Estadísticas del Conjunto de Datos", padding="10")
    stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Total de pacientes
    ttk.Label(stats_frame, text="Total de Pacientes:", font=('Arial', 10, 'bold')).grid(
        row=0, column=0, sticky=tk.W, padx=5, pady=2)
    ttk.Label(stats_frame, text=str(stats["total_patients"])).grid(
        row=0, column=1, sticky=tk.W, padx=5, pady=2)

    # Distribución por género
    ttk.Label(stats_frame, text="Distribución por Género:", font=('Arial', 10, 'bold')).grid(
        row=1, column=0, sticky=tk.W, padx=5, pady=2)
    gender_frame = ttk.Frame(stats_frame)
    gender_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

    ttk.Label(gender_frame, text=f"Hombres: {stats['gender_distribution']['male']}").pack(anchor=tk.W)
    ttk.Label(gender_frame, text=f"Mujeres: {stats['gender_distribution']['female']}").pack(anchor=tk.W)

    # Distribución por diagnóstico
    ttk.Label(stats_frame, text="Distribución de Diagnóstico:", font=('Arial', 10, 'bold')).grid(
        row=2, column=0, sticky=tk.W, padx=5, pady=2)
    diag_frame = ttk.Frame(stats_frame)
    diag_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

    ttk.Label(diag_frame, text=f"Sanos: {stats['diagnosis_distribution']['healthy']}").pack(anchor=tk.W)
    ttk.Label(diag_frame, text=f"Glaucoma: {stats['diagnosis_distribution']['glaucoma']}").pack(anchor=tk.W)
    ttk.Label(diag_frame, text=f"Sospechosos: {stats['diagnosis_distribution']['suspect']}").pack(anchor=tk.W)
    ttk.Label(diag_frame, text=f"Mixtos: {stats['diagnosis_distribution']['mixed']}").pack(anchor=tk.W)

    # Estadísticas de edad
    ttk.Label(stats_frame, text="Estadísticas de Edad:", font=('Arial', 10, 'bold')).grid(
        row=3, column=0, sticky=tk.W, padx=5, pady=2)
    age_frame = ttk.Frame(stats_frame)
    age_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

    # Manejar el caso donde no hay pacientes
    if stats["total_patients"] > 0:
        ttk.Label(age_frame, text=f"Mínima: {stats['age_stats']['min']}").pack(anchor=tk.W)
        ttk.Label(age_frame, text=f"Máxima: {stats['age_stats']['max']}").pack(anchor=tk.W)
        ttk.Label(age_frame, text=f"Promedio: {stats['age_stats']['avg']:.1f}").pack(anchor=tk.W)
    else:
        ttk.Label(age_frame, text="No hay datos disponibles").pack(anchor=tk.W)
