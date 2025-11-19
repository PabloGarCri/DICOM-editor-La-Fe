import os
import fnmatch
import numpy as np
import pydicom
from pydicom.datadict import tag_for_keyword
from pydicom.uid import generate_uid

# --- Carpeta padre con todas las sesiones ---
parent_folder = "/Users/pablogc/Downloads/CURRO/Medidas/Next La Fe/dcms jueves-lunes"
output_parent = os.path.join(parent_folder, "dicoms_editados_02")
os.makedirs(output_parent, exist_ok=True)

# --- Resolución por serie ---
resolutions = {
    "T1": {"PixelSpacing": [1.6, 1.6], "SliceThickness": 4.4},
    "FLAIR": {"PixelSpacing": [1.6, 1.6], "SliceThickness": 8.0}
}

# --- Tags comunes ---
common_tags_template = {
    "Manufacturer": "i3M",
    "ManufacturerModelName": "NextMRI-II",
    "InstitutionName": "MRILab - I3M - UPV",
    "Model": "NEXTMRI II",
    "Modality": "PORTABLE",
    "OperatorsName": "",
    "SoftwareVersions": "MARGE v0.8.1-35g25a2be1",
    "BodyPartExamined": "BRAIN",
    "PatientSex": "H",
    "PatientWeight": "80",
    "PatientBirthDate": "19940101",
    "ImagingFrequency": "3.63"
}

# --- Tags específicos ---
tags_T1 = {
    "SequenceName": "TSE_T1",
    "ScanningSequence": "TSE",
    "SequenceVariant": "T1W",
    "PulseSequenceName": "T1W",
    "SeriesDescription": "T1-weighted Axial Portable"
}

tags_FLAIR = {
    "SequenceName": "TSE_T2",
    "ScanningSequence": "TSE",
    "SequenceVariant": "FLAIR",
    "PulseSequenceName": "T2_FLAIR",
    "SeriesDescription": "T2-weighted Axial BRAIN FLAIR Portable"
}

# --- Función para aplicar tags ---
def apply_tags(ds, tags):
    for key, value in tags.items():
        tag = tag_for_keyword(key)
        if tag is None:
            continue
        try:
            if tag in ds:
                ds[tag].value = value
            else:
                setattr(ds, key, value)
        except Exception:
            pass

# --- Procesamiento por carpeta ---
for folder_name in os.listdir(parent_folder):
    input_folder = os.path.join(parent_folder, folder_name)
    if not os.path.isdir(input_folder):
        continue

    output_folder = os.path.join(output_parent, folder_name)
    os.makedirs(output_folder, exist_ok=True)

    # UIDs únicos por paciente/estudio
    study_uid = generate_uid()
    series_uid_T1 = generate_uid()
    series_uid_FLAIR = generate_uid()

    print(f"\n📂 Procesando carpeta/paciente: {folder_name}")

    # Tags comunes
    common_tags = common_tags_template.copy()
    common_tags["PatientID"] = folder_name
    common_tags["PatientName"] = folder_name
    common_tags["StudyID"] = folder_name

    # Recorrer archivos DICOM
    for fname in os.listdir(input_folder):
        if not fname.lower().endswith(".dcm"):
            continue

        input_path = os.path.join(input_folder, fname)
        output_path = os.path.join(output_folder, fname)

        # Saltar Localizer
        if "localizer" in fname.lower():
            print(f"⏭ Saltando Localizer: {fname}")
            continue

        try:
            ds = pydicom.dcmread(input_path)

            # Aplicar tags comunes
            apply_tags(ds, common_tags)

            # Detectar modalidad
            if fnmatch.fnmatch(fname.lower(), "*t1*"):
                apply_tags(ds, tags_T1)
                ds.SeriesInstanceUID = series_uid_T1
                res = resolutions["T1"]

                # Flip de slices (transversal)
                vol = ds.pixel_array
                vol_flipped_slices = np.flip(vol, axis=0)  # eje 0 = slices
                ds.PixelData = vol_flipped_slices.tobytes()

            elif fnmatch.fnmatch(fname.lower(), "*flair*"):
                apply_tags(ds, tags_FLAIR)
                ds.SeriesInstanceUID = series_uid_FLAIR
                res = resolutions["FLAIR"]

                # Flip vertical (arriba-abajo)
                vol = ds.pixel_array
                vol_flipped = np.flip(vol, axis=1)
                ds.PixelData = vol_flipped.tobytes()
            else:
                res = None

            # SOPInstanceUID único
            ds.SOPInstanceUID = generate_uid()
            ds.StudyInstanceUID = study_uid

            # Mantener FOV y orientación
            if res is not None:
                ds.PixelSpacing = res["PixelSpacing"]
                ds.SliceThickness = res["SliceThickness"]
                ds.SpacingBetweenSlices = res["SliceThickness"]  # sin gap

                # NO cambiar Rows/Columns
                # Mantener ImagePositionPatient y ImageOrientationPatient

            # Guardar
            ds.save_as(output_path)
            print(f"✔ Guardado: {fname}")

        except Exception as e:
            print(f"❌ Error en {fname}: {e}")

print("\n✅ Procesamiento completo de todas las carpetas.")
