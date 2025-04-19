import pandas as pd
from enum import Enum
from dotenv import load_dotenv
import os

# === Cargar variable de entorno ===
load_dotenv()
archivo = os.getenv("OS_EXCEL_FILE")  # <- usa la variable definida por el equipo
if not archivo:
    raise EnvironmentError("❌ No se encontró OS_EXCEL_FILE en el archivo .env")

# === Enumeraciones ===
class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class DiagnosisStatus(Enum):
    HEALTHY = 0
    GLAUCOMA = 1
    SUSPECT = 2

# === Clases auxiliares ===
class RefractiveError:
    def __init__(self, sphere, cylinder=0.0, axis=0.0):
        self.sphere = sphere
        self.cylinder = cylinder
        self.axis = axis

class EyeData:
    def __init__(self):
        self.diagnosis = None
        self.refractive_error = None
        self.pneumatic_iop = None
        self.perkins_iop = None
        self.pachymetry = None
        self.axial_length = None
        self.mean_defect = None

class Patient:
    def __init__(self, patient_id, age, gender, right_eye, left_eye):
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.right_eye = right_eye
        self.left_eye = left_eye

# === Dataset principal ===
class PapilaDataset:
    def __init__(self):
        self.patients = {}

    def load_from_excel(self, path):
        df = pd.read_excel(path, header=2, index_col=None)
        df.columns = df.columns.str.strip()

        if "Unnamed: 0" in df.columns:
            df.rename(columns={"Unnamed: 0": "ID"}, inplace=True)

        print("🧾 Columnas detectadas:", df.columns.tolist())

        if "ID" not in df.columns:
            raise ValueError("❌ La columna 'ID' no se encontró. Verifica el encabezado del archivo Excel.")

        # Eliminar filas vacías o incompletas
        df = df.dropna(subset=["ID", "Age", "Gender", "Diagnosis"])

        for _, row in df.iterrows():
            patient_id = row["ID"]
            age = int(row["Age"])
            gender = Gender.MALE if row["Gender"] == 0 else Gender.FEMALE
            diagnosis = DiagnosisStatus(row["Diagnosis"])

            right_eye = EyeData()
            right_eye.diagnosis = diagnosis
            right_eye.refractive_error = RefractiveError(
                sphere=float(row.get("dioptre_1", 0))
            )
            right_eye.pneumatic_iop = row.get("Pneumatic")
            right_eye.perkins_iop = row.get("Perkins")
            right_eye.pachymetry = row.get("Pachymetry")
            right_eye.axial_length = row.get("Axial_Length")
            right_eye.mean_defect = row.get("VF_MD")

            left_eye = EyeData()
            left_eye.diagnosis = diagnosis

            self.patients[patient_id] = Patient(patient_id, age, gender, right_eye, left_eye)

    def get_patient(self, pid):
        pid_normalizado = str(pid).strip()
        for key in self.patients:
            if str(key).strip() == pid_normalizado:
                return self.patients[key]
        return None

    def add_patient(self, patient):
        self.patients[patient.patient_id] = patient

    def remove_patient(self, pid):
        if pid in self.patients:
            del self.patients[pid]

    def list_patients(self):
        for pid, patient in self.patients.items():
            print(f"ID: {pid}, Edad: {patient.age}, Género: {patient.gender.name}")

    def to_dataframe(self):
        data = []
        for p in self.patients.values():
            data.append({
                "ID": p.patient_id,
                "Age": p.age,
                "Gender": 0 if p.gender == Gender.MALE else 1,
                "Diagnosis": p.right_eye.diagnosis.value,
                "dioptre_1": p.right_eye.refractive_error.sphere,
                "Pneumatic": p.right_eye.pneumatic_iop,
                "Perkins": p.right_eye.perkins_iop,
                "Pachymetry": p.right_eye.pachymetry,
                "Axial_Length": p.right_eye.axial_length,
                "VF_MD": p.right_eye.mean_defect
            })
        return pd.DataFrame(data)

# === Gestor del Menú ===
class GestorPacientes:
    def __init__(self, archivo):
        self.archivo = archivo
        self.dataset = PapilaDataset()
        self.dataset.load_from_excel(archivo)

    def mostrar_menu(self):
        print("\n--- MENÚ ---")
        print("1. Ver pacientes")
        print("2. Agregar paciente")
        print("3. Ver paciente")
        print("4. Eliminar paciente")
        print("5. Guardar y salir")

    def ver_pacientes(self):
        self.dataset.list_patients()

    def ver_paciente(self):
        pid = input("ID del paciente: ").strip()
        paciente = self.dataset.get_patient(pid)
        if paciente:
            print(f"\nID: {paciente.patient_id}")
            print(f"Edad: {paciente.age}")
            print(f"Género: {paciente.gender.name}")
            print(f"Diagnóstico: {paciente.right_eye.diagnosis.name}")
            print(f"dioptre_1: {paciente.right_eye.refractive_error.sphere}")
            print(f"VF_MD: {paciente.right_eye.mean_defect}")
        else:
            print("❌ Paciente no encontrado.")

    def agregar_paciente(self):
        print("Agregar nuevo paciente")
        pid = input("ID: ")
        edad = int(input("Edad: "))
        genero = input("Género (MALE/FEMALE): ").upper()
        gender_enum = Gender[genero]

        diagnosis_input = int(input("Diagnóstico (0=HEALTHY, 1=GLAUCOMA, 2=SUSPECT): "))
        diagnosis = DiagnosisStatus(diagnosis_input)

        ojo_derecho = EyeData()
        ojo_derecho.diagnosis = diagnosis
        ojo_derecho.refractive_error = RefractiveError(
            sphere=float(input("dioptre_1 (esfera): "))
        )
        ojo_derecho.pneumatic_iop = float(input("IOP Neumático: "))
        ojo_derecho.perkins_iop = float(input("IOP Perkins: "))
        ojo_derecho.pachymetry = float(input("Pachymetry: "))
        ojo_derecho.axial_length = float(input("Axial length: "))
        ojo_derecho.mean_defect = float(input("VF_MD: "))

        ojo_izquierdo = EyeData()
        ojo_izquierdo.diagnosis = diagnosis

        nuevo_paciente = Patient(pid, edad, gender_enum, ojo_derecho, ojo_izquierdo)
        self.dataset.add_patient(nuevo_paciente)
        print("✅ Paciente agregado.")

    def eliminar_paciente(self):
        pid = input("ID del paciente a eliminar: ")
        self.dataset.remove_patient(pid)
        print("✅ Paciente eliminado.")

    def guardar(self):
        df = self.dataset.to_dataframe()
        output_path = self.archivo.replace(".xlsx", "_actualizado.xlsx")
        df.to_excel(output_path, index=False)
        print(f"✅ Datos guardados en {output_path}")

    def ejecutar(self):
        while True:
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
                break
            else:
                print("❌ Opción inválida.")

# === EJECUCIÓN PRINCIPAL ===
if __name__ == "__main__":
    app = GestorPacientes(archivo)
    app.ejecutar()
