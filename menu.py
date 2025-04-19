import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

# Importar las clases desde models.py
from core.models import (
    Gender, DiagnosisStatus, Eye, CrystallineStatus,
    RefractiveError, EyeData, Patient, PapilaDataset
)

# === Cargar variables de entorno ===
load_dotenv()
od_excel_file = os.getenv("OD_EXCEL_FILE", "patient_data_od.xlsx")
os_excel_file = os.getenv("OS_EXCEL_FILE", "patient_data_os.xlsx")
fundus_images_dir = os.getenv("FUNDUS_IMAGES_DIR", "FundusImages")

if not os_excel_file or not od_excel_file:
    raise EnvironmentError("❌ No se encontraron las variables OD_EXCEL_FILE y/o OS_EXCEL_FILE en el archivo .env")


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia los encabezados del DataFrame."""
    df.columns = df.columns.str.lower().str.strip()

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

    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    if len(df) > 0:
        df = df.drop(0, errors='ignore')

    return df


# === Gestor del Menú ===
class GestorPacientes:
    def __init__(self, od_file, os_file):
        self.od_file = od_file
        self.os_file = os_file
        self.dataset = PapilaDataset()
        self._load_data()

    def _load_data(self):
        """Carga los datos de pacientes desde los archivos Excel."""
        try:
            # Cargar datos de OD
            od_df = pd.read_excel(self.od_file, header=0)
            od_df = clean_headers(od_df)

            # Cargar datos de OS
            os_df = pd.read_excel(self.os_file, header=0)
            os_df = clean_headers(os_df)

            print("🧾 Columnas OD:", od_df.columns.tolist())
            print("🧾 Columnas OS:", os_df.columns.tolist())

            # Obtener IDs únicos de pacientes
            patient_ids = set(od_df['patient_id'].tolist() + os_df['patient_id'].tolist())
            print(f"👥 Pacientes encontrados: {len(patient_ids)}")

            # Procesar cada paciente
            for patient_id in patient_ids:
                # Obtener datos OD
                od_data = od_df[od_df['patient_id'] == patient_id]
                # Obtener datos OS
                os_data = os_df[os_df['patient_id'] == patient_id]

                # Si hay datos del paciente
                if not od_data.empty or not os_data.empty:
                    # Tomar la primera fila para datos generales
                    patient_row = od_data.iloc[0] if not od_data.empty else os_data.iloc[0]

                    # Crear paciente
                    age = int(patient_row['age']) if not pd.isna(patient_row['age']) else 0
                    gender = Gender(int(patient_row['gender'])) if not pd.isna(patient_row['gender']) else Gender.MALE
                    patient = Patient(str(patient_id), age, gender)

                    # Procesar ojo derecho
                    if not od_data.empty and not pd.isna(od_data.iloc[0]['diagnosis']):
                        row = od_data.iloc[0]

                        # Crear error refractivo
                        refractive_error = None
                        if not pd.isna(row.get('sphere')):
                            refractive_error = RefractiveError(
                                sphere=float(row['sphere']),
                                cylinder=float(row['cylinder']) if 'cylinder' in row and not pd.isna(
                                    row['cylinder']) else None,
                                axis=float(row['axis']) if 'axis' in row and not pd.isna(row['axis']) else None
                            )

                        # Crear objeto EyeData
                        right_eye = EyeData(
                            eye_type=Eye.RIGHT,
                            diagnosis=DiagnosisStatus(int(row['diagnosis'])),
                            refractive_error=refractive_error,
                            crystalline_status=CrystallineStatus(
                                int(row['crystalline_status'])) if 'crystalline_status' in row and not pd.isna(
                                row['crystalline_status']) else None,
                            pneumatic_iop=float(row['pneumatic_iop']) if 'pneumatic_iop' in row and not pd.isna(
                                row['pneumatic_iop']) else None,
                            perkins_iop=float(row['perkins_iop']) if 'perkins_iop' in row and not pd.isna(
                                row['perkins_iop']) else None,
                            pachymetry=float(row['pachymetry']) if 'pachymetry' in row and not pd.isna(
                                row['pachymetry']) else None,
                            axial_length=float(row['axial_length']) if 'axial_length' in row and not pd.isna(
                                row['axial_length']) else None,
                            mean_defect=float(row['mean_defect']) if 'mean_defect' in row and not pd.isna(
                                row['mean_defect']) else None
                        )

                        # Intentar agregar imagen de fondo de ojo
                        try:
                            image_filename = f"RET{str(row['patient_id']).replace('#', '')}OD.jpg"
                            image_path = os.path.join(fundus_images_dir, image_filename)
                            if os.path.exists(image_path):
                                right_eye.add_fundus_image(image_path)
                        except:
                            pass

                        patient.set_eye_data(right_eye)

                    # Procesar ojo izquierdo
                    if not os_data.empty and not pd.isna(os_data.iloc[0]['diagnosis']):
                        row = os_data.iloc[0]

                        # Crear error refractivo
                        refractive_error = None
                        if not pd.isna(row.get('sphere')):
                            refractive_error = RefractiveError(
                                sphere=float(row['sphere']),
                                cylinder=float(row['cylinder']) if 'cylinder' in row and not pd.isna(
                                    row['cylinder']) else None,
                                axis=float(row['axis']) if 'axis' in row and not pd.isna(row['axis']) else None
                            )

                        # Crear objeto EyeData
                        left_eye = EyeData(
                            eye_type=Eye.LEFT,
                            diagnosis=DiagnosisStatus(int(row['diagnosis'])),
                            refractive_error=refractive_error,
                            crystalline_status=CrystallineStatus(
                                int(row['crystalline_status'])) if 'crystalline_status' in row and not pd.isna(
                                row['crystalline_status']) else None,
                            pneumatic_iop=float(row['pneumatic_iop']) if 'pneumatic_iop' in row and not pd.isna(
                                row['pneumatic_iop']) else None,
                            perkins_iop=float(row['perkins_iop']) if 'perkins_iop' in row and not pd.isna(
                                row['perkins_iop']) else None,
                            pachymetry=float(row['pachymetry']) if 'pachymetry' in row and not pd.isna(
                                row['pachymetry']) else None,
                            axial_length=float(row['axial_length']) if 'axial_length' in row and not pd.isna(
                                row['axial_length']) else None,
                            mean_defect=float(row['mean_defect']) if 'mean_defect' in row and not pd.isna(
                                row['mean_defect']) else None
                        )

                        # Intentar agregar imagen de fondo de ojo
                        try:
                            image_filename = f"RET{str(row['patient_id']).replace('#', '')}OS.jpg"
                            image_path = os.path.join(fundus_images_dir, image_filename)
                            if os.path.exists(image_path):
                                left_eye.add_fundus_image(image_path)
                        except:
                            pass

                        patient.set_eye_data(left_eye)

                    # Añadir paciente al dataset
                    self.dataset.add_patient(patient)

            print(f"✅ Se cargaron {len(self.dataset.patients)} pacientes correctamente.")

        except Exception as e:
            print(f"❌ Error al cargar datos: {str(e)}")
            raise

    def mostrar_menu(self):
        print("\n--- MENÚ ---")
        print("1. Ver pacientes")
        print("2. Agregar paciente")
        print("3. Ver paciente")
        print("4. Eliminar paciente")
        print("5. Guardar y salir")

    def ver_pacientes(self):
        if not self.dataset.patients:
            print("❌ No hay pacientes en el dataset.")
            return

        for pid, patient in self.dataset.patients.items():
            od_diagnosis = patient.right_eye.diagnosis.name if patient.right_eye else "N/A"
            os_diagnosis = patient.left_eye.diagnosis.name if patient.left_eye else "N/A"
            print(
                f"ID: {pid}, Edad: {patient.age}, Género: {patient.gender.name}, Diagnóstico: {patient.get_patient_diagnosis()}")

    def ver_paciente(self):
        pid = input("ID del paciente: ").strip()
        paciente = self.dataset.get_patient(pid)
        if paciente:
            print(f"\nID: {paciente.patient_id}")
            print(f"Edad: {paciente.age}")
            print(f"Género: {paciente.gender.name}")
            print(f"Diagnóstico general: {paciente.get_patient_diagnosis()}")

            if paciente.right_eye:
                print("\n=== Ojo Derecho ===")
                print(f"Diagnóstico: {paciente.right_eye.diagnosis.name}")

                if paciente.right_eye.refractive_error:
                    print(f"Error refractivo: {paciente.right_eye.refractive_error}")

                print(f"IOP Neumático: {paciente.right_eye.pneumatic_iop}")
                print(f"IOP Perkins: {paciente.right_eye.perkins_iop}")
                print(f"Paquimetría: {paciente.right_eye.pachymetry}")
                print(f"Longitud Axial: {paciente.right_eye.axial_length}")
                print(f"Defecto Medio: {paciente.right_eye.mean_defect}")

                if paciente.right_eye.fundus_image:
                    print(f"Imagen: {paciente.right_eye.fundus_image}")

            if paciente.left_eye:
                print("\n=== Ojo Izquierdo ===")
                print(f"Diagnóstico: {paciente.left_eye.diagnosis.name}")

                if paciente.left_eye.refractive_error:
                    print(f"Error refractivo: {paciente.left_eye.refractive_error}")

                print(f"IOP Neumático: {paciente.left_eye.pneumatic_iop}")
                print(f"IOP Perkins: {paciente.left_eye.perkins_iop}")
                print(f"Paquimetría: {paciente.left_eye.pachymetry}")
                print(f"Longitud Axial: {paciente.left_eye.axial_length}")
                print(f"Defecto Medio: {paciente.left_eye.mean_defect}")

                if paciente.left_eye.fundus_image:
                    print(f"Imagen: {paciente.left_eye.fundus_image}")
        else:
            print("❌ Paciente no encontrado.")

    def agregar_paciente(self):
        print("Agregar nuevo paciente")
        pid = input("ID: ")

        try:
            edad = int(input("Edad: "))
        except ValueError:
            print("❌ La edad debe ser un número entero.")
            return

        genero_input = input("Género (0=Hombre, 1=Mujer): ").strip()
        try:
            gender_enum = Gender(int(genero_input))
        except (ValueError, IndexError):
            print("❌ Género inválido. Debe ser 0 (Hombre) o 1 (Mujer).")
            return

        # Crear paciente
        nuevo_paciente = Patient(pid, edad, gender_enum)

        # Datos del ojo derecho
        print("\n=== Datos del ojo derecho ===")
        try:
            diagnosis_input = int(input("Diagnóstico (0=HEALTHY, 1=GLAUCOMA, 2=SUSPECT): "))
            diagnosis = DiagnosisStatus(diagnosis_input)

            sphere = float(input("Esfera: "))
            cylinder = float(input("Cilindro (0 si no aplica): ") or 0)
            axis = float(input("Eje (0 si no aplica): ") or 0)

            refractive_error = RefractiveError(sphere, cylinder, axis)

            pneumatic_iop = float(input("IOP Neumático: "))
            perkins_iop = float(input("IOP Perkins: "))
            pachymetry = float(input("Paquimetría: "))
            axial_length = float(input("Longitud Axial: "))
            mean_defect = float(input("Defecto Medio: "))

            # Crear EyeData para ojo derecho
            right_eye = EyeData(
                eye_type=Eye.RIGHT,
                diagnosis=diagnosis,
                refractive_error=refractive_error,
                pneumatic_iop=pneumatic_iop,
                perkins_iop=perkins_iop,
                pachymetry=pachymetry,
                axial_length=axial_length,
                mean_defect=mean_defect
            )

            nuevo_paciente.set_eye_data(right_eye)

        except ValueError as e:
            print(f"❌ Error en los datos del ojo derecho: {str(e)}")
            print("Se creará el paciente sin datos del ojo derecho.")

        # Datos del ojo izquierdo
        print("\n=== Datos del ojo izquierdo ===")
        try:
            if input("¿Desea agregar datos del ojo izquierdo? (s/n): ").lower().startswith('s'):
                diagnosis_input = int(input("Diagnóstico (0=HEALTHY, 1=GLAUCOMA, 2=SUSPECT): "))
                diagnosis = DiagnosisStatus(diagnosis_input)

                sphere = float(input("Esfera: "))
                cylinder = float(input("Cilindro (0 si no aplica): ") or 0)
                axis = float(input("Eje (0 si no aplica): ") or 0)

                refractive_error = RefractiveError(sphere, cylinder, axis)

                pneumatic_iop = float(input("IOP Neumático: "))
                perkins_iop = float(input("IOP Perkins: "))
                pachymetry = float(input("Paquimetría: "))
                axial_length = float(input("Longitud Axial: "))
                mean_defect = float(input("Defecto Medio: "))

                # Crear EyeData para ojo izquierdo
                left_eye = EyeData(
                    eye_type=Eye.LEFT,
                    diagnosis=diagnosis,
                    refractive_error=refractive_error,
                    pneumatic_iop=pneumatic_iop,
                    perkins_iop=perkins_iop,
                    pachymetry=pachymetry,
                    axial_length=axial_length,
                    mean_defect=mean_defect
                )

                nuevo_paciente.set_eye_data(left_eye)
        except ValueError as e:
            print(f"❌ Error en los datos del ojo izquierdo: {str(e)}")
            print("Se creará el paciente sin datos del ojo izquierdo.")

        # Agregar paciente al dataset
        self.dataset.add_patient(nuevo_paciente)
        print("✅ Paciente agregado.")

    def eliminar_paciente(self):
        pid = input("ID del paciente a eliminar: ")
        if self.dataset.remove_patient(pid):
            print("✅ Paciente eliminado.")
        else:
            print("❌ Paciente no encontrado.")

    def guardar(self):
        try:
            # Preparar DataFrames para OD y OS
            od_data = []
            os_data = []

            for patient_id, patient in self.dataset.patients.items():
                # Datos comunes
                common_data = {
                    'patient_id': patient.patient_id,
                    'age': patient.age,
                    'gender': patient.gender.value,
                }

                # Datos del ojo derecho
                if patient.right_eye:
                    od_row = common_data.copy()
                    od_row['diagnosis'] = patient.right_eye.diagnosis.value

                    # Error refractivo
                    if patient.right_eye.refractive_error:
                        od_row['sphere'] = patient.right_eye.refractive_error.sphere
                        od_row['cylinder'] = patient.right_eye.refractive_error.cylinder
                        od_row['axis'] = patient.right_eye.refractive_error.axis

                    # Estado del cristalino
                    if patient.right_eye.crystalline_status:
                        od_row['crystalline_status'] = patient.right_eye.crystalline_status.value

                    # Mediciones
                    for field in ['pneumatic_iop', 'perkins_iop', 'pachymetry', 'axial_length', 'mean_defect']:
                        value = getattr(patient.right_eye, field)
                        if value is not None:
                            od_row[field] = value

                    od_data.append(od_row)

                # Datos del ojo izquierdo
                if patient.left_eye:
                    os_row = common_data.copy()
                    os_row['diagnosis'] = patient.left_eye.diagnosis.value

                    # Error refractivo
                    if patient.left_eye.refractive_error:
                        os_row['sphere'] = patient.left_eye.refractive_error.sphere
                        os_row['cylinder'] = patient.left_eye.refractive_error.cylinder
                        os_row['axis'] = patient.left_eye.refractive_error.axis

                    # Estado del cristalino
                    if patient.left_eye.crystalline_status:
                        os_row['crystalline_status'] = patient.left_eye.crystalline_status.value

                    # Mediciones
                    for field in ['pneumatic_iop', 'perkins_iop', 'pachymetry', 'axial_length', 'mean_defect']:
                        value = getattr(patient.left_eye, field)
                        if value is not None:
                            os_row[field] = value

                    os_data.append(os_row)

            # Crear DataFrames
            od_df = pd.DataFrame(od_data)
            os_df = pd.DataFrame(os_data)

            # Definir rutas de salida
            od_output = self.od_file.replace(".xlsx", "_actualizado.xlsx")
            os_output = self.os_file.replace(".xlsx", "_actualizado.xlsx")

            # Guardar archivos
            od_df.to_excel(od_output, index=False)
            os_df.to_excel(os_output, index=False)

            print(f"✅ Datos guardados en:")
            print(f"   - Ojo derecho: {od_output}")
            print(f"   - Ojo izquierdo: {os_output}")

        except Exception as e:
            print(f"❌ Error al guardar datos: {str(e)}")

    def ejecutar(self):
        print("\n🏥 SISTEMA DE GESTIÓN DE PACIENTES 🏥")

        while True:
            try:
                self.mostrar_menu()
                opcion = input("Seleccione una opción (1-5): ")

                if opcion == "1":
                    self.ver_pacientes()
                elif opcion == "2":
                    self.agregar_paciente()
                elif opcion == "3":
                    self.ver_paciente()
                elif opcion == "4":
                    self.eliminar_paciente()
                elif opcion == "5":
                    self.guardar()
                    print("\n👋 ¡Hasta pronto!")
                    break
                else:
                    print("❌ Opción inválida.")

                input("\nPresione Enter para continuar...")
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
                input("Presione Enter para continuar...")


# === EJECUCIÓN PRINCIPAL ===
if __name__ == "__main__":
    try:
        app = GestorPacientes(od_excel_file, os_excel_file)
        app.ejecutar()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
        print("\nAsegúrese de que:")
        print("1. El archivo .env está configurado correctamente")
        print("2. Los archivos Excel existen y son accesibles")
        print("3. Los archivos Excel tienen el formato esperado")
