import os
import pandas as pd
from typing import Dict, Optional
from core.models import PapilaDataset, Patient, EyeData, RefractiveError, Eye, Gender, DiagnosisStatus, \
    CrystallineStatus

# Obtener rutas de archivos Excel desde variables de entorno
OD_EXCEL_FILE = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
OS_EXCEL_FILE = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')
FUNDUS_IMAGES_DIR = os.environ.get('FUNDUS_IMAGES_DIR', 'FundusImages')


def get_next_correlative_number(images_dir: str) -> int:
    """
    Obtiene el próximo número correlativo para imágenes de fondo de ojo.

    Args:
        images_dir: Directorio de imágenes de fondo de ojo

    Returns:
        Próximo número correlativo
    """
    # Verificar si el directorio existe
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        return 1

    # Obtener todos los archivos de imagen existentes
    image_files = [f for f in os.listdir(images_dir) if f.startswith('RET') and f.endswith(('.jpg', '.jpeg', '.png'))]

    # Si no hay imágenes, comenzar desde 1
    if not image_files:
        return 1

    # Extraer números de las imágenes existentes
    existing_numbers = []
    for filename in image_files:
        try:
            # Extraer el número entre 'RET' y 'O' (para OD/OS)
            number = int(filename[3:filename.index('O')])
            existing_numbers.append(number)
        except (ValueError, IndexError):
            continue

    # Si no se extrajeron números, comenzar desde 1
    if not existing_numbers:
        return 1

    # Devolver el siguiente número no utilizado
    return max(existing_numbers) + 1


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra las columnas del DataFrame a un formato estándar.

    Args:
        df: DataFrame con columnas a renombrar

    Returns:
        DataFrame con columnas renombradas
    """
    column_mapping = {
        "unnamed: 0": "patient_id",
        "dioptre_1": "sphere",
        "dioptre_2": "cylinder",
        "astigmatism": "axis",
        "phakic/pseudophakic": "crystalline_status",
        "pneumatic": "pneumatic_iop",
        "perkins": "perkins_iop",
        "vf_md": "mean_defect"
    }

    # Crear una copia para no modificar el original
    renamed_df = df.copy()

    # Renombrar columnas existentes basado en el mapeo
    for old_col, new_col in column_mapping.items():
        if old_col in renamed_df.columns:
            renamed_df.rename(columns={old_col: new_col}, inplace=True)

    return renamed_df


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

    # Eliminar filas vacías o incompletas (asumiendo que la primera fila es duplicada de cabecera)
    if len(df) > 0:
        return df.drop(0)
    return df


def generate_image_path(patient_id: str, eye_type: Eye) -> Optional[str]:
    """
    Genera la ruta de la imagen del fondo de ojo basado en el ID del paciente y el tipo de ojo.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)

    Returns:
        Ruta completa a la imagen o None si no existe
    """
    print(f"\n--- DEPURACIÓN GENERATE_IMAGE_PATH ---")
    print(f"ID original recibido: '{patient_id}', tipo: {type(patient_id)}")
    print(f"Tipo de ojo: {eye_type}")

    # Obtener sufijo basado en el tipo de ojo
    suffix = "OD" if eye_type == Eye.RIGHT else "OS"
    print(f"Sufijo: {suffix}")

    # Limpiar ID (eliminar caracteres como #)
    clean_id = str(patient_id).replace('#', '')
    print(f"ID limpiado: '{clean_id}'")

    # Intentar con diferentes formatos de ID
    possible_filenames = [
        f"RET{clean_id}{suffix}.jpg",
        f"RET{int(clean_id) if clean_id.isdigit() else clean_id}{suffix}.jpg"
    ]

    for filename in possible_filenames:
        filepath = os.path.join(FUNDUS_IMAGES_DIR, filename)
        print(f"Buscando: {filepath}")

        if os.path.exists(filepath):
            print(f"ÉXITO: Se encontró el archivo {filepath}")
            return filepath

    # Si no se encuentra imagen existente, generar un nombre nuevo
    new_filename = generate_correlative_image_filename(patient_id, eye_type, FUNDUS_IMAGES_DIR)
    new_filepath = os.path.join(FUNDUS_IMAGES_DIR, new_filename)
    print(f"Generando nuevo nombre de archivo: {new_filepath}")

    return new_filepath


def load_patient_data(od_excel_file: str = None, os_excel_file: str = None) -> PapilaDataset:
    """
    Carga los datos de pacientes desde los archivos Excel.
    """
    # Usar los valores de las variables de entorno si no se proporcionan parámetros
    od_excel_file = od_excel_file or OD_EXCEL_FILE
    os_excel_file = os_excel_file or OS_EXCEL_FILE

    dataset = PapilaDataset()

    try:
        # Cargar datos de OD
        od_df = pd.read_excel(od_excel_file,
                              header=0,  # Usar la primera fila como encabezado
                              dtype={
                                  'patient_id': str,  # Asegurar que patient_id sea string
                                  'age': int,
                                  'gender': int,
                                  'diagnosis': int
                              })

        # Cargar datos de OS de manera similar
        os_df = pd.read_excel(os_excel_file,
                              header=0,
                              dtype={
                                  'patient_id': str,
                                  'age': int,
                                  'gender': int,
                                  'diagnosis': int
                              })

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
                    patient_id=str(patient_id),
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

    except Exception as e:
        print(f"Error al cargar datos: {e}")

    return dataset


def _create_eye_data_from_row(row, eye_type: Eye) -> EyeData:
    """
    Crea un objeto EyeData a partir de una fila del DataFrame.
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

    # Intentar agregar imagen de fondo de ojo
    image_path = generate_image_path(str(row['patient_id']), eye_type)
    if os.path.exists(image_path):
        try:
            eye_data.add_fundus_image(image_path)
        except FileNotFoundError:
            print(f"No se pudo encontrar la imagen en: {image_path}")

    return eye_data


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

    try:
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
        }

        if edit_mode:
            os_df = os_df[os_df['patient_id'] != patient.patient_id]
        os_df = pd.concat([os_df, pd.DataFrame([os_data])], ignore_index=True)
        os_df.to_excel(os_excel_file, index=False)

    except Exception as e:
        print(f"Error al actualizar archivos Excel: {e}")
        # Manejar el error según sea necesario


def delete_from_excel(patient_id: str) -> None:
    """
    Elimina un paciente de los archivos Excel.

    Args:
        patient_id: ID del paciente a eliminar
    """
    # Obtener rutas de archivos Excel desde variables de entorno
    od_excel_file = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
    os_excel_file = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')

    try:
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

    except Exception as e:
        print(f"Error al eliminar paciente de archivos Excel: {e}")
