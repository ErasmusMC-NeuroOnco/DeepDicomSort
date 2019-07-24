# DeepDicomSort

DeepDicomSort can recognize different scan types (pre-contrast T1-weighted, post-contrast T1-weighted, T2-weighted, Proton Density-weighted, T2w-FLAIR-weighted, diffusion weighted imaging, perfusion weighted DSC and derived imaging) of brain tumor scans.
It does this using a CNN.
For more information, see the paper:



## Set-up
DeepDicomSort requires the following:
- Python 3.6.7
- dcm2niix (https://github.com/rordenlab/dcm2niix), version v1.0.20190410 was used.
- fsl 5.0 (https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

After install python 3.6.7, install the required packages: 
`pip -r install requirements.txt`

The location of the dcm2niix bin and fsl5.0-fslreorient2std bin can be set in the config.yaml file.

## Running DeepDicomSort

Before running DeepDicomSort pre-processing of the data is required.
Set the root folder containg the DICOM folders to be organized in the config.yaml file.
After this, go to the preprocessing folder and run `python3 preprocessing_pipeline.py`, this will then perform all the necessary steps.

Once the pre-processing is done, the config.yaml file can be updated with the label file that has been produced (in the DICOM root folder, under a directory called 'DATA'). If you just want to run DeepDicomSort to make a prediction, only the testing settings need to be updated.
After updating the testing settings, one can then run `python3 predict_from_CCN.py` which will produce a file with the predicted class for each scan.
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
