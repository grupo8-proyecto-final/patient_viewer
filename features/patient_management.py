from typing import Dict, Any
from core.models import Patient, EyeData, RefractiveError, DiagnosisStatus, CrystallineStatus, Eye, Gender, \
    PapilaDataset
import os


def generate_patient_id(dataset: PapilaDataset) -> str:
    """
    Genera un nuevo ID de paciente de forma automática.

    Args:
        dataset: Dataset actual de pacientes

    Returns:
        Nuevo ID de paciente único
    """
    # Obtener todos los IDs existentes
    existing_ids = list(dataset.patients.keys())

    # Si no hay pacientes, comenzar desde 1
    if not existing_ids:
        return "#001"

    # Extraer los números de los IDs existentes
    numeric_ids = []
    for id_str in existing_ids:
        try:
            # Eliminar el símbolo # y convertir a entero
            numeric_id = int(id_str.replace('#', ''))
            numeric_ids.append(numeric_id)
        except ValueError:
            continue

    # Si no se pudieron extraer números, comenzar desde 1
    if not numeric_ids:
        return "#001"

    # Encontrar el próximo número disponible
    next_id = max(numeric_ids) + 1

    # Formatear con ceros a la izquierda
    return f"#{next_id:03d}"


def add_patient(patient_data: Dict[str, Any], images_dir: str) -> Patient:
    """
    Crea un nuevo paciente a partir de los datos del formulario.

    Args:
        patient_data: Datos del paciente
        images_dir: Directorio base para las imágenes

    Returns:
        Objeto Patient creado
    """
    # Crear el paciente
    patient = Patient(
        patient_id=patient_data['patient_id'],
        age=int(patient_data['age']),
        gender=Gender[patient_data['gender']]
    )

    # Añadir datos del ojo derecho si se proporcionan
    if patient_data.get('od_diagnosis'):
        # Crear error refractivo si se proporciona
        refractive_error = None
        if patient_data.get('od_sphere'):
            refractive_error = RefractiveError(
                sphere=float(patient_data['od_sphere']),
                cylinder=float(patient_data.get('od_cylinder', 0)) if patient_data.get('od_cylinder') else None,
                axis=float(patient_data.get('od_axis', 0)) if patient_data.get('od_axis') else None
            )

        # Crear objeto EyeData para OD
        right_eye = EyeData(
            eye_type=Eye.RIGHT,
            diagnosis=DiagnosisStatus[patient_data['od_diagnosis']],
            refractive_error=refractive_error,
            crystalline_status=CrystallineStatus[patient_data['od_crystalline']] if patient_data.get(
                'od_crystalline') else None,
            pneumatic_iop=float(patient_data.get('od_pneumatic_iop')) if patient_data.get('od_pneumatic_iop') else None,
            perkins_iop=float(patient_data.get('od_perkins_iop')) if patient_data.get('od_perkins_iop') else None,
            pachymetry=float(patient_data.get('od_pachymetry')) if patient_data.get('od_pachymetry') else None,
            axial_length=float(patient_data.get('od_axial_length')) if patient_data.get('od_axial_length') else None,
            mean_defect=float(patient_data.get('od_mean_defect')) if patient_data.get('od_mean_defect') else None
        )

        # Añadir imagen de fondo de ojo si se proporciona
        od_image = patient_data.get('od_image')
        if od_image and os.path.exists(od_image):
            right_eye.add_fundus_image(od_image)

        # Añadir ojo derecho al paciente
        patient.set_eye_data(right_eye)

    # Añadir datos del ojo izquierdo si se proporcionan
    if patient_data.get('os_diagnosis'):
        # Crear error refractivo si se proporciona
        refractive_error = None
        if patient_data.get('os_sphere'):
            refractive_error = RefractiveError(
                sphere=float(patient_data['os_sphere']),
                cylinder=float(patient_data.get('os_cylinder', 0)) if patient_data.get('os_cylinder') else None,
                axis=float(patient_data.get('os_axis', 0)) if patient_data.get('os_axis') else None
            )

        # Crear objeto EyeData para OS
        left_eye = EyeData(
            eye_type=Eye.LEFT,
            diagnosis=DiagnosisStatus[patient_data['os_diagnosis']],
            refractive_error=refractive_error,
            crystalline_status=CrystallineStatus[patient_data['os_crystalline']] if patient_data.get(
                'os_crystalline') else None,
            pneumatic_iop=float(patient_data.get('os_pneumatic_iop')) if patient_data.get('os_pneumatic_iop') else None,
            perkins_iop=float(patient_data.get('os_perkins_iop')) if patient_data.get('os_perkins_iop') else None,
            pachymetry=float(patient_data.get('os_pachymetry')) if patient_data.get('os_pachymetry') else None,
            axial_length=float(patient_data.get('os_axial_length')) if patient_data.get('os_axial_length') else None,
            mean_defect=float(patient_data.get('os_mean_defect')) if patient_data.get('os_mean_defect') else None
        )

        # Añadir imagen de fondo de ojo si se proporciona
        os_image = patient_data.get('os_image')
        if os_image and os.path.exists(os_image):
            left_eye.add_fundus_image(os_image)

        # Añadir ojo izquierdo al paciente
        patient.set_eye_data(left_eye)

    return patient


def update_patient(patient_data: Dict[str, Any], patient: Patient, images_dir: str) -> Patient:
    """
    Actualiza un paciente existente con los datos del formulario.

    Args:
        patient_data: Nuevos datos del paciente
        patient: Paciente a actualizar
        images_dir: Directorio base para las imágenes

    Returns:
        Objeto Patient actualizado
    """
    # Actualizar datos básicos del paciente
    patient.age = int(patient_data['age'])
    patient.gender = Gender[patient_data['gender']]

    # Actualizar datos del ojo derecho
    if patient_data.get('od_diagnosis'):
        # Crear error refractivo si se proporciona
        refractive_error = None
        if patient_data.get('od_sphere'):
            refractive_error = RefractiveError(
                sphere=float(patient_data['od_sphere']),
                cylinder=float(patient_data.get('od_cylinder', 0)) if patient_data.get('od_cylinder') else None,
                axis=float(patient_data.get('od_axis', 0)) if patient_data.get('od_axis') else None
            )

        # Crear objeto EyeData para OD
        right_eye = EyeData(
            eye_type=Eye.RIGHT,
            diagnosis=DiagnosisStatus[patient_data['od_diagnosis']],
            refractive_error=refractive_error,
            crystalline_status=CrystallineStatus[patient_data['od_crystalline']] if patient_data.get(
                'od_crystalline') else None,
            pneumatic_iop=float(patient_data.get('od_pneumatic_iop')) if patient_data.get('od_pneumatic_iop') else None,
            perkins_iop=float(patient_data.get('od_perkins_iop')) if patient_data.get('od_perkins_iop') else None,
            pachymetry=float(patient_data.get('od_pachymetry')) if patient_data.get('od_pachymetry') else None,
            axial_length=float(patient_data.get('od_axial_length')) if patient_data.get('od_axial_length') else None,
            mean_defect=float(patient_data.get('od_mean_defect')) if patient_data.get('od_mean_defect') else None
        )

        # Actualizar imagen de fondo de ojo si se proporciona
        od_image = patient_data.get('od_image')
        if od_image and os.path.exists(od_image):
            right_eye.add_fundus_image(od_image)

        # Actualizar ojo derecho del paciente
        patient.set_eye_data(right_eye)

    # Actualizar datos del ojo izquierdo
    if patient_data.get('os_diagnosis'):
        # Crear error refractivo si se proporciona
        refractive_error = None
        if patient_data.get('os_sphere'):
            refractive_error = RefractiveError(
                sphere=float(patient_data['os_sphere']),
                cylinder=float(patient_data.get('os_cylinder', 0)) if patient_data.get('os_cylinder') else None,
                axis=float(patient_data.get('os_axis', 0)) if patient_data.get('os_axis') else None
            )

        # Crear objeto EyeData para OS
        left_eye = EyeData(
            eye_type=Eye.LEFT,
            diagnosis=DiagnosisStatus[patient_data['os_diagnosis']],
            refractive_error=refractive_error,
            crystalline_status=CrystallineStatus[patient_data['os_crystalline']] if patient_data.get(
                'os_crystalline') else None,
            pneumatic_iop=float(patient_data.get('os_pneumatic_iop')) if patient_data.get('os_pneumatic_iop') else None,
            perkins_iop=float(patient_data.get('os_perkins_iop')) if patient_data.get('os_perkins_iop') else None,
            pachymetry=float(patient_data.get('os_pachymetry')) if patient_data.get('os_pachymetry') else None,
            axial_length=float(patient_data.get('os_axial_length')) if patient_data.get('os_axial_length') else None,
            mean_defect=float(patient_data.get('os_mean_defect')) if patient_data.get('os_mean_defect') else None
        )

        # Actualizar imagen de fondo de ojo si se proporciona
        os_image = patient_data.get('os_image')
        if os_image and os.path.exists(os_image):
            left_eye.add_fundus_image(os_image)

        # Actualizar ojo izquierdo del paciente
        patient.set_eye_data(left_eye)

    return patient


def delete_patient(patient_id: str, dataset: PapilaDataset) -> None:
    """
    Elimina un paciente del dataset.

    Args:
        patient_id: ID del paciente a eliminar
        dataset: Dataset que contiene al paciente
    """
    dataset.remove_patient(patient_id)
