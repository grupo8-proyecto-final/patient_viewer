import os
import shutil
from typing import Optional


def copy_file(source: str, destination: str, overwrite: bool = True) -> bool:
    """
    Copia un archivo de origen a destino.

    Args:
        source: Ruta del archivo de origen
        destination: Ruta de destino
        overwrite: Si es True, sobrescribe el archivo de destino si existe

    Returns:
        True si la copia fue exitosa, False en caso contrario
    """
    try:
        # Verificar si el archivo de origen existe
        if not os.path.exists(source):
            print(f"Error: El archivo de origen {source} no existe.")
            return False

        # Verificar si el directorio de destino existe
        dest_dir = os.path.dirname(destination)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        # Verificar si el archivo de destino existe y si se debe sobrescribir
        if os.path.exists(destination):
            if not overwrite:
                print(f"Error: El archivo de destino {destination} ya existe y no se especificó sobrescribir.")
                return False
            os.remove(destination)

        # Copiar el archivo
        shutil.copy2(source, destination)
        return True

    except Exception as e:
        print(f"Error al copiar el archivo: {str(e)}")
        return False


def delete_file(file_path: str) -> bool:
    """
    Elimina un archivo.

    Args:
        file_path: Ruta al archivo a eliminar

    Returns:
        True si la eliminación fue exitosa, False en caso contrario
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error al eliminar el archivo: {str(e)}")
        return False


def open_file_with_default_app(file_path: str) -> bool:
    """
    Abre un archivo con la aplicación predeterminada del sistema.

    Args:
        file_path: Ruta al archivo a abrir

    Returns:
        True si la apertura fue exitosa, False en caso contrario
    """
    import sys
    import subprocess

    try:
        if not os.path.exists(file_path):
            print(f"Error: El archivo {file_path} no existe.")
            return False

        # Abrir con la aplicación predeterminada según el sistema operativo
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        else:  # Linux u otros
            subprocess.run(["xdg-open", file_path], check=True)

        return True

    except Exception as e:
        print(f"Error al abrir el archivo: {str(e)}")
        return False
