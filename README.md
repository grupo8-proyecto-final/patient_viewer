# Visualizador de Datos de Pacientes PAPILA

Esta aplicación proporciona una interfaz gráfica y por línea de comandos para la gestión y visualización de datos de
pacientes del dataset PAPILA (Dataset with fundus images and clinical data of both eyes of the same patient for glaucoma
assessment). La implementación utiliza Tkinter para la interfaz gráfica y también ofrece un menú de consola para
operaciones básicas.

![Interfaz de usuario](screenshot.png)

## Características

- **Visualización de datos de pacientes:** Información demográfica y clínica completa
- **Visualización de imágenes de fondo de ojo:** Para ambos ojos (OD y OS)
- **Gestión de pacientes:** Añadir, editar y eliminar pacientes
- **Estadísticas del conjunto de datos:** Visualización de distribuciones y métricas
- **Interfaz intuitiva:** Navegación sencilla entre pacientes y datos
- **Menú de consola:** Alternativa para gestión de pacientes mediante línea de comandos

## Estructura del Proyecto

El proyecto sigue una arquitectura modular por características (Vertical Slice):

```
patient_viewer/
│
├── main.py                     # Punto de entrada de la aplicación GUI
├── menu.py                     # Interfaz por línea de comandos
├── .env                        # Variables de entorno para configuración
│
├── core/                       # Modelos y lógica central
│   ├── __init__.py
│   └── models.py               # Clases Patient, EyeData, etc.
│
├── features/                   # Funcionalidades agrupadas por dominio
│   ├── __init__.py
│   ├── patient_management.py   # Gestión de pacientes
│   ├── data_loading.py         # Carga de datos
│   └── image_utils.py          # Módulo unificado para manejo de imágenes
│
├── ui/                         # Componentes de interfaz de usuario
│   ├── __init__.py
│   ├── app.py                  # Clase principal PatientViewer
│   ├── patient_form.py         # Formulario para añadir/editar pacientes
│   ├── patient_display.py      # Visualización de datos
│   └── tabs/                   # Pestañas de la interfaz
│       ├── __init__.py
│       ├── general_tab.py
│       ├── eye_tab.py
│       └── stats_tab.py
│
└── utils/                      # Utilidades comunes
    └── __init__.py
```

## Requisitos

- Python 3.6 o superior
- Bibliotecas requeridas:
    - tkinter (incluido en la mayoría de instalaciones de Python)
    - Pillow (PIL)
    - pandas
    - numpy
    - python-dotenv

## Instalación

1. Clona este repositorio:

```bash
git clone https://github.com/IonVillarreal/patient_viewer.git
cd patient_viewer
```

2. Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install pillow pandas numpy python-dotenv
```

4. Configura las variables de entorno:
    - Crea un archivo `.env` en el directorio raíz con el siguiente contenido:
   ```
   FUNDUS_IMAGES_DIR=FundusImages
   OD_EXCEL_FILE=patient_data_od.xlsx
   OS_EXCEL_FILE=patient_data_os.xlsx
   ```

## Ejecución

### Interfaz Gráfica

Para iniciar la aplicación con interfaz gráfica:

```bash
python main.py
```

### Menú de Consola

Para usar la interfaz por línea de comandos:

```bash
python menu.py
```

## Uso de la Aplicación

### Interfaz Gráfica

#### Navegación Básica

- La interfaz principal muestra los datos del paciente actual con pestañas para diferentes secciones.
- Use los botones "Anterior" y "Siguiente" para navegar entre pacientes.

#### Gestión de Pacientes

1. **Añadir Paciente**:
    - Haga clic en "Añadir"
    - Complete el formulario con los datos requeridos
    - Haga clic en "Guardar"

2. **Editar Paciente**:
    - Seleccione el paciente que desea editar
    - Haga clic en "Editar"
    - Modifique los datos según sea necesario
    - Haga clic en "Guardar"

3. **Eliminar Paciente**:
    - Seleccione el paciente que desea eliminar
    - Haga clic en "Eliminar"
    - Confirme la eliminación

#### Visualización de Imágenes

- Las imágenes de fondo de ojo se muestran en el panel inferior de la interfaz.
- Haga clic en "Abrir Imagen" para ver la imagen en tamaño completo en su visor de imágenes predeterminado.

#### Estadísticas

- La pestaña "Estadísticas" muestra información resumida sobre todos los pacientes en el conjunto de datos.
- Incluye distribuciones por género, diagnóstico y estadísticas de edad.

### Menú de Consola

El menú de consola ofrece las siguientes opciones:

1. **Ver pacientes**: Muestra una lista de todos los pacientes en el dataset.
2. **Agregar paciente**: Permite añadir un nuevo paciente solicitando datos como ID, edad, género, diagnóstico, etc.
3. **Ver paciente**: Muestra información detallada de un paciente específico por su ID.
4. **Eliminar paciente**: Elimina un paciente del dataset por su ID.
5. **Guardar y salir**: Guarda los cambios realizados y cierra el programa.

Para usar el menú de consola:

1. Ingrese el número de la opción deseada (1-5)
2. Siga las instrucciones en pantalla
3. Los cambios se guardarán automáticamente al elegir la opción 5

## Estructura de Datos

### Archivos Excel

La aplicación utiliza dos archivos Excel para almacenar los datos:

1. **patient_data_od.xlsx**: Datos de ojos derechos
2. **patient_data_os.xlsx**: Datos de ojos izquierdos

Cada archivo tiene las siguientes columnas:

- `patient_id`: Identificador único del paciente
- `age`: Edad del paciente
- `gender`: Género (0 = Hombre, 1 = Mujer)
- `diagnosis`: Diagnóstico (0 = Sano, 1 = Glaucoma, 2 = Sospechoso)
- `sphere`, `cylinder`, `axis`: Datos de error refractivo
- `crystalline_status`: Estado del cristalino (0 = Fáquico, 1 = Pseudofáquico)
- `pneumatic_iop`, `perkins_iop`: Mediciones de presión intraocular
- `pachymetry`: Paquimetría
- `axial_length`: Longitud axial
- `mean_defect`: Defecto medio del campo visual

### Imágenes

Las imágenes de fondo de ojo se almacenan en el directorio `FundusImages` con la siguiente convención de nombres:

- Ojo derecho: `RET{patient_id}OD.jpg`
- Ojo izquierdo: `RET{patient_id}OS.jpg`

## Personalización

### Cambiar rutas de archivos

Modifique el archivo `.env` para cambiar las rutas de los archivos:

```
FUNDUS_IMAGES_DIR=ruta/a/su/directorio/de/imágenes
OD_EXCEL_FILE=ruta/a/su/archivo/excel/od.xlsx
OS_EXCEL_FILE=ruta/a/su/archivo/excel/os.xlsx
```
