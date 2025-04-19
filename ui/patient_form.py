import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Callable, Optional
from core.models import Patient, Eye
import os
import re

# Importación de la función generate_image_path
from features.data_loading import generate_image_path


def create_patient_form(parent: tk.Toplevel, images_dir: str, on_save: Callable[[Dict[str, Any]], None],
                        edit_mode: bool = False, patient: Optional[Patient] = None) -> None:
    """
    Crea un formulario para añadir o editar un paciente.

    Args:
        parent: Ventana padre donde se mostrará el formulario
        images_dir: Directorio base para las imágenes
        on_save: Función de callback para guardar el paciente
        edit_mode: True si es modo edición, False si es modo creación
        patient: Paciente a editar (solo en modo edición)
    """
    parent.geometry("600x600")  # Tamaño inicial con desplazamiento

    # Crear un canvas con barra de desplazamiento
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configurar el canvas para actualizar la región desplazable
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Crear una ventana dentro del canvas para el marco desplazable
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Empaquetar el canvas y la barra de desplazamiento
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Usar scrollable_frame como el contenedor principal del formulario
    form_frame = scrollable_frame

    # Diccionario para almacenar los campos de entrada
    entries = {}

    # Función para añadir un campo de entrada
    def add_field(frame, label, row, entry_type=ttk.Entry):
        ttk.Label(frame, text=label).grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
        entry = entry_type(frame)
        entry.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        return entry

    # Datos generales
    general_frame = ttk.LabelFrame(form_frame, text="Datos Generales", padding="5")
    general_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    entries['patient_id'] = add_field(general_frame, "ID del Paciente:", 0)
    entries['age'] = add_field(general_frame, "Edad:", 1)
    entries['gender'] = ttk.Combobox(general_frame, values=["MALE", "FEMALE"])
    entries['gender'].grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(general_frame, text="Género:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)

    # Datos OD
    od_frame = ttk.LabelFrame(form_frame, text="Ojo Derecho (OD)", padding="5")
    od_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

    entries['od_diagnosis'] = ttk.Combobox(od_frame, values=["HEALTHY", "GLAUCOMA", "SUSPECT"])
    entries['od_diagnosis'].grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(od_frame, text="Diagnóstico:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)

    entries['od_crystalline'] = ttk.Combobox(od_frame, values=["PHAKIC", "PSEUDOPHAKIC", ""])
    entries['od_crystalline'].grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(od_frame, text="Estado Cristalino:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)

    entries['od_sphere'] = add_field(od_frame, "Esfera:", 2)
    entries['od_cylinder'] = add_field(od_frame, "Cilindro:", 3)
    entries['od_axis'] = add_field(od_frame, "Eje:", 4)
    entries['od_pneumatic_iop'] = add_field(od_frame, "IOP Neumático:", 5)
    entries['od_perkins_iop'] = add_field(od_frame, "IOP Perkins:", 6)
    entries['od_pachymetry'] = add_field(od_frame, "Paquimetría:", 7)
    entries['od_axial_length'] = add_field(od_frame, "Longitud Axial:", 8)
    entries['od_mean_defect'] = add_field(od_frame, "Defecto Medio:", 9)

    # Crear una etiqueta informativa para imágenes
    ttk.Label(od_frame, text="Imagen (generada automáticamente):", font=('Arial', 9)).grid(row=10, column=0,
                                                                                           columnspan=3, padx=5, pady=2,
                                                                                           sticky=tk.W)

    # Etiqueta para mostrar el estado de la imagen
    entries['od_image_status'] = ttk.Label(od_frame, text="La imagen se generará automáticamente",
                                           font=('Arial', 9, 'italic'))
    entries['od_image_status'].grid(row=11, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)

    # Botón para verificar disponibilidad de imagen
    ttk.Button(od_frame, text="Verificar Disponibilidad",
               command=lambda: check_image_availability(entries['patient_id'].get(), Eye.RIGHT,
                                                        entries['od_image_status'], images_dir)).grid(row=12, column=0,
                                                                                                      columnspan=3,
                                                                                                      padx=5, pady=2)

    # Datos OS
    os_frame = ttk.LabelFrame(form_frame, text="Ojo Izquierdo (OS)", padding="5")
    os_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    entries['os_diagnosis'] = ttk.Combobox(os_frame, values=["HEALTHY", "GLAUCOMA", "SUSPECT"])
    entries['os_diagnosis'].grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(os_frame, text="Diagnóstico:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)

    entries['os_crystalline'] = ttk.Combobox(os_frame, values=["PHAKIC", "PSEUDOPHAKIC", ""])
    entries['os_crystalline'].grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(os_frame, text="Estado Cristalino:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)

    entries['os_sphere'] = add_field(os_frame, "Esfera:", 2)
    entries['os_cylinder'] = add_field(os_frame, "Cilindro:", 3)
    entries['os_axis'] = add_field(os_frame, "Eje:", 4)
    entries['os_pneumatic_iop'] = add_field(os_frame, "IOP Neumático:", 5)
    entries['os_perkins_iop'] = add_field(os_frame, "IOP Perkins:", 6)
    entries['os_pachymetry'] = add_field(os_frame, "Paquimetría:", 7)
    entries['os_axial_length'] = add_field(os_frame, "Longitud Axial:", 8)
    entries['os_mean_defect'] = add_field(os_frame, "Defecto Medio:", 9)

    # Crear una etiqueta informativa para imágenes
    ttk.Label(os_frame, text="Imagen (generada automáticamente):", font=('Arial', 9)).grid(row=10, column=0,
                                                                                           columnspan=3, padx=5, pady=2,
                                                                                           sticky=tk.W)

    # Etiqueta para mostrar el estado de la imagen
    entries['os_image_status'] = ttk.Label(os_frame, text="La imagen se generará automáticamente",
                                           font=('Arial', 9, 'italic'))
    entries['os_image_status'].grid(row=11, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)

    # Botón para verificar disponibilidad de imagen
    ttk.Button(os_frame, text="Verificar Disponibilidad",
               command=lambda: check_image_availability(entries['patient_id'].get(), Eye.LEFT,
                                                        entries['os_image_status'], images_dir)).grid(row=12, column=0,
                                                                                                      columnspan=3,
                                                                                                      padx=5, pady=2)

    # Enlazar evento de cambio de ID para actualizar las etiquetas de imágenes
    def update_image_labels(*args):
        patient_id = entries['patient_id'].get()
        if patient_id:
            check_image_availability(patient_id, Eye.RIGHT, entries['od_image_status'], images_dir)
            check_image_availability(patient_id, Eye.LEFT, entries['os_image_status'], images_dir)

    entries['patient_id'].bind("<FocusOut>", update_image_labels)

    # Botones de acción
    button_frame = ttk.Frame(form_frame)
    button_frame.grid(row=3, column=0, pady=10)

    ttk.Button(button_frame, text="Guardar",
               command=lambda: save_patient(entries, on_save)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancelar",
               command=parent.destroy).pack(side=tk.LEFT, padx=5)

    # Habilitar desplazamiento con la rueda del ratón
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Rellenar datos si es modo edición
    if edit_mode and patient:
        # Datos generales
        entries['patient_id'].insert(0, patient.patient_id)
        entries['patient_id'].config(state='disabled')  # No permitir editar el ID
        entries['age'].insert(0, patient.age)
        entries['gender'].set(patient.gender.name)

        # Verificar disponibilidad de imágenes para el paciente actual
        check_image_availability(patient.patient_id, Eye.RIGHT, entries['od_image_status'], images_dir)
        check_image_availability(patient.patient_id, Eye.LEFT, entries['os_image_status'], images_dir)

        # Datos OD
        if patient.right_eye:
            entries['od_diagnosis'].set(patient.right_eye.diagnosis.name)
            if patient.right_eye.crystalline_status:
                entries['od_crystalline'].set(patient.right_eye.crystalline_status.name)

            if patient.right_eye.refractive_error:
                entries['od_sphere'].insert(0, patient.right_eye.refractive_error.sphere)
                if patient.right_eye.refractive_error.cylinder is not None:
                    entries['od_cylinder'].insert(0, patient.right_eye.refractive_error.cylinder)
                if patient.right_eye.refractive_error.axis is not None:
                    entries['od_axis'].insert(0, patient.right_eye.refractive_error.axis)

            if patient.right_eye.pneumatic_iop is not None:
                entries['od_pneumatic_iop'].insert(0, patient.right_eye.pneumatic_iop)
            if patient.right_eye.perkins_iop is not None:
                entries['od_perkins_iop'].insert(0, patient.right_eye.perkins_iop)
            if patient.right_eye.pachymetry is not None:
                entries['od_pachymetry'].insert(0, patient.right_eye.pachymetry)
            if patient.right_eye.axial_length is not None:
                entries['od_axial_length'].insert(0, patient.right_eye.axial_length)
            if patient.right_eye.mean_defect is not None:
                entries['od_mean_defect'].insert(0, patient.right_eye.mean_defect)

        # Datos OS
        if patient.left_eye:
            entries['os_diagnosis'].set(patient.left_eye.diagnosis.name)
            if patient.left_eye.crystalline_status:
                entries['os_crystalline'].set(patient.left_eye.crystalline_status.name)

            if patient.left_eye.refractive_error:
                entries['os_sphere'].insert(0, patient.left_eye.refractive_error.sphere)
                if patient.left_eye.refractive_error.cylinder is not None:
                    entries['os_cylinder'].insert(0, patient.left_eye.refractive_error.cylinder)
                if patient.left_eye.refractive_error.axis is not None:
                    entries['os_axis'].insert(0, patient.left_eye.refractive_error.axis)

            if patient.left_eye.pneumatic_iop is not None:
                entries['os_pneumatic_iop'].insert(0, patient.left_eye.pneumatic_iop)
            if patient.left_eye.perkins_iop is not None:
                entries['os_perkins_iop'].insert(0, patient.left_eye.perkins_iop)
            if patient.left_eye.pachymetry is not None:
                entries['os_pachymetry'].insert(0, patient.left_eye.pachymetry)
            if patient.left_eye.axial_length is not None:
                entries['os_axial_length'].insert(0, patient.left_eye.axial_length)
            if patient.left_eye.mean_defect is not None:
                entries['os_mean_defect'].insert(0, patient.left_eye.mean_defect)


def check_image_availability(patient_id: str, eye_type: Eye, status_label: ttk.Label, images_dir: str) -> None:
    """
    Verifica la disponibilidad de una imagen y actualiza la etiqueta de estado.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        status_label: Etiqueta para mostrar el estado
        images_dir: Directorio de imágenes
    """
    if not patient_id:
        status_label.config(text="Por favor, ingrese primero el ID del paciente", foreground="red")
        return

    # Validar el formato del ID del paciente
    if not re.match(r'^\d+$', patient_id):
        status_label.config(text="El ID debe ser numérico para generar imágenes automáticamente", foreground="red")
        return

    # Verificar si ya existe una imagen para este paciente y ojo
    image_path = generate_image_path(patient_id, eye_type)

    if image_path and os.path.exists(image_path):
        status_label.config(text=f"✓ Imagen disponible: {os.path.basename(image_path)}", foreground="green")
    else:
        suffix = "OD" if eye_type == Eye.RIGHT else "OS"
        expected_name = f"RET{patient_id}{suffix}.jpg"
        status_label.config(text=f"✗ Imagen no disponible. Se buscará: {expected_name}", foreground="red")


def save_patient(entries: Dict[str, Any], on_save: Callable[[Dict[str, Any]], None]) -> None:
    """
    Recopila los datos del formulario y llama a la función de guardado.

    Args:
        entries: Diccionario con los campos de entrada
        on_save: Función de callback para guardar el paciente
    """
    # Validar ID de paciente
    patient_id = entries['patient_id'].get()
    if not patient_id:
        messagebox.showerror("Error", "Debe ingresar un ID de paciente")
        return

    if not re.match(r'^\d+$', patient_id):
        messagebox.showwarning("Advertencia", "El ID debe ser numérico para la generación automática de imágenes")

    # Recopilar datos del formulario
    patient_data = {}

    for key, entry in entries.items():
        # Saltar etiquetas de estado de imagen que no son campos de entrada
        if key in ['od_image_status', 'os_image_status']:
            continue

        if isinstance(entry, ttk.Combobox):
            patient_data[key] = entry.get()
        elif isinstance(entry, ttk.Entry):
            patient_data[key] = entry.get()

    # Añadir campos virtuales para rutas de imágenes (serán ignorados ya que se generan automáticamente)
    patient_data['od_image'] = ""
    patient_data['os_image'] = ""

    # Llamar a la función de guardado
    on_save(patient_data)
