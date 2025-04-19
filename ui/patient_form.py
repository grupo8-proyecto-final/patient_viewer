import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Callable, Optional
from pip._internal.utils import logging
from core.models import Patient, Eye, PapilaDataset
from features.patient_management import generate_patient_id


def create_patient_form(parent: tk.Toplevel, images_dir: str, on_save: Callable[[Dict[str, Any]], None],
                        edit_mode: bool = False, patient: Optional[Patient] = None,
                        dataset: Optional[PapilaDataset] = None) -> None:
    """
    Crea un formulario para añadir o editar un paciente.

    Args:
        parent: Ventana padre donde se mostrará el formulario
        images_dir: Directorio base para las imágenes
        on_save: Función de callback para guardar el paciente
        edit_mode: True si es modo edición, False si es modo creación
        patient: Paciente a editar (solo en modo edición)
        dataset: Dataset de pacientes para generar ID automático
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

    # Generar ID de paciente automáticamente
    if not edit_mode and dataset:
        patient_id = generate_patient_id(dataset)
    elif edit_mode and patient:
        patient_id = patient.patient_id
    else:
        patient_id = ""

    # Datos generales
    general_frame = ttk.LabelFrame(form_frame, text="Datos Generales", padding="5")
    general_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    entries['age'] = add_field(general_frame, "Edad:", 0)
    entries['gender'] = ttk.Combobox(general_frame, values=["MALE", "FEMALE"])
    entries['gender'].grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Label(general_frame, text="Género:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)

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

    # Campo para la imagen OD con selector de archivos
    ttk.Label(od_frame, text="Imagen (OD):").grid(row=10, column=0, padx=5, pady=2, sticky=tk.W)
    entries['od_image'] = ttk.Entry(od_frame)
    entries['od_image'].grid(row=10, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Button(od_frame, text="Seleccionar",
               command=lambda: select_image(entries['od_image'])).grid(row=10, column=2, padx=5)

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

    # Campo para la imagen OS con selector de archivos
    ttk.Label(os_frame, text="Imagen (OS):").grid(row=10, column=0, padx=5, pady=2, sticky=tk.W)
    entries['os_image'] = ttk.Entry(os_frame)
    entries['os_image'].grid(row=10, column=1, padx=5, pady=2, sticky=tk.W)
    ttk.Button(os_frame, text="Seleccionar",
               command=lambda: select_image(entries['os_image'])).grid(row=10, column=2, padx=5)

    # Botones de acción
    button_frame = ttk.Frame(form_frame)
    button_frame.grid(row=3, column=0, pady=10)

    ttk.Button(button_frame, text="Guardar",
               command=lambda: save_patient(entries, on_save, images_dir, patient_id)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancelar",
               command=parent.destroy).pack(side=tk.LEFT, padx=5)

    # Habilitar desplazamiento con la rueda del ratón
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Rellenar datos si es modo edición
    if edit_mode and patient:
        # Datos generales
        entries['age'].insert(0, patient.age)
        entries['gender'].set(patient.gender.name)

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
            if patient.right_eye.fundus_image:
                entries['od_image'].insert(0, patient.right_eye.fundus_image)

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
            if patient.left_eye.fundus_image:
                entries['os_image'].insert(0, patient.left_eye.fundus_image)


def select_image(entry: ttk.Entry) -> None:
    """
    Abre un diálogo para seleccionar una imagen y la guarda en el campo de entrada.

    Args:
        entry: Campo de entrada donde se guardará la ruta de la imagen
    """
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)


def save_patient(entries: Dict[str, Any], on_save: Callable[[Dict[str, Any]], None],
                 images_dir: str, patient_id: str) -> None:
    """
    Recopila los datos del formulario y llama a la función de guardado.
    Incluye manejo mejorado de imágenes.
    """
    # Importar el nuevo módulo de utilidades de imágenes
    from utils.image_utils import ensure_directory_exists, save_patient_image
    logger = logging.getLogger("patient_form")

    # Validar edad
    age = entries['age'].get()
    if not age:
        messagebox.showerror("Error", "Debe ingresar la edad del paciente")
        return
    try:
        int(age)
    except ValueError:
        messagebox.showerror("Error", "La edad debe ser un número entero")
        return

    # Validar género
    gender = entries['gender'].get()
    if not gender:
        messagebox.showerror("Error", "Debe seleccionar el género del paciente")
        return

    # Validar diagnóstico OD o OS (al menos uno debe estar presente)
    od_diagnosis = entries['od_diagnosis'].get()
    os_diagnosis = entries['os_diagnosis'].get()
    if not od_diagnosis and not os_diagnosis:
        messagebox.showerror("Error", "Debe ingresar al menos un diagnóstico (OD u OS)")
        return

    # Asegurar que el directorio de imágenes existe
    ensure_directory_exists(images_dir)

    # Procesar imágenes seleccionadas
    try:
        logger.info(f"Procesando imágenes para paciente {patient_id}")

        # Procesar imagen OD si se ha seleccionado
        od_image_path = entries['od_image'].get()
        od_dest_path = None

        if od_image_path and os.path.exists(od_image_path):
            logger.info(f"Guardando imagen OD desde {od_image_path}")
            od_dest_path = save_patient_image(od_image_path, patient_id, Eye.RIGHT, images_dir)

            if od_dest_path:
                logger.info(f"Imagen OD guardada en {od_dest_path}")
                # Actualizar el campo con la nueva ruta
                entries['od_image'].delete(0, tk.END)
                entries['od_image'].insert(0, od_dest_path)
            else:
                logger.error(f"Error al guardar la imagen OD")
                messagebox.showwarning("Advertencia", "No se pudo guardar la imagen del ojo derecho")
        else:
            # Si no hay imagen nueva, conservar la ruta existente
            logger.info(f"No hay nueva imagen OD para procesar o la ruta no existe")
            od_dest_path = od_image_path

        # Proceso similar para imagen OS
        os_image_path = entries['os_image'].get()
        os_dest_path = None

        if os_image_path and os.path.exists(os_image_path):
            logger.info(f"Guardando imagen OS desde {os_image_path}")
            os_dest_path = save_patient_image(os_image_path, patient_id, Eye.LEFT, images_dir)

            if os_dest_path:
                logger.info(f"Imagen OS guardada en {os_dest_path}")
                # Actualizar el campo con la nueva ruta
                entries['os_image'].delete(0, tk.END)
                entries['os_image'].insert(0, os_dest_path)
            else:
                logger.error(f"Error al guardar la imagen OS")
                messagebox.showwarning("Advertencia", "No se pudo guardar la imagen del ojo izquierdo")
        else:
            # Si no hay imagen nueva, conservar la ruta existente
            logger.info(f"No hay nueva imagen OS para procesar o la ruta no existe")
            os_dest_path = os_image_path

    except Exception as e:
        logger.error(f"Error al procesar imágenes: {str(e)}", exc_info=True)
        messagebox.showwarning("Advertencia", f"Error al procesar imágenes: {str(e)}")

    # Preparar datos del paciente para guardar
    patient_data = {
        'patient_id': patient_id,
        'age': entries['age'].get(),
        'gender': entries['gender'].get(),
        'od_diagnosis': entries['od_diagnosis'].get(),
        'od_crystalline': entries['od_crystalline'].get(),
        'od_sphere': entries['od_sphere'].get(),
        'od_cylinder': entries['od_cylinder'].get(),
        'od_axis': entries['od_axis'].get(),
        'od_pneumatic_iop': entries['od_pneumatic_iop'].get(),
        'od_perkins_iop': entries['od_perkins_iop'].get(),
        'od_pachymetry': entries['od_pachymetry'].get(),
        'od_axial_length': entries['od_axial_length'].get(),
        'od_mean_defect': entries['od_mean_defect'].get(),
        'od_image': od_dest_path,  # Usar la nueva ruta generada
        'os_diagnosis': entries['os_diagnosis'].get(),
        'os_crystalline': entries['os_crystalline'].get(),
        'os_sphere': entries['os_sphere'].get(),
        'os_cylinder': entries['os_cylinder'].get(),
        'os_axis': entries['os_axis'].get(),
        'os_pneumatic_iop': entries['os_pneumatic_iop'].get(),
        'os_perkins_iop': entries['os_perkins_iop'].get(),
        'os_pachymetry': entries['os_pachymetry'].get(),
        'os_axial_length': entries['os_axial_length'].get(),
        'os_mean_defect': entries['os_mean_defect'].get(),
        'os_image': os_dest_path,  # Usar la nueva ruta generada
    }

    # Llamar a la función de guardado con los datos
    on_save(patient_data)
