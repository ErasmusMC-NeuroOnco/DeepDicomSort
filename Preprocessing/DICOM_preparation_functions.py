import pydicom
import os
import shutil
from pydicom.errors import InvalidDicomError
import numpy as np


def sort_DICOM_to_structured_folders(root_dir, move_files=False, make_date_folder=False):
    # Given a folder (with possible nested subfolders) of DICOMS, this function will sort all dicoms
    # Into a subject folders, based on modality, date and sequence
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    output_dir = os.path.join(base_dir, 'DICOM_STRUCTURED')

    # Set to True to move files instead of copy
    move_files = False

    # Set to True to use date folders below subject folders, otherwise sequences will be placed directly underneath subject folder
    make_date_folder = False

    # To keep files seperate from following functions place in specific folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(root_dir):
        # Check if there actually are any files in current folder
        if len(files) > 0:
            for i_file_name in files:
                try:
                    # Try, so that only dicom files get moved (pydicom will give an error otherwise)
                    full_file_path = os.path.join(root, i_file_name)
                    dicom_data = pydicom.read_file(full_file_path)

                    patient_ID = dicom_data.PatientID
                    study_date = dicom_data.StudyDate
                    scan_modality = dicom_data.Modality
                    series_instance_UID = dicom_data.SeriesInstanceUID

                    if make_date_folder:
                        dicom_output_folder = os.path.join(output_dir, patient_ID,
                                                           study_date, scan_modality, series_instance_UID)
                    else:
                        dicom_output_folder = os.path.join(output_dir, patient_ID,
                                                           scan_modality, series_instance_UID)

                    if not os.path.exists(dicom_output_folder):
                        os.makedirs(dicom_output_folder)

                    if move_files:
                        shutil.move(full_file_path, dicom_output_folder)
                    else:
                        shutil.copy(full_file_path, dicom_output_folder)
                except InvalidDicomError:
                    pass
    return output_dir


def make_filepaths_safe_for_linux(root_dir):
    # Rename everythinng so no more spaces in names
    # Spaces can trip up multiple tools
    for root, dirs, files in os.walk(root_dir):
        for i_dir in dirs:
            new_name = i_dir.replace(' ', '_')
            os.rename(os.path.join(root, i_dir), os.path.join(root, new_name))
        for i_file in files:
            os.rename(os.path.join(root, i_file), os.path.join(root, i_file.replace(' ', '_')))


def split_in_series(root_dir):
    # If multiple DICOM series are in the same folder
    # This function will split them up
    for root, dirs, files in os.walk(root_dir):
        if len(files) > 0:
            hash_list = list()
            for i_file in files:
                i_dicom_file = os.path.join(root, i_file)
                try:
                    temp_dicom = pydicom.read_file(i_dicom_file)
                except InvalidDicomError:
                    continue

                # Fields to split on
                if (0x28, 0x10) in temp_dicom:
                    N_rows = temp_dicom[0x28, 0x10].value
                else:
                    N_rows = -1
                if (0x28, 0x11) in temp_dicom:
                    N_columns = temp_dicom[0x28, 0x11].value
                else:
                    N_columns = -1

                # some very small deviations can be expected, so we round
                if (0x28, 0x30) in temp_dicom:
                    pixel_spacing = temp_dicom[0x28, 0x30].value
                    if not isinstance(pixel_spacing, str):
                        pixel_spacing = np.round(pixel_spacing, decimals=6)
                    else:
                        pixel_spacing = [-1, -1]
                else:
                    pixel_spacing = [-1, -1]
                if 'RepetitionTime' in temp_dicom:
                    try:
                        repetition_time = float(temp_dicom[0x18, 0x80].value)
                        repetition_time = np.round(repetition_time, decimals=6)
                    except:
                        repetition_time = -1
                else:
                    repetition_time = -1
                try:
                    echo_time = np.round(temp_dicom[0x18, 0x81].value, decimals=6)
                except:
                    echo_time = -1

                diff_tuple = (N_rows, N_columns, pixel_spacing[0], pixel_spacing[1],
                              repetition_time, echo_time)
                hash_tuple = hash(diff_tuple)

                hash_list.append(hash_tuple)

            if len(set(hash_list)) > 1:
                N_sets = len(set(hash_list))

                i_sets = range(1, N_sets + 1)
                upper_folder = os.path.dirname(root)
                scan_name = os.path.basename(os.path.normpath(root))
                for i_set in i_sets:
                    new_scan_dir = os.path.join(upper_folder, scan_name + '_Scan_' + str(i_set))
                    if not os.path.exists(new_scan_dir):
                        os.makedirs(new_scan_dir)

                _, reverse_indices = np.unique(hash_list, return_inverse=True)

                for i_dicom, index_type in zip(files, reverse_indices):
                    new_scan_dir = os.path.join(upper_folder, scan_name + '_Scan_' + str(i_sets[index_type]))
                    shutil.move(os.path.join(root, i_dicom), new_scan_dir)
                os.rmdir(root)
