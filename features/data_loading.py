import os
import pandas as pd
from typing import Dict, Optional
from core.models import PapilaDataset, Patient, EyeData, RefractiveError, Eye, Gender, DiagnosisStatus, \
    CrystallineStatus

# Obtener rutas de archivos Excel desde variables de entorno
OD_EXCEL_FILE = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
OS_EXCEL_FILE = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')
FUNDUS_IMAGES_DIR = os.environ.get('FUNDUS_IMAGES_DIR', 'FundusImages')


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

    # Construir el nombre del archivo
    file_name = f"RET{clean_id}{suffix}.jpg"
    print(f"Nombre de archivo generado: {file_name}")

    # Construir la ruta completa
    file_path = os.path.join(FUNDUS_IMAGES_DIR, file_name)
    print(f"Ruta completa: {file_path}")
    print(f"Variable FUNDUS_IMAGES_DIR: {FUNDUS_IMAGES_DIR}")
    print(f"¿Existe el archivo? {os.path.exists(file_path)}")

    # Verificar si el archivo existe
    if os.path.exists(file_path):
        print(f"ÉXITO: Se encontró el archivo {file_path}")
        return file_path

    # Si no existe, buscar patrones alternativos (por ejemplo, si el ID está sin ceros a la izquierda)
    try:
        # Intentar con ID numérico sin ceros a la izquierda
        if clean_id.isdigit():
            numeric_id = int(clean_id)
            alt_file_name = f"RET{numeric_id}{suffix}.jpg"
            alt_file_path = os.path.join(FUNDUS_IMAGES_DIR, alt_file_name)
            print(f"Intentando con ID numérico sin ceros: {alt_file_path}")
            print(f"¿Existe? {os.path.exists(alt_file_path)}")

            if os.path.exists(alt_file_path):
                print(f"ÉXITO: Se encontró archivo alternativo {alt_file_path}")
                return alt_file_path
    except ValueError:
        # Si no es numérico, no intentar esta conversión
        print("El ID no es numérico, no se intentó conversión")

    # Buscar en el directorio si hay algún archivo que coincida con el patrón
    print("Buscando archivos que coincidan con el patrón en el directorio...")
    if os.path.exists(FUNDUS_IMAGES_DIR):
        found_files = []
        pattern = f"RET{clean_id}".upper()
        alt_pattern = f"RET{clean_id.lstrip('0')}".upper() if clean_id.isdigit() else None

        for file in os.listdir(FUNDUS_IMAGES_DIR):
            file_upper = file.upper()
            if (file_upper.startswith(pattern) and file_upper.endswith(f"{suffix}.JPG".upper())) or \
                    (alt_pattern and file_upper.startswith(alt_pattern) and file_upper.endswith(
                        f"{suffix}.JPG".upper())):
                found_path = os.path.join(FUNDUS_IMAGES_DIR, file)
                found_files.append(found_path)
                print(f"Encontrado archivo que coincide: {found_path}")

        if found_files:
            print(f"ÉXITO: Se encontró coincidencia {found_files[0]}")
            return found_files[0]
        else:
            print(f"No se encontraron archivos que coincidan con el patrón")
    else:
        print(f"ADVERTENCIA: El directorio {FUNDUS_IMAGES_DIR} no existe")

    # Listar todos los archivos en el directorio para depuración
    if os.path.exists(FUNDUS_IMAGES_DIR):
        print("\nArchivos disponibles en el directorio:")
        for i, file in enumerate(sorted(os.listdir(FUNDUS_IMAGES_DIR))[:20]):  # Mostrar solo los primeros 20
            print(f"  - {file}")
        if len(os.listdir(FUNDUS_IMAGES_DIR)) > 20:
            print(f"  ... y {len(os.listdir(FUNDUS_IMAGES_DIR)) - 20} archivos más")

    print("No se encontró ninguna imagen correspondiente")
    return None


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

    try:
        # Cargar datos de OD - manejar casos donde hay cabeceras fusionadas
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
                    patient_id=str(patient_id),  # Asegurar que sea string
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
        # Manejar el error según sea necesario

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

    # Intentar generar la ruta de la imagen automáticamente
    patient_id = str(row['patient_id'])
    image_path = generate_image_path(patient_id, eye_type)

    # Si se encontró una imagen, agregarla
    if image_path:
        try:
            eye_data.add_fundus_image(image_path)
        except FileNotFoundError:
            # Si hay error al agregar la imagen, lo registramos pero no fallamos
            print(f"No se pudo encontrar la imagen en: {image_path}")

    # Como respaldo, si image_path existe en el DataFrame y no pudimos generar la ruta automáticamente
    elif 'image_path' in row and not pd.isna(row['image_path']) and isinstance(row['image_path'], str):
        try:
            eye_data.add_fundus_image(row['image_path'])
        except FileNotFoundError:
            # Si no encuentra la imagen, buscarla en la carpeta FundusImages
            base_name = os.path.basename(row['image_path'])
            alt_path = os.path.join(FUNDUS_IMAGES_DIR, base_name)
            if os.path.exists(alt_path):
                eye_data.add_fundus_image(alt_path)

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

        # Ya no necesitamos guardar image_path, se generará automáticamente
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
