import os
import SimpleITK as sitk
import numpy as np


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def convert_DICOM_to_NIFTI(root_dir):
    # Convert all dicom files in the directory to nifti
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    out_dir = os.path.join(base_dir, 'NIFTI')

    create_directory(out_dir)

    for root, dirs, files in os.walk(root_dir):
        if len(files) > 0:
            patient_ID = root.split(root_dir)[1]
            patient_ID = patient_ID.split(os.sep)[1]

            patient_out_folder = os.path.join(out_dir, patient_ID)
            create_directory(patient_out_folder)

            sub_directory_names = root.split(os.path.join(root_dir, patient_ID))[1]
            sub_directory_names = sub_directory_names.split(os.sep)[1:]

            nifti_file_name = '_'.join(sub_directory_names)

            system_command = 'dcm2niix -b n -d 0 -f ' + nifti_file_name + ' -o ' + patient_out_folder + ' ' + root
            os.system(system_command)

    return out_dir


def extract_4D_images(root_dir):
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    data_dir = os.path.join(base_dir, 'DATA')
    create_directory(data_dir)
    out_4D_file = os.path.join(data_dir, 'Scans_4D.txt')

    with open(out_4D_file, 'w') as the_file:
        for root, dirs, files in os.walk(root_dir):
            for i_file in files:
                if '.nii.gz' in i_file:
                    image_file = os.path.join(root, i_file)

                    image = sitk.ReadImage(os.path.join(root, i_file), sitk.sitkFloat32)
                    if image.GetDimension() == 4:
                        file_name = i_file.split('.nii.gz')[0]
                        image_size = list(image.GetSize())
                        image_size[3] = 0
                        image = sitk.Extract(image,
                                             size=image_size,
                                             index=[0, 0, 0, 0])

                        sitk.WriteImage(image, image_file)

                        the_file.write(file_name + '\n')
    return out_4D_file


def reorient_to_std(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for i_file in files:
            if '.nii.gz' in i_file:
                full_file = os.path.join(root, i_file)

                command = 'fsl5.0-fslreorient2std ' + full_file + ' ' + full_file
                os.system(command)
    return


def resample_images(root_dir, resample_size):
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    out_dir = os.path.join(base_dir, 'NIFTI_RESAMPLED')

    create_directory(out_dir)

    for root, dirs, files in os.walk(root_dir):
        for i_file in files:
            if '.nii.gz' in i_file:
                out_file = os.path.join(out_dir, i_file)

                image = sitk.ReadImage(os.path.join(root, i_file), sitk.sitkFloat32)

                original_size = image.GetSize()
                original_spacing = image.GetSpacing()

                new_spacing = [original_size[0]*original_spacing[0]/resample_size[0],
                               original_size[1]*original_spacing[1]/resample_size[1],
                               original_size[2]*original_spacing[2]/resample_size[2]]

                ResampleFilter = sitk.ResampleImageFilter()

                ResampleFilter.SetInterpolator(sitk.sitkBSpline)

                ResampleFilter.SetOutputSpacing(new_spacing)
                ResampleFilter.SetSize(resample_size)

                ResampleFilter.SetOutputDirection(image.GetDirection())
                ResampleFilter.SetOutputOrigin(image.GetOrigin())
                ResampleFilter.SetOutputPixelType(image.GetPixelID())
                ResampleFilter.SetTransform(sitk.Transform())

                resampled_image = ResampleFilter.Execute(image)

                sitk.WriteImage(resampled_image, out_file)
    return out_dir


def slice_images(root_dir):
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    out_dir = os.path.join(base_dir, 'NIFTI_SLICES')

    create_directory(out_dir)

    for root, dirs, files in os.walk(root_dir):
        for i_file in files:
            if '.nii.gz' in i_file:
                file_name = i_file.split('.nii.gz')[0]
                image = sitk.ReadImage(os.path.join(root, i_file), sitk.sitkFloat32)

                for i_i_slice in range(0, image.GetDepth()):
                    out_file_name = os.path.join(out_dir, file_name + '_' + str(i_i_slice) + '.nii.gz')
                    i_slice = image[:, :, i_i_slice]
                    sitk.WriteImage(i_slice, out_file_name)

    return out_dir


def rescale_image_intensity(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for i_file in files:
            if '.nii.gz' in i_file:
                image = sitk.ReadImage(os.path.join(root, i_file), sitk. sitkFloat32)
                image = sitk.RescaleIntensity(image, 0, 1)
                sitk.WriteImage(image, os.path.join(root, i_file))

    return


def create_label_file(root_dir, images_4D_file):
    base_dir = os.path.dirname(os.path.normpath(root_dir))
    data_dir = os.path.join(base_dir, 'DATA')

    label_file = os.path.join(data_dir, 'labels.txt')

    images_4D = np.genfromtxt(images_4D_file, dtype='str')

    with open(label_file, 'w') as the_file:
        for root, dirs, files in os.walk(root_dir):
            for i_file in files:
                if '.nii.gz' in i_file:
                    file_name = i_file.split('.nii.gz')[0].split('_')[0:-1]
                    file_name = '_'.join(file_name)
                    if file_name in images_4D:
                        is_4D = '1'
                    else:
                        is_4D = '0'

                    file_location = os.path.join(root, i_file)

                    out_elements = [file_location, '99', is_4D]

                    the_file.write('\t'.join(out_elements) + '\n')

    return label_file