import numpy as np
import os
import shutil
import yaml
import json

BIDS_VERSION = 'v1.2.1'


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


with open('./config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

prediction_file = cfg['post_processing']['prediction_file']
root_dicom_folder = cfg['preprocessing']['root_dicom_folder']
base_dir = os.path.dirname(os.path.normpath(root_dicom_folder))
nifti_dir = os.path.join(base_dir, 'NIFTI')

base_dir = os.path.dirname(os.path.normpath(root_dicom_folder))
root_out_folder = os.path.join(base_dir, 'BIDS_SORTED')

os.makedirs(root_out_folder, exist_ok=True)

predictions = np.loadtxt(prediction_file, dtype=np.str)

prediction_names = ['T1', 'T1GD', 'T2', 'PD', 'FLAIR', 'DWI_DWI', 'DERIVED', 'PWI_DSC', 'UNKNOWN']
orientation_names = ['3D', 'Ax', 'Cor', 'Sag', 'Obl', '4D', 'UNKNOWN']

prediction_file_names = predictions[:, 0]
prediction_results = predictions[:, 1].astype(np.int)

file_names = [i_file_name.split(os.sep)[-1] for i_file_name in prediction_file_names]

unique_names = np.unique(file_names)
unique_predictions = np.zeros([len(unique_names), 1])

out_json = {'Name': 'DDS_sorted_dataset',
            'BIDSVersion': BIDS_VERSION}

with open(os.path.join(root_out_folder, 'dataset_description.json'), 'w') as jf:
    json.dump(out_json, jf)


def get_out_file_name(subject_label, session_label, sub_type,
                      ce_label, modality_label, run_index):
    run_label = 'run-' + str(run_index)

    scan_labels = list(filter(None,
                             [subject_label, session_label,
                               ce_label, run_label, modality_label]))

    out_file_name = '_'.join(scan_labels) + '.nii.gz'

    out_directory = os.path.join(root_out_folder, subject_label,
                                 session_label, sub_type)

    out_file = os.path.join(out_directory, out_file_name)

    return out_file, out_directory


for root, dir, files in os.walk(nifti_dir):
    if len(files) > 0:
        patient_ID = os.path.basename(os.path.normpath(root))
        patient_ID = patient_ID.replace('-', '')
        subject_label = 'sub-' + patient_ID
        session_dict = dict()
        cur_session_index = 1
        for i_file in files:
            print(i_file)
            # Reset everything
            sub_type = None
            modality_label = None
            ce_label = None
            session_label = None

            full_file = os.path.join(root, i_file)
            i_file = i_file.split('.nii.gz')[0]
            splitted_elements = i_file.split('__')
            session_ID = splitted_elements[2]

            if session_ID not in session_dict:
                session_dict[session_ID] = cur_session_index
                session_num = cur_session_index
                cur_session_index += 1
            else:
                session_num = session_dict[session_ID]
            session_label = 'ses-' + str(session_num)

            indices = np.argwhere([i_file in i_result_name for i_result_name in file_names])
            if len(indices) != 0:
                predictions = prediction_results[indices].ravel()
                i_prediction = np.bincount(predictions).argmax() - 1
            else:
                i_prediction = -1

            if i_prediction == 0 or i_prediction == 1:
                sub_type = 'anat'
                modality_label = 'T1w'
                if i_prediction == 1:
                    ce_label = 'ce-GD'
            elif i_prediction == 2:
                sub_type = 'anat'
                modality_label = 'T2w'
            elif i_prediction == 3:
                sub_type = 'anat'
                modality_label = 'PD'
            elif i_prediction == 4:
                sub_type = 'anat'
                modality_label = 'FLAIR'
            elif i_prediction == 5:
                sub_type = 'dwi'
                modality_label = 'dwi'
            else:
                break
            current_run_index = 1

            scan_labels = [subject_label, ce_label, modality_label]

            out_file, out_directory = get_out_file_name(subject_label, session_label,
                                         sub_type, ce_label, modality_label,
                                         current_run_index)

            while os.path.exists(out_file):
                current_run_index += 1
                out_file, out_directory = get_out_file_name(subject_label, session_label,
                                             sub_type, ce_label, modality_label,
                                             current_run_index)

            if not os.path.exists(out_directory):
                os.makedirs(out_directory)

            shutil.copy(full_file, out_file)
