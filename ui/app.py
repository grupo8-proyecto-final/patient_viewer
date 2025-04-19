import os
import tkinter as tk
from tkinter import ttk, messagebox

from core.models import Eye
# Importaciones internas
from features.data_loading import load_patient_data
from features.patient_management import add_patient, update_patient, delete_patient
from ui.patient_form import create_patient_form
from ui.tabs.eye_tab import setup_eye_tab
from ui.tabs.general_tab import setup_general_tab
from ui.tabs.stats_tab import setup_stats_tab
from utils.image_utils import open_external_image

# Obtener la ruta de imágenes de las variables de entorno
FUNDUS_IMAGES_DIR = os.environ.get('FUNDUS_IMAGES_DIR', 'FundusImages')


class PatientViewer:
    def __init__(self, root):
        self.images_dir = os.environ.get('FUNDUS_IMAGES_DIR', 'FundusImages')
        self.od_excel_file = os.environ.get('OD_EXCEL_FILE', 'patient_data_od.xlsx')
        self.os_excel_file = os.environ.get('OS_EXCEL_FILE', 'patient_data_os.xlsx')
        self.root = root
        self.root.title("Visualizador de Datos de Pacientes")

        # Configurar tamaño y posición
        self._configure_window()

        # Cargar los datos usando las variables de entorno
        self.dataset = load_patient_data(self.od_excel_file, self.os_excel_file)

        # Ya no necesitamos cargar explícitamente las rutas de imágenes
        # self.od_images = load_image_paths(self.od_excel_file, self.images_dir)
        # self.os_images = load_image_paths(self.os_excel_file, self.images_dir)

        self.patient_ids = sorted(self.dataset.patients.keys())
        self.current_index = 0 if self.patient_ids else -1

        # Variables para las imágenes
        self.od_image = None
        self.os_image = None
        self.od_photo = None
        self.os_photo = None

        # Crear la interfaz
        self._create_widgets()

        # Reducir el problema de foco/parpadeo al cambiar pestañas
        self.notebook.bind("<<NotebookTabChanged>>", self._handle_tab_change)

        # Mostrar datos del paciente actual
        if self.patient_ids:
            self.display_patient_data()
        else:
            self.clear_display()

    def _configure_window(self):
        window_width = 780
        window_height = 780  # Reducción de altura
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.bind("<Map>", lambda e: self.bring_to_front())

        # Aplicar un estilo más compacto - reducir paddings
        style = ttk.Style()
        style.configure("TFrame", padding=2)  # Reducir padding en frames
        style.configure("TLabelframe", padding=2)  # Reducir padding en labelframes
        style.configure("TButton", padding=(4, 2))  # Botones más compactos
        style.configure("TLabel", padding=(2, 1))  # Etiquetas más compactas

    def bring_to_front(self):
        """Trae la ventana al frente cuando se restaura"""
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        self.root.focus_force()

    def _handle_tab_change(self, event):
        """Maneja el cambio de pestañas para minimizar el efecto de parpadeo/cambio de foco"""
        # Usar after para dar tiempo al redibujado antes de realizar otras acciones
        self.root.after(50, lambda: self.root.update_idletasks())
        # Evitar cambios innecesarios de foco
        current_tab = self.notebook.select()
        self.notebook.focus_set()

    # Modificar el método _configure_window para un tamaño más compacto
    def _configure_window(self):
        """Configura el tamaño y posición de la ventana para una UI más compacta"""
        # Reducimos ligeramente el ancho, pero sobre todo la altura
        window_width = 780
        window_height = 780  # Reducción de altura
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.bind("<Map>", lambda e: self.bring_to_front())

        # Aplicar un estilo más compacto - reducir paddings
        style = ttk.Style()
        style.configure("TFrame", padding=2)  # Reducir padding en frames
        style.configure("TLabelframe", padding=2)  # Reducir padding en labelframes
        style.configure("TButton", padding=(4, 2))  # Botones más compactos
        style.configure("TLabel", padding=(2, 1))  # Etiquetas más compactas

    # Modificar el método _create_widgets para una UI más compacta
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz con un diseño más compacto"""
        # Frame principal con padding reducido
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para la información del paciente actual - reducir espacio
        patient_info_frame = ttk.Frame(main_frame)
        patient_info_frame.pack(fill=tk.X, pady=(0, 5))

        self.patient_label = ttk.Label(patient_info_frame, text="", font=('Arial', 10, 'bold'))
        self.patient_label.pack(side=tk.TOP, pady=(0, 2))

        # Notebook para pestañas - reducir espacio después
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=False, pady=(0, 5))  # expand=False para limitar expansión

        # Crear pestañas
        self.general_tab = ttk.Frame(self.notebook)
        self.od_tab = ttk.Frame(self.notebook)
        self.os_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.general_tab, text="Información General")
        self.notebook.add(self.od_tab, text="Ojo Derecho (OD)")
        self.notebook.add(self.os_tab, text="Ojo Izquierdo (OS)")
        self.notebook.add(self.stats_tab, text="Estadísticas")

        # Configurar pestañas
        self.gen_labels = setup_general_tab(self.general_tab)
        self.od_diagnosis_label, self.od_crystalline_label, self.od_ref_labels, self.od_meas_labels = setup_eye_tab(
            self.od_tab, "right")
        self.os_diagnosis_label, self.os_crystalline_label, self.os_ref_labels, self.os_meas_labels = setup_eye_tab(
            self.os_tab, "left")
        setup_stats_tab(self.stats_tab, self.dataset)

        # Frame para imágenes
        images_frame = ttk.LabelFrame(main_frame, text="Imágenes de Fondo de Ojo")
        images_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Contenedor para ambas imágenes
        images_container = ttk.Frame(images_frame)
        images_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Imagen OD
        od_img_frame = ttk.Frame(images_container)
        od_img_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))

        ttk.Label(od_img_frame, text="Ojo Derecho (OD)", font=('Arial', 9, 'bold')).pack(pady=(0, 2))
        self.od_img_label = ttk.Label(od_img_frame, border=1, relief="solid")
        self.od_img_label.pack(fill=tk.BOTH, expand=True, pady=(0, 2))
        self.od_img_btn = ttk.Button(od_img_frame, text="Abrir Imagen", command=lambda: self.open_image('od'))
        self.od_img_btn.pack()

        # Imagen OS
        os_img_frame = ttk.Frame(images_container)
        os_img_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))

        ttk.Label(os_img_frame, text="Ojo Izquierdo (OS)", font=('Arial', 9, 'bold')).pack(pady=(0, 2))
        self.os_img_label = ttk.Label(os_img_frame, border=1, relief="solid")
        self.os_img_label.pack(fill=tk.BOTH, expand=True, pady=(0, 2))
        self.os_img_btn = ttk.Button(os_img_frame, text="Abrir Imagen", command=lambda: self.open_image('os'))
        self.os_img_btn.pack()

        # Controles de navegación
        nav_frame = ttk.LabelFrame(main_frame, text="Navegación")
        nav_frame.pack(fill=tk.X, pady=(0, 2))

        # Grupo de botones de navegació
        navigation_buttons = ttk.Frame(nav_frame)
        navigation_buttons.pack(pady=3, fill=tk.X)

        # Botones de navegación de pacientes
        nav_patient_frame = ttk.Frame(navigation_buttons)
        nav_patient_frame.pack(side=tk.LEFT, padx=5)

        self.prev_btn = ttk.Button(nav_patient_frame, text="< Anterior", command=self.prev_patient, width=10)
        self.prev_btn.pack(side=tk.LEFT, padx=1)

        self.next_btn = ttk.Button(nav_patient_frame, text="Siguiente >", command=self.next_patient, width=10)
        self.next_btn.pack(side=tk.LEFT, padx=1)

        # Grupo de botones de gestión
        manage_frame = ttk.Frame(navigation_buttons)
        manage_frame.pack(side=tk.RIGHT, padx=5)

        self.add_btn = ttk.Button(manage_frame, text="Añadir", command=self.add_patient, width=8)
        self.add_btn.pack(side=tk.LEFT, padx=1)

        self.edit_btn = ttk.Button(manage_frame, text="Editar", command=self.edit_patient, width=8)
        self.edit_btn.pack(side=tk.LEFT, padx=1)

        self.delete_btn = ttk.Button(manage_frame, text="Eliminar", command=self.delete_patient, width=8)
        self.delete_btn.pack(side=tk.LEFT, padx=1)

    def display_patient_data(self):
        """Muestra los datos del paciente actual"""
        if not self.patient_ids:
            return

        patient_id = self.patient_ids[self.current_index]
        patient = self.dataset.patients[patient_id]

        # Actualizar etiqueta de paciente
        self.patient_label.config(
            text=f"Paciente {self.current_index + 1} de {len(self.patient_ids)} - ID: {patient_id}")

        # Actualizar información general
        self.gen_labels["patient_id"].config(text=patient.patient_id)
        self.gen_labels["age"].config(text=patient.age)
        self.gen_labels["gender"].config(text="Hombre" if patient.gender.name == "MALE" else "Mujer")
        self.gen_labels["diagnosis"].config(text=patient.get_patient_diagnosis())

        # Actualizar información de ojos
        from ui.patient_display import update_eye_data
        update_eye_data(patient.right_eye, self.od_diagnosis_label, self.od_crystalline_label,
                        self.od_ref_labels, self.od_meas_labels)
        update_eye_data(patient.left_eye, self.os_diagnosis_label, self.os_crystalline_label,
                        self.os_ref_labels, self.os_meas_labels)

        # Actualizar imágenes
        self.update_images(patient_id)

        # Configurar estado de botones de navegación
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.patient_ids) - 1 else tk.DISABLED)
        self.edit_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)

    def update_images(self, patient_id):
        """
        Actualiza las imágenes de fondo de ojo para el paciente actual
        usando el nuevo módulo de utilidades de imágenes.
        """
        # Importar el nuevo módulo de utilidades de imágenes
        from utils.image_utils import find_image_for_patient, load_and_display_image

        # Limpiar imágenes previas
        self.od_img_label.config(image='')
        self.os_img_label.config(image='')
        self.od_photo = None
        self.os_photo = None

        # Obtener el paciente actual
        patient = self.dataset.patients[patient_id]

        # Log para depuración
        print(f"DEBUG - Actualizando imágenes para paciente: {patient_id}")
        print(f"DEBUG - Directorio de imágenes: {self.images_dir}")

        # Buscar y cargar imagen OD
        od_path = find_image_for_patient(patient_id, Eye.RIGHT, self.images_dir)
        if od_path:
            print(f"DEBUG - Imagen OD encontrada: {od_path}")
            self.od_image, self.od_photo = load_and_display_image(od_path, self.od_img_label, self.images_dir)
            self.od_img_btn.config(state=tk.NORMAL)
        else:
            print(f"DEBUG - No se encontró imagen OD para paciente {patient_id}")
            self.od_img_label.config(text="Imagen no disponible")
            self.od_img_btn.config(state=tk.DISABLED)

            # Intentar usar la ruta almacenada en el objeto paciente como respaldo
            if patient.right_eye and patient.right_eye.fundus_image:
                od_path = patient.right_eye.fundus_image
                print(f"DEBUG - Intentando con ruta desde objeto paciente: {od_path}")
                if os.path.exists(od_path):
                    self.od_image, self.od_photo = load_and_display_image(od_path, self.od_img_label, self.images_dir)
                    self.od_img_btn.config(state=tk.NORMAL)

        # Buscar y cargar imagen OS
        os_path = find_image_for_patient(patient_id, Eye.LEFT, self.images_dir)
        if os_path:
            print(f"DEBUG - Imagen OS encontrada: {os_path}")
            self.os_image, self.os_photo = load_and_display_image(os_path, self.os_img_label, self.images_dir)
            self.os_img_btn.config(state=tk.NORMAL)
        else:
            print(f"DEBUG - No se encontró imagen OS para paciente {patient_id}")
            self.os_img_label.config(text="Imagen no disponible")
            self.os_img_btn.config(state=tk.DISABLED)

            # Intentar usar la ruta almacenada en el objeto paciente como respaldo
            if patient.left_eye and patient.left_eye.fundus_image:
                os_path = patient.left_eye.fundus_image
                print(f"DEBUG - Intentando con ruta desde objeto paciente: {os_path}")
                if os.path.exists(os_path):
                    self.os_image, self.os_photo = load_and_display_image(os_path, self.os_img_label, self.images_dir)
                    self.os_img_btn.config(state=tk.NORMAL)

    def open_image(self, eye_side):
        """Abre la imagen en el visor predeterminado del sistema"""
        patient_id = self.patient_ids[self.current_index]

        # Generar ruta de imagen basada en el ID del paciente
        clean_id = str(patient_id).replace('#', '')
        suffix = "OD" if eye_side == 'od' else "OS"

        # Intentar con formato estándar
        filename = f"RET{clean_id}{suffix}.jpg"
        image_path = os.path.join(self.images_dir, filename)

        # Intentar también sin ceros a la izquierda
        if not os.path.exists(image_path) and clean_id.isdigit():
            numeric_id = int(clean_id)
            filename_alt = f"RET{numeric_id}{suffix}.jpg"
            image_path_alt = os.path.join(self.images_dir, filename_alt)

            if os.path.exists(image_path_alt):
                image_path = image_path_alt

        if os.path.exists(image_path):
            open_external_image(image_path, self.images_dir)
        else:
            messagebox.showwarning("Advertencia", "No hay imagen disponible para abrir")

    def prev_patient(self):
        """Navega al paciente anterior"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_patient_data()

    def next_patient(self):
        """Navega al siguiente paciente"""
        if self.current_index < len(self.patient_ids) - 1:
            self.current_index += 1
            self.display_patient_data()

    def add_patient(self):
        """Abre el formulario para añadir un nuevo paciente"""
        form_window = tk.Toplevel(self.root)
        form_window.title("Añadir Paciente")

        def on_save(patient_data):
            """Callback para guardar el nuevo paciente"""
            try:
                # Crear nuevo paciente
                new_patient = add_patient(patient_data, self.images_dir)

                # Actualizar dataset
                self.dataset.add_patient(new_patient)

                # Actualizar Excel
                from features.data_loading import update_excel_files
                update_excel_files(new_patient, False)

                # Actualizar interfaz
                self.patient_ids = sorted(self.dataset.patients.keys())
                self.current_index = self.patient_ids.index(new_patient.patient_id)
                self.display_patient_data()

                # Actualizar estadísticas
                setup_stats_tab(self.stats_tab, self.dataset)

                messagebox.showinfo("Éxito", "Paciente guardado correctamente")
                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el paciente: {str(e)}")

        create_patient_form(form_window, self.images_dir, on_save=on_save, dataset=self.dataset)

    def edit_patient(self):
        """Edita el paciente actual"""
        if not self.patient_ids:
            messagebox.showwarning("Advertencia", "No hay pacientes para editar")
            return

        patient_id = self.patient_ids[self.current_index]
        patient = self.dataset.patients[patient_id]

        form_window = tk.Toplevel(self.root)
        form_window.title("Editar Paciente")

        def on_save(patient_data):
            """Callback para guardar los cambios del paciente"""
            try:
                # Actualizar paciente
                updated_patient = update_patient(patient_data, patient, self.images_dir)

                # Actualizar dataset
                self.dataset.update_patient(updated_patient)

                # Actualizar Excel
                from features.data_loading import update_excel_files
                update_excel_files(updated_patient, True)

                # Actualizar interfaz
                self.display_patient_data()

                # Actualizar estadísticas
                setup_stats_tab(self.stats_tab, self.dataset)

                messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el paciente: {str(e)}")

        create_patient_form(form_window, self.images_dir, on_save=on_save,
                            edit_mode=True,
                            patient=patient,
                            dataset=self.dataset)

    def delete_patient(self):
        """Elimina el paciente actual"""
        if not self.patient_ids:
            messagebox.showwarning("Advertencia", "No hay pacientes para eliminar")
            return

        patient_id = self.patient_ids[self.current_index]
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar al paciente {patient_id}?"):
            try:
                # Eliminar paciente
                delete_patient(patient_id, self.dataset)

                # Actualizar Excel
                from features.data_loading import delete_from_excel
                delete_from_excel(patient_id)

                # Actualizar interfaz
                self.patient_ids = sorted(self.dataset.patients.keys())

                if self.current_index >= len(self.patient_ids):
                    self.current_index = len(self.patient_ids) - 1

                if self.patient_ids:
                    self.display_patient_data()
                else:
                    self.clear_display()

                # Actualizar estadísticas
                setup_stats_tab(self.stats_tab, self.dataset)

                messagebox.showinfo("Éxito", "Paciente eliminado correctamente")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el paciente: {str(e)}")

    def clear_display(self):
        """Limpia la pantalla cuando no hay pacientes"""
        self.patient_label.config(text="No hay pacientes")

        # Limpiar información general
        for label in self.gen_labels.values():
            label.config(text="")

        # Limpiar información de ojos
        from ui.patient_display import update_eye_data
        update_eye_data(None, self.od_diagnosis_label, self.od_crystalline_label,
                        self.od_ref_labels, self.od_meas_labels)
        update_eye_data(None, self.os_diagnosis_label, self.os_crystalline_label,
                        self.os_ref_labels, self.os_meas_labels)

        # Limpiar imágenes
        self.od_img_label.config(image='', text="Imagen no disponible")
        self.os_img_label.config(image='', text="Imagen no disponible")
        self.od_img_btn.config(state=tk.DISABLED)
        self.os_img_btn.config(state=tk.DISABLED)

        # Deshabilitar botones de navegación
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.edit_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
