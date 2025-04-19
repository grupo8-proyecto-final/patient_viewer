import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Tuple, Optional, Union
from core.models import Eye
import logging

# Configurar sistema de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_images.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("image_handling")


def load_and_display_image(image_path: str, label_widget: tk.Label, images_dir: str) -> Tuple[
    Optional[Image.Image], Optional[ImageTk.PhotoImage]]:
    """
    Carga y muestra una imagen en un widget Label.

    Args:
        image_path: Ruta a la imagen
        label_widget: Widget Label donde mostrar la imagen
        images_dir: Directorio alternativo para buscar la imagen

    Returns:
        Tupla con la imagen PIL y la imagen PhotoTk
    """
    logger.info(f"Intentando cargar imagen: {image_path}")
    logger.info(f"Directorio de imágenes: {images_dir}")

    try:
        if not image_path or not isinstance(image_path, str):
            logger.warning(f"Ruta de imagen inválida: {image_path}, tipo: {type(image_path)}")
            label_widget.config(text="Imagen no disponible")
            return None, None

        # Normalizar la ruta y manejar barras invertidas
        if os.name != 'nt':  # Si no es Windows
            normalized_path = image_path.replace('\\', '/')
            logger.debug(f"Ruta normalizada: {normalized_path}")
        else:
            normalized_path = image_path

        # Registrar si la imagen existe en la ruta original
        if os.path.exists(normalized_path):
            logger.info(f"Imagen encontrada en la ruta original: {normalized_path}")
        else:
            logger.warning(f"Imagen no encontrada en la ruta original: {normalized_path}")

            # Intentar con ruta alternativa
            base_name = os.path.basename(normalized_path)
            alt_path = os.path.join(images_dir, base_name)
            logger.debug(f"Intentando con ruta alternativa: {alt_path}")

            if os.path.exists(alt_path):
                logger.info(f"Imagen encontrada en ruta alternativa: {alt_path}")
                normalized_path = alt_path
            else:
                logger.error(
                    f"Imagen no encontrada en ninguna ubicación. Rutas probadas: {normalized_path}, {alt_path}")

                # Listar contenido del directorio de imágenes para depuración
                try:
                    logger.debug(f"Contenido del directorio de imágenes: {os.listdir(images_dir)}")
                except Exception as dir_error:
                    logger.error(f"Error al listar contenido del directorio: {str(dir_error)}")

                label_widget.config(text=f"Imagen no disponible: {base_name}")
                return None, None

        # Cargar y redimensionar la imagen
        logger.debug(f"Abriendo imagen desde: {normalized_path}")
        img = Image.open(normalized_path)
        img_size = img.size
        logger.debug(f"Imagen abierta correctamente. Tamaño original: {img_size}")

        img.thumbnail((250, 250))  # Redimensionar manteniendo proporción
        logger.debug(f"Imagen redimensionada a: {img.size}")

        # Convertir a formato para Tkinter
        photo = ImageTk.PhotoImage(img)
        label_widget.config(image=photo)
        logger.info(f"Imagen cargada y mostrada correctamente: {normalized_path}")

        return img, photo

    except FileNotFoundError as fnf:
        logger.error(f"Archivo no encontrado: {str(fnf)}")
        label_widget.config(
            text=f"Archivo no encontrado: {os.path.basename(image_path) if isinstance(image_path, str) else 'Unknown'}")
        return None, None
    except PermissionError as pe:
        logger.error(f"Error de permisos al acceder a la imagen: {str(pe)}")
        label_widget.config(text="Error de permisos")
        return None, None
    except Exception as e:
        logger.error(f"Error al cargar imagen {image_path}: {str(e)}", exc_info=True)
        if isinstance(image_path, str):
            label_widget.config(text=f"Error al cargar imagen: {os.path.basename(image_path)}")
        else:
            label_widget.config(text="Error al cargar imagen")
        return None, None


def generate_image_path(patient_id: Union[str, int], eye_type: Eye, images_dir: str) -> Optional[str]:
    """
    Genera y verifica la ruta de una imagen para un paciente y tipo de ojo específicos.

    Args:
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        images_dir: Directorio base de imágenes

    Returns:
        Ruta completa a la imagen si existe, None en caso contrario
    """
    # Limpiar el ID y generar el nombre de archivo
    file_name = generate_image_name(patient_id, eye_type)
    file_path = os.path.join(images_dir, file_name)

    logger.debug(f"Generando ruta de imagen para ID: {patient_id}, Ojo: {eye_type.name}")
    logger.debug(f"Nombre de archivo generado: {file_name}")
    logger.debug(f"Ruta completa: {file_path}")

    # Verificar si el archivo existe
    if os.path.exists(file_path):
        logger.info(f"Imagen encontrada: {file_path}")
        return file_path

    # Si no se encuentra la imagen con ID exacto, intentar buscar alternativas
    logger.warning(f"Imagen no encontrada en la ruta generada: {file_path}")

    # Si el ID comienza con ceros, intentar sin ellos
    if isinstance(patient_id, str) and patient_id.startswith('0'):
        numeric_id = patient_id.lstrip('0')
        if numeric_id:  # Asegurarse de que no sea vacío
            alt_file_name = generate_image_name(numeric_id, eye_type)
            alt_file_path = os.path.join(images_dir, alt_file_name)
            logger.debug(f"Intentando con ID sin ceros iniciales: {numeric_id}, ruta: {alt_file_path}")

            if os.path.exists(alt_file_path):
                logger.info(f"Imagen alternativa encontrada: {alt_file_path}")
                return alt_file_path

    # Por último, intentar buscar entre todos los archivos
    try:
        logger.debug("Buscando imágenes que coincidan con el patrón en todo el directorio...")
        pattern = f"RET{str(patient_id).lstrip('0') if str(patient_id).startswith('0') else patient_id}"
        suffix = "OD" if eye_type == Eye.RIGHT else "OS"

        for file in os.listdir(images_dir):
            file_upper = file.upper()
            if file_upper.startswith(pattern.upper()) and file_upper.endswith(f"{suffix.upper()}.JPG"):
                full_path = os.path.join(images_dir, file)
                logger.info(f"Imagen coincidente encontrada con búsqueda en directorio: {full_path}")
                return full_path
    except Exception as e:
        logger.error(f"Error al buscar en directorio: {str(e)}")

    logger.error(f"No se pudo encontrar ninguna imagen para el paciente {patient_id}, ojo {eye_type.name}")
    return None


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
    clean_id = str(patient_id).replace('#', '')

    # Determinar sufijo según el tipo de ojo
    suffix = "OD" if eye_type == Eye.RIGHT else "OS"

    # Crear nombre de archivo
    return f"RET{clean_id}{suffix}.jpg"


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
        messagebox.showerror("Error", "No hay imagen disponible para mostrar")
        return

    try:
        # Normalizar la ruta para el sistema operativo actual
        normalized_path = os.path.normpath(image_path)
        logger.debug(f"Ruta normalizada: {normalized_path}")

        # Reemplazar explícitamente las barras invertidas por barras diagonales en macOS/Linux
        if os.name != 'nt':  # Si no es Windows
            normalized_path = normalized_path.replace('\\', '/')
            logger.debug(f"Ruta adaptada para SO no-Windows: {normalized_path}")

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


def copy_image_to_destination(source_path: str, patient_id: str, eye_type: Eye, images_dir: str) -> str:
    """
    Copia una imagen al directorio de imágenes con un nombre estandarizado.

    Args:
        source_path: Ruta de la imagen original
        patient_id: ID del paciente
        eye_type: Tipo de ojo (RIGHT o LEFT)
        images_dir: Directorio donde se guardarán las imágenes

    Returns:
        Ruta de la imagen copiada
    """
    import shutil

    logger.info(f"Copiando imagen desde {source_path} para paciente {patient_id}, ojo {eye_type.name}")

    # Generar nombre de destino estandarizado
    dest_filename = generate_image_name(patient_id, eye_type)
    dest_path = os.path.join(images_dir, dest_filename)

    logger.debug(f"Nombre de archivo destino: {dest_filename}")
    logger.debug(f"Ruta destino completa: {dest_path}")

    try:
        # Crear directorio si no existe
        if not os.path.exists(images_dir):
            logger.info(f"Creando directorio de imágenes: {images_dir}")
            os.makedirs(images_dir, exist_ok=True)

        # Copiar imagen
        if os.path.exists(source_path) and source_path != dest_path:
            # Si ya existe un archivo en el destino, eliminarlo primero
            if os.path.exists(dest_path):
                logger.warning(f"Eliminando imagen existente en destino: {dest_path}")
                os.remove(dest_path)

            # Copiar la nueva imagen
            logger.info(f"Copiando imagen de {source_path} a {dest_path}")
            shutil.copy(source_path, dest_path)
            logger.info(f"Imagen copiada exitosamente")
        elif not os.path.exists(source_path):
            logger.error(f"Imagen fuente no existe: {source_path}")
        elif source_path == dest_path:
            logger.info(f"La imagen ya está en la ubicación correcta: {source_path}")

        return dest_path
    except Exception as e:
        logger.error(f"Error al copiar imagen: {str(e)}", exc_info=True)
        raise
