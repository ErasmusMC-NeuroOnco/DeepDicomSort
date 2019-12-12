import os
import yaml
import DICOM_preparation_functions as DPF
import NIFTI_preparation_functions as NPF
import time

start_time = time.time()
with open('../config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

x_image_size = cfg['data_preparation']['image_size_x']
y_image_size = cfg['data_preparation']['image_size_y']
z_image_size = cfg['data_preparation']['image_size_z']
DICOM_FOLDER = cfg['preprocessing']['root_dicom_folder']
DCM2NIIX_BIN = cfg['preprocessing']['dcm2niix_bin']
FSLREORIENT_BIN = cfg['preprocessing']['fslreorient2std_bin']
FSLVAL_BIN = cfg['preprocessing']['fslval_bin']


DEFAULT_SIZE = [x_image_size, y_image_size, z_image_size]


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def is_odd(number):
    return number % 2 != 0


print('Sorting DICOM to structured folders....')
structured_dicom_folder = DPF.sort_DICOM_to_structured_folders(DICOM_FOLDER)

# Turn the following step on if you have problems running the pipeline
# It will replaces spaces in the path names, which can sometimes
# Cause errors with some tools
# print('Removing spaces from filepaths....')
# DPF.make_filepaths_safe_for_linux(structured_dicom_folder)
#
print('Checking and splitting for double scans in folders....')
DPF.split_in_series(structured_dicom_folder)

print('Converting DICOMs to NIFTI....')
nifti_folder = NPF.convert_DICOM_to_NIFTI(structured_dicom_folder, DCM2NIIX_BIN)

print('Moving RGB valued images.....')
NPF.move_RGB_images(nifti_folder, FSLVAL_BIN)

print('Extracting single point from 4D images....')
images_4D_file = NPF.extract_4D_images(nifti_folder)

print('Reorient to standard space....')
NPF.reorient_to_std(nifti_folder, FSLREORIENT_BIN)

print('Resampling images....')
nifti_resampled_folder = NPF.resample_images(nifti_folder, DEFAULT_SIZE)

print('Extracting slices from images...')
nifti_slices_folder = NPF.slice_images(nifti_resampled_folder)

print('Rescaling image intensity....')
NPF.rescale_image_intensity(nifti_slices_folder)

print('Creating label file....')
NPF.create_label_file(nifti_slices_folder, images_4D_file)

elapsed_time = time.time() - start_time

print(elapsed_time)
