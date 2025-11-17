import os
import fnmatch
import numpy as np
import pydicom
from pydicom.datadict import tag_for_keyword
from pydicom.uid import generate_uid


# --- Carpetas ---
input_folder = "/home/pablogc/Descargas/Physio II/NextLaFe/dcmjueves1"
output_folder = "/home/pablogc/Descargas/Physio II/NextLaFe/dicoms_editados_jueves1"
os.makedirs(output_folder, exist_ok=True)

# Nombre del paciente = nombre de la carpeta
patient_name = os.path.basename(input_folder)


# -----------------------------------------------------------
#                 TAGS COMUNES A TODAS LAS SERIES
# -----------------------------------------------------------
common_tags = {
    "Manufacturer": "i3M",
    "StudyID": patient_name,
    "PatientName": patient_name,
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


# -----------------------------------------------------------
#            TAGS ESPECÍFICOS DE CADA SECUENCIA
# -----------------------------------------------------------

# --- T1 ---
tags_T1 = {
    "SequenceName": "TSE_T1",
    "ScanningSequence": "TSE",
    "SequenceVariant": "T1W",
    "PulseSequenceName": "T1W",
    "SeriesDescription": "T1-weighted Axial Portable"
}

# --- FLAIR ---
tags_FLAIR = {
    "SequenceName": "TSE_T2",
    "ScanningSequence": "TSE",
    "SequenceVariant": "FLAIR",
    "PulseSequenceName": "T2_FLAIR",
    "SeriesDescription": "T2-weighted Axial BRAIN FLAIR Portable"
}


# --- UIDs por serie ---
series_uid_T1 = generate_uid()
series_uid_FLAIR = generate_uid()


def apply_tags(ds, tags):
    """Aplica correctamente tags respetando VR."""
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
            # Evita crashear por VR incorrecto
            pass


# -----------------------------------------------------------
#                    PROCESAMIENTO PRINCIPAL
# -----------------------------------------------------------
for fname in os.listdir(input_folder):

    if not fname.lower().endswith(".dcm"):
        continue

    input_path = os.path.join(input_folder, fname)
    output_path = os.path.join(output_folder, fname)

    try:
        ds = pydicom.dcmread(input_path)

        # --- Saltar LOCALIZER ---
        if fnmatch.fnmatch(fname.lower(),"*Localizer"):
            print(f"⏭ Saltando Localizer: {fname}")
            continue

        # --- Patient ID/Name automáticos ---
        ds.PatientID = patient_name
        ds.PatientName = patient_name

        # --- Tags comunes ---
        apply_tags(ds, common_tags)

        # --- T1 ------------------------------------------------------
        if fnmatch.fnmatch(fname.lower(), "*t1*"):
            apply_tags(ds, tags_T1)
            ds.SeriesInstanceUID = series_uid_T1

        # --- FLAIR ---------------------------------------------------
        if fnmatch.fnmatch(fname.lower(), "*flair*"):
            apply_tags(ds, tags_FLAIR)
            ds.SeriesInstanceUID = series_uid_FLAIR

            # Flip vertical (arriba-abajo)
            vol = ds.pixel_array
            vol_flipped = np.flip(vol, axis=1)  # eje 1 = vertical
            ds.PixelData = vol_flipped.tobytes()

        # --- Nuevo UID por imagen ---
        ds.SOPInstanceUID = generate_uid()

        # Guardar
        ds.save_as(output_path)
        print(f"✔ Editado y guardado: {fname}")

    except Exception as e:
        print(f"❌ Error en {fname}: {e}")

print("\n✅ Edición completa.")
