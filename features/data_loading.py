import os
import pandas as pd
from typing import Dict, Optional
from core.models import PapilaDataset, Patient, EyeData, RefractiveError, Eye, Gender, DiagnosisStatus, \
    CrystallineStatus

# Obtener rutas de archivos Excel desde variables de entorno
OD_EXCEL_FILE = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
OS_EXCEL_FILE = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')


def rename_columns(df: pd.DataFrame) -> None:
    df.rename(columns={"unnamed: 0": "patient_id"}, inplace=True)
    df.rename(columns={"dioptre_1": "sphere"}, inplace=True)
    df.rename(columns={"dioptre_2": "cylinder"}, inplace=True)
    df.rename(columns={"astigmatism": "axis"}, inplace=True)
    df.rename(columns={"phakic/pseudophakic": "crystalline_status"}, inplace=True)
    df.rename(columns={"pneumatic": "pneumatic_iop"}, inplace=True)
    df.rename(columns={"perkins": "perkins_iop"}, inplace=True)
    df.rename(columns={"vf_md": "mean_defect"}, inplace=True)
    return df

def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los encabezados del DataFrame.

    Args:
        df: DataFrame a limpiar
    Returns:
        DataFrame con encabezados limpios
    """
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.strip()
    df = rename_columns(df)
    # Eliminar filas vacías o incompletas
    return df.drop(0)

def load_patient_data(od_excel_file: str = None, os_excel_file: str = None) -> PapilaDataset:
    """
    Carga los datos de pacientes desde los archivos Excel.

    Args:
        od_excel_file: Ruta al archivo Excel con datos de ojos derechos (opcional)
        os_excel_file: Ruta al archivo Excel con datos de ojos izquierdos (opcional)

    Returns:
        Un objeto PapilaDataset con los datos cargados
    """
    # Usar los valores de las variables de entorno si no se proporcionan parámetros
    od_excel_file = od_excel_file or OD_EXCEL_FILE
    os_excel_file = os_excel_file or OS_EXCEL_FILE

    dataset = PapilaDataset()

    # Cargar datos de OD
    od_df = pd.read_excel(od_excel_file, header=1)
    od_df = clean_headers(od_df)

    # Cargar datos de OS
    os_df = pd.read_excel(os_excel_file, header=1)
    os_df = clean_headers(os_df)

    # Combinar IDs de pacientes
    patient_ids = set(od_df['patient_id'].tolist() + os_df['patient_id'].tolist())

    # Crear pacientes
    for patient_id in patient_ids:
        # Obtener datos OD
        od_data = od_df[od_df['patient_id'] == patient_id]
        # Obtener datos OS
        os_data = os_df[os_df['patient_id'] == patient_id]

        # Si hay datos del paciente
        if not od_data.empty or not os_data.empty:
            # Tomar la primera fila para datos generales (debería ser la misma en ambos archivos)
            patient_row = od_data.iloc[0] if not od_data.empty else os_data.iloc[0]

            # Crear paciente
            patient = Patient(
                patient_id=patient_id,
                age=int(patient_row['age']),
                gender=Gender(int(patient_row['gender']))
            )

            # Agregar datos OD si existen
            if not od_data.empty and not pd.isna(od_data.iloc[0]['diagnosis']):
                right_eye = _create_eye_data_from_row(od_data.iloc[0], Eye.RIGHT)
                patient.set_eye_data(right_eye)

            # Agregar datos OS si existen
            if not os_data.empty and not pd.isna(os_data.iloc[0]['diagnosis']):
                left_eye = _create_eye_data_from_row(os_data.iloc[0], Eye.LEFT)
                patient.set_eye_data(left_eye)

            # Agregar paciente al dataset
            dataset.add_patient(patient)

    return dataset


def _create_eye_data_from_row(row, eye_type: Eye) -> EyeData:
    """
    Crea un objeto EyeData a partir de una fila del DataFrame.

    Args:
        row: Fila del DataFrame con datos del ojo
        eye_type: Tipo de ojo (RIGHT o LEFT)

    Returns:
        Objeto EyeData con los datos del ojo
    """
    # Crear objeto RefractiveError si existe el valor de esfera
    refractive_error = None
    if not pd.isna(row['sphere']):
        refractive_error = RefractiveError(
            sphere=float(row['sphere']),
            cylinder=float(row['cylinder']) if not pd.isna(row['cylinder']) else None,
            axis=float(row['axis']) if not pd.isna(row['axis']) else None
        )

    # Crear objeto EyeData
    eye_data = EyeData(
        eye_type=eye_type,
        diagnosis=DiagnosisStatus(int(row['diagnosis'])),
        refractive_error=refractive_error,
        crystalline_status=CrystallineStatus(int(row['crystalline_status'])) if not pd.isna(
            row['crystalline_status']) else None,
        pneumatic_iop=float(row['pneumatic_iop']) if not pd.isna(row['pneumatic_iop']) else None,
        perkins_iop=float(row['perkins_iop']) if not pd.isna(row['perkins_iop']) else None,
        pachymetry=float(row['pachymetry']) if not pd.isna(row['pachymetry']) else None,
        axial_length=float(row['axial_length']) if not pd.isna(row['axial_length']) else None,
        mean_defect=float(row['mean_defect']) if not pd.isna(row['mean_defect']) else None
    )

    # Agregar imagen de fondo de ojo si existe
    if not pd.isna(row['image_path']) and isinstance(row['image_path'], str):
        try:
            eye_data.add_fundus_image(row['image_path'])
        except FileNotFoundError:
            # Si no encuentra la imagen, buscarla en la carpeta FundusImages
            base_name = os.path.basename(row['image_path'])
            alt_path = os.path.join(os.environ.get('FUNDUS_IMAGES_DIR', 'FundusImages'), base_name)
            if os.path.exists(alt_path):
                eye_data.add_fundus_image(alt_path)

    return eye_data


def load_image_paths(excel_file: str, images_dir: str) -> Dict[str, str]:
    """
    Carga las rutas de las imágenes desde el archivo Excel.

    Args:
        excel_file: Ruta al archivo Excel con datos de imágenes
        images_dir: Directorio base para las imágenes

    Returns:
        Diccionario con IDs de pacientes como claves y rutas de imágenes como valores
    """
    df = pd.read_excel(excel_file, header=1)
    df = clean_headers(df)

    # Ajustar las rutas para usar la variable de entorno
    image_paths = {}
    for patient_id, path in zip(df['patient_id'], df['image_path']):
        if pd.notna(path) and isinstance(path, str):
            # Normalizar la ruta y manejar barras invertidas
            if os.name != 'nt':  # Si no es Windows
                path = path.replace('\\', '/')

            # Extraer el nombre base del archivo
            base_name = os.path.basename(path)

            # Construir la ruta completa usando la variable de entorno
            full_path = os.path.join(images_dir, base_name)

            # Si la ruta alternativa existe, usarla, sino mantener la original
            if os.path.exists(full_path):
                path = full_path

            image_paths[patient_id] = path

    return image_paths


def update_excel_files(patient: Patient, edit_mode: bool) -> None:
    """
    Actualiza los archivos Excel con los datos del paciente.

    Args:
        patient: Paciente a actualizar
        edit_mode: True si es una edición, False si es un nuevo paciente
    """
    # Obtener rutas de archivos Excel desde variables de entorno
    od_excel_file = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
    os_excel_file = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')

    # Actualizar OD
    od_df = pd.read_excel(od_excel_file)
    od_df = clean_headers(od_df)
    od_data = {
        'patient_id': patient.patient_id,
        'age': patient.age,
        'gender': patient.gender.value,
        'diagnosis': patient.right_eye.diagnosis.value if patient.right_eye else "",
        'sphere': patient.right_eye.refractive_error.sphere if patient.right_eye and patient.right_eye.refractive_error else "",
        'cylinder': patient.right_eye.refractive_error.cylinder if patient.right_eye and patient.right_eye.refractive_error and patient.right_eye.refractive_error.cylinder is not None else "",
        'axis': patient.right_eye.refractive_error.axis if patient.right_eye and patient.right_eye.refractive_error and patient.right_eye.refractive_error.axis is not None else "",
        'crystalline_status': patient.right_eye.crystalline_status.value if patient.right_eye and patient.right_eye.crystalline_status else "",
        'pneumatic_iop': patient.right_eye.pneumatic_iop if patient.right_eye and patient.right_eye.pneumatic_iop is not None else "",
        'perkins_iop': patient.right_eye.perkins_iop if patient.right_eye and patient.right_eye.perkins_iop is not None else "",
        'pachymetry': patient.right_eye.pachymetry if patient.right_eye and patient.right_eye.pachymetry is not None else "",
        'axial_length': patient.right_eye.axial_length if patient.right_eye and patient.right_eye.axial_length is not None else "",
        'mean_defect': patient.right_eye.mean_defect if patient.right_eye and patient.right_eye.mean_defect is not None else "",
        'image_path': patient.right_eye.fundus_image if patient.right_eye and patient.right_eye.fundus_image else ""
    }

    if edit_mode:
        od_df = od_df[od_df['patient_id'] != patient.patient_id]
    od_df = pd.concat([od_df, pd.DataFrame([od_data])], ignore_index=True)
    od_df.to_excel(od_excel_file, index=False)

    # Actualizar OS
    os_df = pd.read_excel(os_excel_file)
    os_df = clean_headers(os_df)
    os_data = {
        'patient_id': patient.patient_id,
        'age': patient.age,
        'gender': patient.gender.value,
        'diagnosis': patient.left_eye.diagnosis.value if patient.left_eye else "",
        'sphere': patient.left_eye.refractive_error.sphere if patient.left_eye and patient.left_eye.refractive_error else "",
        'cylinder': patient.left_eye.refractive_error.cylinder if patient.left_eye and patient.left_eye.refractive_error and patient.left_eye.refractive_error.cylinder is not None else "",
        'axis': patient.left_eye.refractive_error.axis if patient.left_eye and patient.left_eye.refractive_error and patient.left_eye.refractive_error.axis is not None else "",
        'crystalline_status': patient.left_eye.crystalline_status.value if patient.left_eye and patient.left_eye.crystalline_status else "",
        'pneumatic_iop': patient.left_eye.pneumatic_iop if patient.left_eye and patient.left_eye.pneumatic_iop is not None else "",
        'perkins_iop': patient.left_eye.perkins_iop if patient.left_eye and patient.left_eye.perkins_iop is not None else "",
        'pachymetry': patient.left_eye.pachymetry if patient.left_eye and patient.left_eye.pachymetry is not None else "",
        'axial_length': patient.left_eye.axial_length if patient.left_eye and patient.left_eye.axial_length is not None else "",
        'mean_defect': patient.left_eye.mean_defect if patient.left_eye and patient.left_eye.mean_defect is not None else "",
        'image_path': patient.left_eye.fundus_image if patient.left_eye and patient.left_eye.fundus_image else ""
    }

    if edit_mode:
        os_df = os_df[os_df['patient_id'] != patient.patient_id]
    os_df = pd.concat([os_df, pd.DataFrame([os_data])], ignore_index=True)
    os_df.to_excel(os_excel_file, index=False)


def delete_from_excel(patient_id: str) -> None:
    """
    Elimina un paciente de los archivos Excel.

    Args:
        patient_id: ID del paciente a eliminar
    """
    # Obtener rutas de archivos Excel desde variables de entorno
    od_excel_file = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
    os_excel_file = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')

    # Eliminar de OD
    od_df = pd.read_excel(od_excel_file)
    od_df = clean_headers(od_df)
    od_df = od_df[od_df['patient_id'] != patient_id]
    od_df.to_excel(od_excel_file, index=False)

    # Eliminar de OS
    os_df = pd.read_excel(os_excel_file)
    os_df = clean_headers(os_df)
    os_df = os_df[os_df['patient_id'] != patient_id]
    os_df.to_excel(os_excel_file, index=False)
