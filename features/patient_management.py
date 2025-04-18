import os
from typing import Dict, Any, Optional
from core.models import Patient, EyeData, RefractiveError, Eye, Gender, DiagnosisStatus, CrystallineStatus, \
    PapilaDataset
from features.image_handling import copy_image_to_destination


def add_patient(patient_data: Dict[str, Any], images_dir: str) -> Patient:
    """
    Crea un nuevo paciente a partir de los datos proporcionados.

    Args:
        patient_data: Diccionario con datos del paciente
        images_dir: Directorio donde se guardarán las imágenes

    Returns:
        Nuevo objeto Patient
    """
    # Validar datos
    patient_id = patient_data['patient_id']
    if not patient_id:
        raise ValueError("El ID del paciente es obligatorio")

    age = int(patient_data['age']) if patient_data['age'] else 0
    if age <= 0:
        raise ValueError("La edad debe ser mayor que 0")

    gender = Gender[patient_data['gender']]

    # Validar que las imágenes OD y OS no sean el mismo archivo
    od_image_path = patient_data['od_image']
    os_image_path = patient_data['os_image']
    if od_image_path and os_image_path and od_image_path == os_image_path:
        raise ValueError("Las imágenes para OD y OS no pueden ser el mismo archivo")

    # Crear paciente
    patient = Patient(
        patient_id=patient_id,
        age=age,
        gender=gender
    )

    # Crear datos OD
    if patient_data['od_diagnosis']:
        od_data = _create_eye_data(
            patient_data=patient_data,
            eye_type=Eye.RIGHT,
            prefix='od_',
            patient_id=patient_id,
            images_dir=images_dir
        )
        patient.set_eye_data(od_data)

    # Crear datos OS
    if patient_data['os_diagnosis']:
        os_data = _create_eye_data(
            patient_data=patient_data,
            eye_type=Eye.LEFT,
            prefix='os_',
            patient_id=patient_id,
            images_dir=images_dir
        )
        patient.set_eye_data(os_data)

    return patient


def update_patient(patient_data: Dict[str, Any], original_patient: Patient, images_dir: str) -> Patient:
    """
    Actualiza un paciente existente con nuevos datos.

    Args:
        patient_data: Diccionario con los nuevos datos del paciente
        original_patient: Paciente original a actualizar
        images_dir: Directorio donde se guardarán las imágenes

    Returns:
        Paciente actualizado
    """
    # Obtener imágenes existentes
    existing_od_image = original_patient.right_eye.fundus_image if original_patient.right_eye else None
    existing_os_image = original_patient.left_eye.fundus_image if original_patient.left_eye else None

    # Crear nuevo paciente con los datos actualizados
    patient = add_patient(patient_data, images_dir)

    # Conservar imágenes existentes si no se proporcionan nuevas
    if (not patient_data['od_image'] and existing_od_image and
            patient.right_eye and not patient.right_eye.fundus_image):
        patient.right_eye.add_fundus_image(existing_od_image)

    if (not patient_data['os_image'] and existing_os_image and
            patient.left_eye and not patient.left_eye.fundus_image):
        patient.left_eye.add_fundus_image(existing_os_image)

    return patient


def delete_patient(patient_id: str, dataset: PapilaDataset) -> None:
    """
    Elimina un paciente del dataset y sus imágenes asociadas.

    Args:
        patient_id: ID del paciente a eliminar
        dataset: Dataset que contiene al paciente
    """
    patient = dataset.get_patient(patient_id)
    if not patient:
        raise ValueError(f"El paciente con ID {patient_id} no existe")

    # Eliminar imágenes si existen
    if patient.right_eye and patient.right_eye.fundus_image and os.path.exists(patient.right_eye.fundus_image):
        os.remove(patient.right_eye.fundus_image)
    if patient.left_eye and patient.left_eye.fundus_image and os.path.exists(patient.left_eye.fundus_image):
        os.remove(patient.left_eye.fundus_image)

    # Eliminar del dataset
    dataset.remove_patient(patient_id)


def _create_eye_data(patient_data: Dict[str, Any], eye_type: Eye, prefix: str,
                     patient_id: str, images_dir: str) -> EyeData:
    """
    Crea un objeto EyeData a partir de datos del formulario.

    Args:
        patient_data: Diccionario con datos del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        prefix: Prefijo para las claves ('od_' o 'os_')
        patient_id: ID del paciente
        images_dir: Directorio de imágenes

    Returns:
        Objeto EyeData con los datos del ojo
    """
    # Crear objeto RefractiveError si hay datos de esfera
    sphere_key = f"{prefix}sphere"
    cylinder_key = f"{prefix}cylinder"
    axis_key = f"{prefix}axis"

    refractive_error = None
    if patient_data[sphere_key]:
        refractive_error = RefractiveError(
            sphere=float(patient_data[sphere_key]),
            cylinder=float(patient_data[cylinder_key]) if patient_data[cylinder_key] else None,
            axis=float(patient_data[axis_key]) if patient_data[axis_key] else None
        )

    # Crear objeto EyeData
    eye_data = EyeData(
        eye_type=eye_type,
        diagnosis=DiagnosisStatus[patient_data[f"{prefix}diagnosis"]],
        refractive_error=refractive_error,
        crystalline_status=CrystallineStatus[patient_data[f"{prefix}crystalline"]] if patient_data[
            f"{prefix}crystalline"] else None,
        pneumatic_iop=float(patient_data[f"{prefix}pneumatic_iop"]) if patient_data[f"{prefix}pneumatic_iop"] else None,
        perkins_iop=float(patient_data[f"{prefix}perkins_iop"]) if patient_data[f"{prefix}perkins_iop"] else None,
        pachymetry=float(patient_data[f"{prefix}pachymetry"]) if patient_data[f"{prefix}pachymetry"] else None,
        axial_length=float(patient_data[f"{prefix}axial_length"]) if patient_data[f"{prefix}axial_length"] else None,
        mean_defect=float(patient_data[f"{prefix}mean_defect"]) if patient_data[f"{prefix}mean_defect"] else None
    )

    # Agregar imagen si existe
    image_key = f"{prefix}image"
    if patient_data[image_key]:
        eye_side = "OD" if eye_type == Eye.RIGHT else "OS"
        dest_path = copy_image_to_destination(
            patient_data[image_key],
            patient_id,
            eye_side,
            images_dir
        )
        eye_data.add_fundus_image(dest_path)

    return eye_data
