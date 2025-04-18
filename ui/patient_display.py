import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from core.models import EyeData, DiagnosisStatus


def update_eye_data(eye_data: Optional[EyeData], diagnosis_label: ttk.Label, crystalline_label: ttk.Label,
                    ref_labels: Dict[str, ttk.Label], meas_labels: Dict[str, ttk.Label]) -> None:
    """
    Actualiza los widgets de la interfaz con los datos del ojo.

    Args:
        eye_data: Datos del ojo (EyeData)
        diagnosis_label: Etiqueta para mostrar el diagnóstico
        crystalline_label: Etiqueta para mostrar el estado del cristalino
        ref_labels: Diccionario de etiquetas para datos refractivos
        meas_labels: Diccionario de etiquetas para mediciones
    """
    if eye_data is None:
        diagnosis_label.config(text="Sin datos")
        crystalline_label.config(text="")

        for label in ref_labels.values():
            label.config(text="")

        for label in meas_labels.values():
            label.config(text="")
        return

    # Actualizar etiquetas principales
    diagnosis_label.config(text=eye_data.diagnosis.name)
    crystalline_label.config(text=eye_data.crystalline_status.name if eye_data.crystalline_status else "N/A")

    # Actualizar error refractivo
    if eye_data.refractive_error:
        ref_labels["esfera"].config(text=eye_data.refractive_error.sphere)
        ref_labels["cilindro"].config(
            text=eye_data.refractive_error.cylinder if eye_data.refractive_error.cylinder is not None else "N/A")
        ref_labels["eje"].config(
            text=eye_data.refractive_error.axis if eye_data.refractive_error.axis is not None else "N/A")
    else:
        for label in ref_labels.values():
            label.config(text="N/A")

    # Actualizar mediciones
    meas_labels["pneumatic_iop"].config(
        text=eye_data.pneumatic_iop if eye_data.pneumatic_iop is not None else "N/A")
    meas_labels["perkins_iop"].config(text=eye_data.perkins_iop if eye_data.perkins_iop is not None else "N/A")
    meas_labels["pachymetry"].config(text=eye_data.pachymetry if eye_data.pachymetry is not None else "N/A")
    meas_labels["axial_length"].config(text=eye_data.axial_length if eye_data.axial_length is not None else "N/A")
    meas_labels["mean_defect"].config(text=eye_data.mean_defect if eye_data.mean_defect is not None else "N/A")

    # Actualizar severidad del glaucoma
    severity = eye_data.get_glaucoma_severity() if eye_data.diagnosis == DiagnosisStatus.GLAUCOMA else "N/A"
    meas_labels["severity"].config(text=severity if severity else "N/A")
