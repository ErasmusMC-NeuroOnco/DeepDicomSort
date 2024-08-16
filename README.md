# DeepDicomSort

DeepDicomSort can recognize different scan types (pre-contrast T1-weighted, post-contrast T1-weighted, T2-weighted, Proton Density-weighted, T2w-FLAIR-weighted, diffusion weighted imaging, perfusion weighted DSC and derived imaging) of brain tumor scans.
It does this using a CNN.

For more information, see the paper: <https://doi.org/10.1007/s12021-020-09475-7>

If you use DeepDicomSort in your work, please cite the following: van der Voort, S.R., Smits, M., Klein, S. et al. DeepDicomSort: An Automatic Sorting Algorithm for Brain Magnetic Resonance Imaging Data. Neuroinform 19, 159–184 (2021). <https://doi.org/10.1007/s12021-020-09475-7>

If you want to use a docker image please see the end of this section.
If you want to install manually please continue reading.

## Set-up

DeepDicomSort requires the following:

- Python 3.6.7
- [dcm2niix](https://github.com/rordenlab/dcm2niix), version v1.0.20190410 was used.
- [fsl 5.0](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

After install python 3.6.7, install the required packages:
`pip install -r requirements.txt`

The location of the dcm2niix bin and fsl5.0-fslreorient2std bin can be set in the config.yaml file.

### Using python 3.7.x

DeepDicomSort can also run using Python 3.7.x, although this is not the original python version that DeepDicomSort was designed in.

If you want to use Python 3.7.x you need to use a different requirements file as tensorflow version 1.12.X is not available in Python 3.7.x. To install the correct requirements:

`pip install -r requirements_python37.txt`

## Running DeepDicomSort

Before running DeepDicomSort pre-processing of the data is required.
Set the root folder containing the DICOM folders to be organized in the config.yaml file.
After this, go to the preprocessing folder and run `python3 preprocessing_pipeline.py`, this will then perform all the necessary steps.

Once the pre-processing is done, the config.yaml file can be updated with the label file that has been produced (in the DICOM root folder, under a directory called 'DATA'). If you just want to run DeepDicomSort to make a prediction, only the testing settings need to be updated.
After updating the testing settings, one can then run `python3 predict_from_CNN.py` which will produce a file with the predicted class for each scan.
The label corresponding to each scan type is shown in the table below. The leftmost column is the label as predicted directly by the CNN if you use the CNN directly. The second column is the label as is provided in the predictions file, where +1 has been added to each label to make them range from 1 up to and including 8.

| Label prediction by CNN | Label in prediction file | Scan type                  |
| ----------------------- | ------------------------ | -------------------------- |
| 0                       | 1                        | pre-contrast T1-weighted   |
| 1                       | 2                        | post-contrast T1-weighted  |
| 2                       | 3                        | T2 weighted                |
| 3                       | 4                        | Proton density weighted    |
| 4                       | 5                        | T2 weighted-FLAIR          |
| 5                       | 6                        | Diffusion weighted imaging |
| 6                       | 7                        | Derived imaging            |
| 7                       | 8                        | Perfusion weighted-DSC     |

Once testing is the done, in the config the file with the predicted labels can be specified.
The dataset can then be automatically sorted using either `Sort_to_BIDS.py`, which will sort the dataset into the [BIDS format](https://bids.neuroimaging.io/) (and thus will only sort the NIFTI files), or `Rename_folders_from_predictions.py`, which will sort the whole DICOM dataset.

When sorting to BIDS format derived images and perfusion weighted images are not sort, as they are not supported by BIDS.
`Rename_folders_from_predictions.py` uses a structure used internally at our institute, but it can also be used as an inspiration for your own structure.

## Running using docker

If you do not want to set up things manually you can use a docker that comes with all the required dependencies pre-installed.
Running DeepDicomSort using docker is easy and requires only two setup steps:

### Getting the DeepDicomSort docker

The DeepDicomSort docker can be obtained from dockerhub using the following command: `docker pull svdvoort/dds:1.0.0`.

### Preparing data

To prepare the data for the docker first create a root directory, for example `/home/user/deepdicomsort`.
In this root directory you need to create on directory called `DICOM` (so in this example `/home/user/deepdicomsort/DICOM`), in which you put all DICOM data to be sorted.
You also need to create an output folder, which you can name whatever you want, for example `/home/user/deepdicomsort/out`.

You are now done with the setup, and are ready to run the docker

### Running the DeepDicomSort docker

Running the docker is done using one simple command:

`docker run -u $UID:$GROUPS -v "<root_folder>:/input/" -v "<output_folder>:/output/" svdvoort/dds:1.0.0`

Where `<root_folder>` is the root folder you created before, and `<output_folder>` is the output folder you created.
So using the example from above the command would be:

`docker run -u $UID:$GROUPS -v "/home/user/deepdicomsort/:/input/" -v "/home/user/deepdicomsort/out/:/output/" svdvoort/dds:1.0.0`

## Scan data

We have released the data regarding the scan types that have been used for the construction in the algorithm.
This data also includes the scan types of some scans that were in the end not used in this work, but which can still be valuable for other researchers.
This data can be found in the `Data/` folder, where there is a file for the train set(`TCIA_scan_types_UID_train.csv`) and for the test set (`TCIA_scan_types_UID_test.csv`).
These files contains the following data:

- `TCIA project name`: The project name of the data on TCIA
- `TCIA subject ID`: The identifier of the subject on TCIA
- `Series UID`: The series instance UID extracted from DICOM tag (0020,000E)
- `Series ID`: The series number extracted from DICOM tag (0020,0011)
- `Scan type`: The scan type as identified manually (so not by the algorithm!). See the below table for explanation
- `Scan direction`: The scan direction as based on the direction matrix

The following scan types are identified:

| Scan type   | Meaning                                 |
| ----------- | --------------------------------------- |
| T1          | Pre-contrast T1-weighted                |
| T1GD        | Post-contrast T1-weighted               |
| T2          | T2-weighted                             |
| FLAIR       | T2-weighted FLAIR                       |
| PD          | Proton Density-weighted                 |
| DWI_DWI     | Diffusion weighted scan                 |
| DWI_DERIVED | Scan derived from DWI (for example ADC) |
| PWI_DSC     | DSC-type perfusion scan                 |
| PWI_DCE     | DCE-type perfusion scan                 |

### TCIA projects

The following TCIA projects are included in this data:

#### Train set

- [Brain-Tumor-Progression](https://doi.org/10.7937/K9/TCIA.2018.15quzvnb)
- [IvyGAP](https://doi.org/10.7937/K9/TCIA.2016.XLwaN6nL)
- [LGG-1p19qDeletion](https://doi.org/10.7937/K9/TCIA.2017.DWEHTZ9V)
- [TCGA-GBM](https://doi.org/10.7937/K9/TCIA.2016.RNYFUYE9)
- [TCGA-LGG](https://doi.org/10.7937/K9/TCIA.2016.L4LTD3TK)

#### Test set

- [CPTAC-GBM](https://doi.org/10.7937/K9/TCIA.2018.3RJE41Q1)
- [REMBRANDT](https://doi.org/10.7937/K9/TCIA.2015.588OZUZB)
- [RIDER NEURO MRI](https://doi.org/10.7937/K9/TCIA.2015.VOSN3HN1)
