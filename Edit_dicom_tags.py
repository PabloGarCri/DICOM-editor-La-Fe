import os
import pydicom
from pydicom.datadict import tag_for_keyword
from pydicom.uid import generate_uid

# --- Carpetas ---
input_folder = "/Users/pablogc/Downloads/CURRO/Medidas/Next La Fe/dcm NEXTMRI_005"  # Carpeta con los archivos originales
output_folder = "dicoms_editados"  # Carpeta donde guardar los archivos editados
os.makedirs(output_folder, exist_ok=True)

# --- Tags a editar según tus especificaciones ---
edit_tags = {
    "Manufacturer": "i3M",
    "StudyID":"Protocolo La Fe",
    "ManufacturerModelName": "NextMRI-II",
    "InstitutionName": "MRILab - I3M - UPV",
    "Model": "NEXTMRI II",
    "Modality": "PORTABLE",
    "OperatorsName": "",
    "SoftwareVersions": "MARGE v0.8.1-35g25a2be1",
    "BodyPartExamined": "BRAIN",
    "PatientName": "NEXTMRI_005 - Portable",
    "PatientID": "NEXTMRI_005 - Portable",
    "PatientSex": "F",
    "PatientWeight": "68",
    "PatientBirthDate": "19940101",
    "SequenceName": "TSE_T2",
    "ScanningSequence": "TSE",
    "SequenceVariant": "FLAIR",
    "ScanOptions": "",
    "PulseSequenceName": "T2_FLAIR",
    "SeriesDescription": "T2-weighted Axial BRAIN FLAIR Portable",
    "ImagingFrequency": "3.63"

}

# --- Procesamiento de los DICOM ---
for fname in os.listdir(input_folder):
    if not fname.lower().endswith(".dcm"):
        continue

    input_path = os.path.join(input_folder, fname)
    output_path = os.path.join(output_folder, fname)

    try:
        ds = pydicom.dcmread(input_path)

        # Editar tags
        for key, value in edit_tags.items():
            try:
                tag = tag_for_keyword(key)
                if tag is None:
                    continue
                if tag in ds:
                    ds[tag].value = value
                else:
                    setattr(ds, key, value)
            except Exception as e:
                print(f"Advertencia al editar {key}: {e}")

        # Generar nuevos UIDs aleatorios (para separar estudios y series)
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.SOPInstanceUID = generate_uid()

        # Guardar
        ds.save_as(output_path)
        print(f"✔ Editado y guardado: {output_path}")

    except Exception as e:
        print(f"❌ Error con {fname}: {e}")

print("\n✅ Edición completa de todos los DICOMs.")

ds = pydicom.dcmread('/Users/pablogc/Downloads/CURRO/Medidas/Next La Fe/dicoms_editados/RareDoubleImage.2025.11.07.14.21.40.302.dcm')
for element in ds:
    print(element)