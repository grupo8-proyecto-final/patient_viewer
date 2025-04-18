import tkinter as tk
from tkinter import ttk, messagebox
import os

# Importaciones internas
from features.data_loading import load_patient_data, load_image_paths
from features.patient_management import add_patient, update_patient, delete_patient
from features.image_handling import load_and_display_image, open_external_image
from ui.patient_form import create_patient_form
from ui.tabs.general_tab import setup_general_tab
from ui.tabs.eye_tab import setup_eye_tab
from ui.tabs.stats_tab import setup_stats_tab

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
        self.od_images = load_image_paths(self.od_excel_file, self.images_dir)
        self.os_images = load_image_paths(self.os_excel_file, self.images_dir)

        self.patient_ids = sorted(self.dataset.patients.keys())
        self.current_index = 0 if self.patient_ids else -1

        # Variables para las imágenes
        self.od_image = None
        self.os_image = None
        self.od_photo = None
        self.os_photo = None

        # Crear la interfaz
        self._create_widgets()

        # Mostrar datos del paciente actual
        if self.patient_ids:
            self.display_patient_data()
        else:
            self.clear_display()

    def _configure_window(self):
        """Configura el tamaño y posición de la ventana"""
        window_width = 1000
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.bind("<Map>", lambda e: self.bring_to_front())

    def bring_to_front(self):
        """Trae la ventana al frente cuando se restaura"""
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        self.root.focus_force()

    def _create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Controles de navegación
        self._create_navigation_controls(main_frame)

        # Frame para datos e imágenes
        data_image_frame = ttk.Frame(main_frame)
        data_image_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook para pestañas
        self.notebook = ttk.Notebook(data_image_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
        self._create_image_frame(data_image_frame)

    def _create_navigation_controls(self, parent):
        """Crea los controles de navegación y acciones"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=5)

        self.prev_btn = ttk.Button(nav_frame, text="< Anterior", command=self.prev_patient)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(nav_frame, text="Siguiente >", command=self.next_patient)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.add_btn = ttk.Button(nav_frame, text="Añadir Paciente", command=self.add_patient)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = ttk.Button(nav_frame, text="Editar Paciente", command=self.edit_patient)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = ttk.Button(nav_frame, text="Eliminar Paciente", command=self.delete_patient)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.patient_label = ttk.Label(nav_frame, text="", font=('Arial', 10, 'bold'))
        self.patient_label.pack(side=tk.LEFT, padx=10)

    def _create_image_frame(self, parent):
        """Crea el frame para mostrar las imágenes de fondo de ojo"""
        image_frame = ttk.LabelFrame(parent, text="Imágenes de Fondo de Ojo", padding="10")
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        # Imagen OD
        od_img_frame = ttk.Frame(image_frame)
        od_img_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(od_img_frame, text="Ojo Derecho (OD)", font=('Arial', 10, 'bold')).pack()
        self.od_img_label = ttk.Label(od_img_frame)
        self.od_img_label.pack(fill=tk.BOTH, expand=True)
        self.od_img_btn = ttk.Button(od_img_frame, text="Abrir Imagen", command=lambda: self.open_image('od'))
        self.od_img_btn.pack(pady=5)

        # Imagen OS
        os_img_frame = ttk.Frame(image_frame)
        os_img_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(os_img_frame, text="Ojo Izquierdo (OS)", font=('Arial', 10, 'bold')).pack()
        self.os_img_label = ttk.Label(os_img_frame)
        self.os_img_label.pack(fill=tk.BOTH, expand=True)
        self.os_img_btn = ttk.Button(os_img_frame, text="Abrir Imagen", command=lambda: self.open_image('os'))
        self.os_img_btn.pack(pady=5)

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

    def update_images(self, patient_id):
        """Actualiza las imágenes de fondo de ojo para el paciente actual"""
        # Limpiar imágenes previas
        self.od_img_label.config(image='')
        self.os_img_label.config(image='')
        self.od_photo = None
        self.os_photo = None

        # Cargar imagen OD
        od_path = self.od_images.get(patient_id)
        if od_path and isinstance(od_path, str):
            self.od_image, self.od_photo = load_and_display_image(od_path, self.od_img_label, self.images_dir)
            self.od_img_btn.config(state=tk.NORMAL)
        else:
            self.od_img_label.config(text="Imagen no disponible")
            self.od_img_btn.config(state=tk.DISABLED)

        # Cargar imagen OS
        os_path = self.os_images.get(patient_id)
        if os_path and isinstance(os_path, str):
            self.os_image, self.os_photo = load_and_display_image(os_path, self.os_img_label, self.images_dir)
            self.os_img_btn.config(state=tk.NORMAL)
        else:
            self.os_img_label.config(text="Imagen no disponible")
            self.os_img_btn.config(state=tk.DISABLED)

    def open_image(self, eye_side):
        """Abre la imagen en el visor predeterminado del sistema"""
        patient_id = self.patient_ids[self.current_index]
        image_path = self.od_images.get(patient_id) if eye_side == 'od' else self.os_images.get(patient_id)
        open_external_image(image_path, self.images_dir)

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

                # Actualizar listado de imágenes
                self.od_images = load_image_paths("patient_data_od.xlsx", self.images_dir)
                self.os_images = load_image_paths("patient_data_os.xlsx", self.images_dir)

                messagebox.showinfo("Éxito", "Paciente guardado correctamente")
                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el paciente: {str(e)}")

        create_patient_form(form_window, self.images_dir, on_save=on_save)

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

                # Actualizar listado de imágenes
                self.od_images = load_image_paths("patient_data_od.xlsx", self.images_dir)
                self.os_images = load_image_paths("patient_data_os.xlsx", self.images_dir)

                messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
                form_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el paciente: {str(e)}")

        create_patient_form(form_window, self.images_dir, on_save=on_save, edit_mode=True, patient=patient)

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

                # Actualizar listado de imágenes
                self.od_images = load_image_paths("patient_data_od.xlsx", self.images_dir)
                self.os_images = load_image_paths("patient_data_os.xlsx", self.images_dir)

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
