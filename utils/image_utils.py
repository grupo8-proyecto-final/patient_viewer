import logging
import os
import shutil
import sys
import tkinter as tk
from typing import Optional, Union, Tuple

from PIL import Image, ImageTk

from core.models import Eye

# Configurar sistema de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_utils.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("image_utils")


def ensure_directory_exists(directory: str) -> bool:
    """
    Asegura que un directorio exista, creándolo si es necesario.

    Args:
        directory: Ruta del directorio

    Returns:
        True si el directorio existe o fue creado, False en caso de error
    """
    try:
        if not os.path.exists(directory):
            logger.info(f"Creando directorio: {directory}")
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error al crear directorio {directory}: {str(e)}")
        return False


def normalize_path(path: str) -> str:
    """
    Normaliza una ruta para el sistema operativo actual.

    Args:
        path: Ruta a normalizar

    Returns:
        Ruta normalizada
    """
    # Normalizar la ruta según el sistema operativo
    norm_path = os.path.normpath(path)

    # En sistemas no Windows, convertir barras invertidas a barras diagonales
    if os.name != 'nt':
        norm_path = norm_path.replace('\\', '/')

    logger.debug(f"Ruta normalizada: '{path}' -> '{norm_path}'")
    return norm_path


def generate_image_name(patient_id: Union[str, int], eye_type: Eye) -> str:
    """
    Genera un nombre de archivo estandarizado para una imagen de fondo de ojo.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)

    Returns:
        Nombre de archivo estandarizado
    """
    # Limpiar ID de paciente (eliminar caracteres especiales)
    clean_id = str(patient_id).replace('#', '').strip()

    # Determinar sufijo según el tipo de ojo
    suffix = "OD" if eye_type == Eye.RIGHT else "OS"

    # Crear nombre de archivo
    return f"RET{clean_id}{suffix}.jpg"


def get_next_correlative_number(images_dir: str) -> int:
    """
    Obtiene el próximo número correlativo para imágenes de fondo de ojo.

    Args:
        images_dir: Directorio de imágenes de fondo de ojo

    Returns:
        Próximo número correlativo
    """
    try:
        # Verificar si el directorio existe
        if not os.path.exists(images_dir):
            ensure_directory_exists(images_dir)
            return 1

        # Obtener todos los archivos de imagen existentes
        image_files = [f for f in os.listdir(images_dir)
                       if f.upper().startswith('RET') and
                       f.upper().endswith(('.JPG', '.JPEG', '.PNG'))]

        # Si no hay imágenes, comenzar desde 1
        if not image_files:
            return 1

        # Extraer números de las imágenes existentes
        existing_numbers = []
        for filename in image_files:
            try:
                # Buscar el índice de 'O' para separar el número del sufijo (OD/OS)
                o_index = filename.upper().find('O')
                if o_index > 3:  # Asegurarse que hay al menos "RET" + algún número
                    # Extraer el número entre 'RET' y 'O'
                    num_part = filename[3:o_index]
                    if num_part.isdigit():
                        existing_numbers.append(int(num_part))
            except (ValueError, IndexError) as e:
                logger.warning(f"Error al extraer número de '{filename}': {str(e)}")
                continue

        # Si no se extrajeron números, comenzar desde 1
        if not existing_numbers:
            return 1

        # Devolver el siguiente número no utilizado
        return max(existing_numbers) + 1

    except Exception as e:
        logger.error(f"Error al obtener número correlativo: {str(e)}")
        return 1  # En caso de error, devolver 1 como valor predeterminado


def generate_correlative_filename(patient_id: str, eye_type: Eye, images_dir: str) -> str:
    """
    Genera un nombre de archivo con número correlativo.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        images_dir: Directorio de imágenes

    Returns:
        Nombre de archivo generado
    """
    # Obtener sufijo basado en el tipo de ojo
    suffix = "OD" if eye_type == Eye.RIGHT else "OS"

    # Obtener el próximo número correlativo
    next_number = get_next_correlative_number(images_dir)
    logger.debug(f"Próximo número correlativo: {next_number}")

    # Generar nombre de archivo con relleno de ceros
    filename = f"RET{next_number:03d}{suffix}.jpg"
    logger.info(f"Nombre de archivo generado: {filename}")

    return filename


def copy_image(source_path: str, dest_path: str, overwrite: bool = True) -> bool:
    """
    Copia una imagen de origen a destino.

    Args:
        source_path: Ruta de la imagen original
        dest_path: Ruta de destino
        overwrite: Si debe sobrescribir la imagen si ya existe

    Returns:
        True si la copia fue exitosa, False en caso contrario
    """
    try:
        # Normalizar rutas
        source_path = normalize_path(source_path)
        dest_path = normalize_path(dest_path)

        logger.debug(f"Copiando imagen de '{source_path}' a '{dest_path}'")

        # Verificar si el archivo de origen existe
        if not os.path.exists(source_path):
            logger.error(f"La imagen de origen no existe: {source_path}")
            return False

        # Crear directorio de destino si no existe
        dest_dir = os.path.dirname(dest_path)
        if not ensure_directory_exists(dest_dir):
            return False

        # Verificar si el archivo de destino ya existe
        if os.path.exists(dest_path):
            if not overwrite:
                logger.warning(f"La imagen de destino ya existe y no se permite sobrescribir: {dest_path}")
                return False
            else:
                logger.info(f"Sobrescribiendo imagen existente: {dest_path}")
                os.remove(dest_path)

        # Copiar el archivo
        shutil.copy2(source_path, dest_path)
        logger.info(f"Imagen copiada exitosamente a {dest_path}")

        return True

    except Exception as e:
        logger.error(f"Error al copiar imagen: {str(e)}", exc_info=True)
        return False


def find_image_for_patient(patient_id: str, eye_type: Eye, images_dir: str) -> Optional[str]:
    """
    Busca la imagen existente para un paciente y tipo de ojo.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        images_dir: Directorio base de imágenes

    Returns:
        Ruta a la imagen si existe, None en caso contrario
    """
    try:
        # Asegurar que el directorio existe
        if not os.path.exists(images_dir):
            logger.warning(f"El directorio de imágenes no existe: {images_dir}")
            return None

        # Limpiar ID y determinar sufijo
        clean_id = str(patient_id).replace('#', '').strip()
        suffix = "OD" if eye_type == Eye.RIGHT else "OS"

        # Lista de posibles nombres de archivo a buscar
        possible_filenames = [
            f"RET{clean_id}{suffix}.jpg",  # Formato estándar
        ]

        # Intentar también sin ceros a la izquierda si es un número
        if clean_id.isdigit():
            numeric_id = int(clean_id)
            possible_filenames.append(f"RET{numeric_id}{suffix}.jpg")

        # Buscar los archivos
        for filename in possible_filenames:
            filepath = os.path.join(images_dir, filename)
            if os.path.exists(filepath):
                logger.info(f"Imagen encontrada: {filepath}")
                return normalize_path(filepath)

        # Buscar por patrón en el directorio completo
        pattern_prefix = f"RET{clean_id}"
        pattern_suffix = suffix + ".jpg"

        for file in os.listdir(images_dir):
            file_upper = file.upper()
            if (file_upper.startswith(pattern_prefix.upper()) and
                    file_upper.endswith(pattern_suffix.upper())):
                filepath = os.path.join(images_dir, file)
                logger.info(f"Imagen encontrada con búsqueda de patrón: {filepath}")
                return normalize_path(filepath)

        logger.warning(f"No se encontró imagen para paciente {patient_id}, ojo {eye_type.name}")
        return None

    except Exception as e:
        logger.error(f"Error buscando imagen: {str(e)}", exc_info=True)
        return None


def save_patient_image(source_path: str, patient_id: str, eye_type: Eye,
                       images_dir: str) -> Optional[str]:
    """
    Guarda una imagen para un paciente específico.

    Args:
        source_path: Ruta de la imagen original
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        images_dir: Directorio base para imágenes

    Returns:
        Ruta de la imagen guardada, None en caso de error
    """
    try:
        # Verificar si hay una ruta de origen
        if not source_path or not os.path.exists(source_path):
            logger.warning(f"No hay imagen para guardar o no existe: {source_path}")
            return None

        # Crear directorio de imágenes si no existe
        if not ensure_directory_exists(images_dir):
            return None

        # Generar nombre de archivo estándar
        dest_filename = generate_image_name(patient_id, eye_type)
        dest_path = os.path.join(images_dir, dest_filename)

        # Copiar la imagen
        if copy_image(source_path, dest_path, overwrite=True):
            return normalize_path(dest_path)

        return None

    except Exception as e:
        logger.error(f"Error al guardar imagen: {str(e)}", exc_info=True)
        return None


def load_and_display_image(image_path: str, label_widget: tk.Label, images_dir: str) -> Tuple[
    Optional[Image.Image], Optional[ImageTk.PhotoImage]]:
    """
    Carga y muestra una imagen en un widget Label con un tamaño más compacto.
    """
    try:
        logger.debug(f"Intentando cargar imagen: {image_path}")

        if not image_path or not isinstance(image_path, str):
            logger.warning(f"Ruta de imagen inválida: {image_path}, tipo: {type(image_path)}")
            label_widget.config(text="Imagen no disponible")
            return None, None

        # Normalizar ruta
        norm_path = normalize_path(image_path)

        # Verificar si existe la imagen
        if not os.path.exists(norm_path):
            # Intentar buscar en directorio alternativo
            base_name = os.path.basename(norm_path)
            alt_path = os.path.join(images_dir, base_name)

            if os.path.exists(alt_path):
                norm_path = alt_path
                logger.info(f"Imagen encontrada en ruta alternativa: {alt_path}")
            else:
                logger.warning(f"Imagen no encontrada: {norm_path} ni {alt_path}")
                label_widget.config(text=f"No disponible")
                return None, None

        # Cargar y redimensionar la imagen - TAMAÑO REDUCIDO PARA UI COMPACTA
        try:
            img = Image.open(norm_path)
            logger.debug(f"Imagen abierta. Tamaño original: {img.size}")
            img.thumbnail((200, 200))  # Tamaño reducido para UI compacta
            logger.debug(f"Imagen redimensionada. Nuevo tamaño: {img.size}")
        except Exception as img_error:
            logger.error(f"Error abriendo imagen: {str(img_error)}")
            label_widget.config(text="Error")
            return None, None

        # Convertir a formato para Tkinter
        try:
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo)
            logger.debug(f"Imagen mostrada en widget")
            return img, photo
        except Exception as photo_error:
            logger.error(f"Error creando PhotoImage: {str(photo_error)}")
            label_widget.config(text="Error")
            return img, None

    except Exception as e:
        logger.error(f"Error general al cargar imagen: {str(e)}", exc_info=True)
        label_widget.config(text="Error")
        return None, None


def open_image_with_default_app(image_path: str, images_dir: str) -> bool:
    """
    Abre una imagen con la aplicación predeterminada del sistema.

    Args:
        image_path: Ruta a la imagen
        images_dir: Directorio alternativo para buscar la imagen

    Returns:
        True si se abrió correctamente, False en caso contrario
    """
    try:
        if not image_path or not isinstance(image_path, str):
            logger.warning(f"Ruta de imagen inválida para abrir: {image_path}")
            return False

        # Normalizar la ruta
        norm_path = normalize_path(image_path)
        logger.debug(f"Intentando abrir imagen: {norm_path}")

        # Verificar si existe la imagen
        if not os.path.exists(norm_path):
            # Intentar con solo el nombre base
            base_name = os.path.basename(norm_path)

            if os.path.exists(base_name):
                norm_path = base_name
                logger.debug(f"Imagen encontrada como nombre base: {base_name}")
            else:
                # Intentar en el directorio alternativo
                alt_path = os.path.join(images_dir, base_name)

                if os.path.exists(alt_path):
                    norm_path = alt_path
                    logger.debug(f"Imagen encontrada en ruta alternativa: {alt_path}")
                else:
                    logger.error(f"Imagen no encontrada en ninguna ubicación probada")
                    return False

        # Abrir la imagen con la aplicación predeterminada
        logger.info(f"Abriendo imagen con aplicación predeterminada: {norm_path}")

        if os.name == 'nt':  # Windows
            os.startfile(norm_path)
        elif sys.platform == "darwin":  # macOS
            os.system(f"open '{norm_path}'")
        else:  # Linux u otros
            os.system(f"xdg-open '{norm_path}'")

        return True

    except Exception as e:
        logger.error(f"Error al abrir imagen con aplicación predeterminada: {str(e)}", exc_info=True)
        return False


def open_external_image(image_path: str, images_dir: str) -> None:
    """
    Abre una imagen en el visor predeterminado del sistema.

    Args:
        image_path: Ruta a la imagen
        images_dir: Directorio alternativo para buscar la imagen
    """
    logger.info(f"Intentando abrir imagen externa: {image_path}")

    if not image_path or not isinstance(image_path, str):
        logger.warning(f"Ruta de imagen inválida para abrir externamente: {image_path}")
        from tkinter import messagebox
        messagebox.showerror("Error", "No hay imagen disponible para mostrar")
        return

    try:
        # Normalizar la ruta para el sistema operativo actual
        normalized_path = normalize_path(image_path)
        logger.debug(f"Ruta normalizada: {normalized_path}")

        # Intentar encontrar la imagen en diferentes lugares
        if os.path.exists(normalized_path):
            logger.info(f"Imagen encontrada en la ruta completa: {normalized_path}")
            _open_image_with_system_viewer(normalized_path)
        else:
            logger.warning(f"Imagen no encontrada en la ruta completa: {normalized_path}")

            # Intentar con solo el nombre base
            base_name = os.path.basename(normalized_path)
            if os.path.exists(base_name):
                logger.info(f"Imagen encontrada como nombre base: {base_name}")
                _open_image_with_system_viewer(base_name)
            else:
                logger.warning(f"Imagen no encontrada como nombre base: {base_name}")

                # Intentar buscar en la ruta de la variable de entorno
                alt_path = os.path.join(images_dir, base_name)
                logger.debug(f"Intentando con ruta alternativa: {alt_path}")

                if os.path.exists(alt_path):
                    logger.info(f"Imagen encontrada en ruta alternativa: {alt_path}")
                    _open_image_with_system_viewer(alt_path)
                else:
                    logger.error(
                        f"Imagen no encontrada en ninguna ubicación. Rutas probadas: {normalized_path}, {base_name}, {alt_path}")
                    raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    except Exception as e:
        logger.error(f"Error al abrir imagen: {str(e)}", exc_info=True)
        from tkinter import messagebox
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{str(e)}")


def _open_image_with_system_viewer(image_path: str) -> None:
    """
    Abre una imagen con el visor predeterminado del sistema operativo.

    Args:
        image_path: Ruta a la imagen a abrir
    """
    logger.info(f"Abriendo imagen con visor del sistema: {image_path}")

    try:
        if os.name == 'nt':  # Windows
            logger.debug("Detectado SO Windows, usando os.startfile")
            os.startfile(image_path)
        elif sys.platform == "darwin":  # macOS
            logger.debug("Detectado SO macOS, usando comando 'open'")
            cmd = f"open '{image_path}'"
            logger.debug(f"Ejecutando comando: {cmd}")
            os.system(cmd)
        else:  # Linux u otros
            logger.debug("Detectado SO Linux/otro, usando comando 'xdg-open'")
            cmd = f"xdg-open '{image_path}'"
            logger.debug(f"Ejecutando comando: {cmd}")
            os.system(cmd)

        logger.info(f"Imagen abierta correctamente: {image_path}")
    except Exception as e:
        logger.error(f"Error al abrir imagen con visor del sistema: {str(e)}", exc_info=True)
        raise
