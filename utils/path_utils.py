import os
import sys
from typing import Optional


def normalize_path(path: str) -> str:
    """
    Normaliza una ruta para el sistema operativo actual.

    Args:
        path: Ruta a normalizar

    Returns:
        Ruta normalizada
    """
    # Normalizar la ruta según el sistema operativo
    path = os.path.normpath(path)

    # En sistemas no Windows, convertir barras invertidas a barras diagonales
    if os.name != 'nt':
        path = path.replace('\\', '/')

    return path


def find_file(filename: str, search_dirs: list[str]) -> Optional[str]:
    """
    Busca un archivo en varios directorios.

    Args:
        filename: Nombre del archivo a buscar
        search_dirs: Lista de directorios donde buscar

    Returns:
        Ruta completa al archivo si se encuentra, None en caso contrario
    """
    # Verificar si el nombre del archivo existe directamente
    if os.path.exists(filename):
        return filename

    # Buscar en los directorios proporcionados
    for directory in search_dirs:
        potential_path = os.path.join(directory, filename)
        if os.path.exists(potential_path):
            return potential_path

    # No se encontró el archivo
    return None


def get_base_name(path: str) -> str:
    """
    Obtiene el nombre base de un archivo sin la ruta.

    Args:
        path: Ruta completa al archivo

    Returns:
        Nombre base del archivo
    """
    return os.path.basename(path)


def ensure_directory_exists(directory: str) -> None:
    """
    Asegura que un directorio exista, creándolo si es necesario.

    Args:
        directory: Ruta del directorio
    """
    os.makedirs(directory, exist_ok=True)
