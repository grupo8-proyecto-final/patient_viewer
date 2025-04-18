import os
from enum import Enum
from typing import List, Dict, Optional, Any


class Gender(Enum):
    MALE = 0
    FEMALE = 1


class DiagnosisStatus(Enum):
    HEALTHY = 0
    GLAUCOMA = 1
    SUSPECT = 2


class Eye(Enum):
    RIGHT = "OD"
    LEFT = "OS"


class CrystallineStatus(Enum):
    PHAKIC = 0
    PSEUDOPHAKIC = 1


class RefractiveError:
    def __init__(self, sphere: float, cylinder: Optional[float] = None, axis: Optional[float] = None):
        self.sphere = sphere
        self.cylinder = cylinder
        self.axis = axis

    def __str__(self) -> str:
        if self.cylinder is not None and self.axis is not None:
            return f"Sphere: {self.sphere}, Cylinder: {self.cylinder}, Axis: {self.axis}°"
        return f"Sphere: {self.sphere}"


class EyeData:
    def __init__(
            self,
            eye_type: Eye,
            diagnosis: DiagnosisStatus,
            refractive_error: Optional[RefractiveError] = None,
            crystalline_status: Optional[CrystallineStatus] = None,
            pneumatic_iop: Optional[float] = None,
            perkins_iop: Optional[float] = None,
            pachymetry: Optional[float] = None,
            axial_length: Optional[float] = None,
            mean_defect: Optional[float] = None
    ):
        self.eye_type = eye_type
        self.diagnosis = diagnosis
        self.refractive_error = refractive_error
        self.crystalline_status = crystalline_status
        self.pneumatic_iop = pneumatic_iop
        self.perkins_iop = perkins_iop
        self.pachymetry = pachymetry
        self.axial_length = axial_length
        self.mean_defect = mean_defect

        self.fundus_image: Optional[str] = None

    def add_fundus_image(self, image_path: str) -> None:
        if os.path.exists(image_path):
            self.fundus_image = image_path
        else:
            raise FileNotFoundError(f"La imagen {image_path} no existe")

    def get_glaucoma_severity(self) -> Optional[str]:
        if self.mean_defect is None or self.diagnosis != DiagnosisStatus.GLAUCOMA:
            return None

        if -6 <= self.mean_defect < -3:
            return "Glaucoma Leve"
        elif -12 <= self.mean_defect < -6:
            return "Glaucoma Moderado"
        elif self.mean_defect < -12:
            return "Glaucoma Severo"
        else:
            return "No clasificable"


class Patient:
    def __init__(
            self,
            patient_id: str,
            age: int,
            gender: Gender,
            right_eye: Optional[EyeData] = None,
            left_eye: Optional[EyeData] = None
    ):
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.right_eye = right_eye
        self.left_eye = left_eye

    def set_eye_data(self, eye_data: EyeData) -> None:
        if eye_data.eye_type == Eye.RIGHT:
            self.right_eye = eye_data
        elif eye_data.eye_type == Eye.LEFT:
            self.left_eye = eye_data
        else:
            raise ValueError("El tipo de ojo debe ser RIGHT o LEFT")

    def get_patient_diagnosis(self) -> str:
        if not self.right_eye and not self.left_eye:
            return "Sin datos"

        if (self.right_eye and self.right_eye.diagnosis == DiagnosisStatus.GLAUCOMA) or \
                (self.left_eye and self.left_eye.diagnosis == DiagnosisStatus.GLAUCOMA):
            return "Glaucoma"

        if (self.right_eye and self.right_eye.diagnosis == DiagnosisStatus.SUSPECT) or \
                (self.left_eye and self.left_eye.diagnosis == DiagnosisStatus.SUSPECT):
            return "Sospechoso"

        return "Sano"


class PapilaDataset:
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.base_dir: Optional[str] = None

    def set_base_directory(self, directory: str) -> None:
        if os.path.isdir(directory):
            self.base_dir = directory
        else:
            raise NotADirectoryError(f"El directorio {directory} no existe")

    def add_patient(self, patient: Patient) -> None:
        self.patients[patient.patient_id] = patient

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        return self.patients.get(patient_id)

    def update_patient(self, patient: Patient) -> None:
        """Actualiza un paciente existente en el dataset."""
        if patient.patient_id not in self.patients:
            raise ValueError(f"El paciente con ID {patient.patient_id} no existe en el dataset")
        self.patients[patient.patient_id] = patient

    def remove_patient(self, patient_id: str) -> bool:
        if patient_id in self.patients:
            del self.patients[patient_id]
            return True
        return False

    def load_from_csv(self, od_file: str, os_file: str) -> None:
        pass

    def load_images(self, directory: str) -> None:
        pass

    def filter_patients(self, **kwargs) -> List[Patient]:
        filtered_patients = list(self.patients.values())

        for key, value in kwargs.items():
            if key == 'age_min':
                filtered_patients = [p for p in filtered_patients if p.age >= value]
            elif key == 'age_max':
                filtered_patients = [p for p in filtered_patients if p.age <= value]
            elif key == 'gender':
                filtered_patients = [p for p in filtered_patients if p.gender == value]
            elif key == 'diagnosis':
                filtered_patients = [p for p in filtered_patients
                                     if (p.right_eye and p.right_eye.diagnosis == value) or
                                     (p.left_eye and p.left_eye.diagnosis == value)]

        return filtered_patients

    def get_statistics(self) -> Dict[str, Any]:
        stats = {
            "total_patients": len(self.patients),
            "gender_distribution": {
                "male": sum(1 for p in self.patients.values() if p.gender == Gender.MALE),
                "female": sum(1 for p in self.patients.values() if p.gender == Gender.FEMALE)
            },
            "diagnosis_distribution": {
                "healthy": 0,
                "glaucoma": 0,
                "suspect": 0,
                "mixed": 0
            },
            "age_stats": {
                "min": float('inf') if self.patients else 0,
                "max": float('-inf') if self.patients else 0,
                "avg": 0
            }
        }

        # Manejar caso cuando no hay pacientes
        if not self.patients:
            return stats

        total_age = 0
        for patient in self.patients.values():
            total_age += patient.age
            stats["age_stats"]["min"] = min(stats["age_stats"]["min"], patient.age)
            stats["age_stats"]["max"] = max(stats["age_stats"]["max"], patient.age)

            right_diagnosis = patient.right_eye.diagnosis if patient.right_eye else None
            left_diagnosis = patient.left_eye.diagnosis if patient.left_eye else None

            if right_diagnosis == left_diagnosis:
                if right_diagnosis == DiagnosisStatus.HEALTHY:
                    stats["diagnosis_distribution"]["healthy"] += 1
                elif right_diagnosis == DiagnosisStatus.GLAUCOMA:
                    stats["diagnosis_distribution"]["glaucoma"] += 1
                elif right_diagnosis == DiagnosisStatus.SUSPECT:
                    stats["diagnosis_distribution"]["suspect"] += 1
            else:
                stats["diagnosis_distribution"]["mixed"] += 1

        if self.patients:
            stats["age_stats"]["avg"] = total_age / len(self.patients)

        return stats