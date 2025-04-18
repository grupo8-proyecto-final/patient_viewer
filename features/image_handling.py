import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Tuple, Optional


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
    try:
        # Normalizar la ruta y manejar barras invertidas
        if os.name != 'nt' and isinstance(image_path, str):  # Si no es Windows
            image_path = image_path.replace('\\', '/')

        # Si no existe la ruta original, intentar con la alternativa
        if not os.path.exists(image_path) and isinstance(image_path, str):
            base_name = os.path.basename(image_path)
            alt_path = os.path.join(images_dir, base_name)

            if os.path.exists(alt_path):
                image_path = alt_path
            else:
                label_widget.config(text=f"Imagen no disponible: {base_name}")
                return None, None

        # Cargar y redimensionar la imagen
        img = Image.open(image_path)
        img.thumbnail((250, 250))  # Redimensionar manteniendo proporción

        # Convertir a formato para Tkinter
        photo = ImageTk.PhotoImage(img)
        label_widget.config(image=photo)

        return img, photo

    except Exception as e:
        print(f"Error al cargar imagen {image_path}: {str(e)}")
        if isinstance(image_path, str):
            label_widget.config(text=f"Error al cargar imagen: {os.path.basename(image_path)}")
        else:
            label_widget.config(text="Error al cargar imagen")
        return None, None


def open_external_image(image_path: str, images_dir: str) -> None:
    """
    Abre una imagen en el visor predeterminado del sistema.

    Args:
        image_path: Ruta a la imagen
        images_dir: Directorio alternativo para buscar la imagen
    """
    if not image_path or not isinstance(image_path, str):
        messagebox.showerror("Error", "No hay imagen disponible para mostrar")
        return

    try:
        # Normalizar la ruta para el sistema operativo actual
        image_path = os.path.normpath(image_path)

        # Reemplazar explícitamente las barras invertidas por barras diagonales en macOS/Linux
        if os.name != 'nt':  # Si no es Windows
            image_path = image_path.replace('\\', '/')

        # Intentar encontrar la imagen en diferentes lugares
        if os.path.exists(image_path):
            # La imagen existe en la ruta completa
            _open_image_with_system_viewer(image_path)
        else:
            # Intentar con solo el nombre base
            base_name = os.path.basename(image_path)
            if os.path.exists(base_name):
                _open_image_with_system_viewer(base_name)
            else:
                # Intentar buscar en la ruta de la variable de entorno
                alt_path = os.path.join(images_dir, base_name)
                if os.path.exists(alt_path):
                    _open_image_with_system_viewer(alt_path)
                else:
                    raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    except Exception as e:
        print(f"Error al abrir imagen: {str(e)}")
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{str(e)}")


def _open_image_with_system_viewer(image_path: str) -> None:
    """
    Abre una imagen con el visor predeterminado del sistema operativo.

    Args:
        image_path: Ruta a la imagen a abrir
    """
    if os.name == 'nt':  # Windows
        os.startfile(image_path)
    elif sys.platform == "darwin":  # macOS
        os.system(f"open '{image_path}'")
    else:  # Linux u otros
        os.system(f"xdg-open '{image_path}'")


def copy_image_to_destination(source_path: str, patient_id: str, eye_side: str, images_dir: str) -> str:
    """
    Copia una imagen al directorio de imágenes con un nombre estandarizado.

    Args:
        source_path: Ruta de la imagen original
        patient_id: ID del paciente
        eye_side: Lado del ojo ('OD' o 'OS')
        images_dir: Directorio donde se guardarán las imágenes

    Returns:
        Ruta de la imagen copiada
    """
    import shutil

    # Limpiar ID de paciente (eliminar caracteres especiales)
    clean_id = patient_id.replace('#', '')

    # Crear nombre de destino
    dest_filename = f"RET{clean_id}{eye_side}.jpg"
    dest_path = os.path.join(images_dir, dest_filename)

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Copiar imagen
    if os.path.exists(source_path) and source_path != dest_path:
        # Si ya existe un archivo en el destino, eliminarlo primero
        if os.path.exists(dest_path):
            os.remove(dest_path)

        # Copiar la nueva imagen
        shutil.copy(source_path, dest_path)

    return dest_path
