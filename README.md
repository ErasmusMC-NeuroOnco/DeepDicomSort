# DeepDicomSort

DeepDicomSort can recognize different scan types (pre-contrast T1-weighted, post-contrast T1-weighted, T2-weighted, Proton Density-weighted, T2w-FLAIR-weighted, diffusion weighted imaging, perfusion weighted DSC and derived imaging) of brain tumor scans.
It does this using a CNN.

For more information, see the paper: https://doi.org/10.1007/s12021-020-09475-7

If you use DeepDicomSort in your work, please cite the following: van der Voort, S.R., Smits, M., Klein, S. et al. DeepDicomSort: An Automatic Sorting Algorithm for Brain Magnetic Resonance Imaging Data. Neuroinform 19, 159–184 (2021). https://doi.org/10.1007/s12021-020-09475-7





## Set-up
DeepDicomSort requires the following:
- Python 3.6.7
- dcm2niix (https://github.com/rordenlab/dcm2niix), version v1.0.20190410 was used.
- fsl 5.0 (https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

After install python 3.6.7, install the required packages:
`pip -r install requirements.txt`

The location of the dcm2niix bin and fsl5.0-fslreorient2std bin can be set in the config.yaml file.

### Using python 3.7.x

DeepDicomSort can also run using Python 3.7.x, although this is not the original python version that DeepDicomSort was designed in.

If you want to use Python 3.7.x you need to use a different requirements file as tensorflow version 1.12.X is not available in Python 3.7.x. To install the correct requirements:

`pip -r install requirements_python37.txt`

## Running DeepDicomSort

Before running DeepDicomSort pre-processing of the data is required.
Set the root folder containg the DICOM folders to be organized in the config.yaml file.
After this, go to the preprocessing folder and run `python3 preprocessing_pipeline.py`, this will then perform all the necessary steps.

Once the pre-processing is done, the config.yaml file can be updated with the label file that has been produced (in the DICOM root folder, under a directory called 'DATA'). If you just want to run DeepDicomSort to make a prediction, only the testing settings need to be updated.
After updating the testing settings, one can then run `python3 predict_from_CNN.py` which will produce a file with the predicted class for each scan.
The label corresponding to each scan type is shown in the table below:

| Label  | Scan type |
| ------------- | ------------- |
| 0  | pre-contrast T1-weighted  |
| 1  | post-contrast T1-weighted  |
| 2  | T2 weighted |
| 3  | Proton density weighted |
| 4  | T2 weighted-FLAIR |
| 5  | Diffusion weighted imaging |
| 6  | Derived imaging |
| 7  | Perfusion weighted-DSC|

Once testing is the done, in the config the file with the predicted labels can be specified.
The dataset can then be automatically sorted using either `Sort_to_BIDS.py`, which will sort the dataset into the [BIDS format](https://bids.neuroimaging.io/) (and thus will only sort the NIFTI files), or `Rename_folders_from_predictions.py`, which will sort the whole DICOM dataset.

When sorting to BIDS format derived images and perfusion weighted images are not sort, as they are not supported by BIDS.
`Rename_folders_from_predictions.py` uses a structure used internally at our institute, but it can also be used as an inspiration for your own structure.
