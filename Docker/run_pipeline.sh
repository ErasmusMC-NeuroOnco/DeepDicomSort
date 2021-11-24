#!/bin/bash

# Do not add a trailing slash to any of the paths!

INPUT_FOLDER='/input'
OUTPUT_FOLDER='/output'
DATA_FOLDER='/DATA'
ATLAS_DATA_FOLDER=$DATA_FOLDER'/ATLAS'
ELASTIX_DATA_FOLDER=$DATA_FOLDER'/ELASTIX'
MODEL_FOLDER=$DATA_FOLDER'/MODEL'

registration_folder=$OUTPUT_FOLDER'/Registered'
mkdir -p $registration_folder

for pat_dir in $INPUT_FOLDER/*
do
    patient_name="$(basename $pat_dir)"
    echo "Registering scans for patient $patient_name"
    pat_registered_folder=$registration_folder/$patient_name
    echo $pat_registered_folder
    mkdir -p $pat_registered_folder
    for scan in $pat_dir/*.nii.gz
    do
        scan_name="$(basename $scan)"
        echo "Registering scan $scan_name"
        if [[ $scan == *"T2.nii.gz"* ]] || [[ $scan == *"FLAIR.nii.gz"* ]] ; then
            atlas_file=$ATLAS_DATA_FOLDER/T2_atlas.nii.gz
        fi

        if [[ $scan == *"T1GD.nii.gz"* ]] || [[ $scan == *"T1.nii.gz"* ]] ; then
            atlas_file=$ATLAS_DATA_FOLDER/T1_atlas.nii.gz
        fi

        elastix -f $atlas_file -m $scan -out $pat_registered_folder -p $ELASTIX_DATA_FOLDER/parameter_map_0.txt -p $ELASTIX_DATA_FOLDER/parameter_map_1.txt
        transformix -in $scan -out $pat_registered_folder -tp $pat_registered_folder/TransformParameters.1.txt

        mv $pat_registered_folder/result.nii.gz $pat_registered_folder/$scan_name

        atlas_file="NONE"
        rm $pat_registered_folder/*.txt
        rm $pat_registered_folder/*.log

    done
done

prediction_output_folder=$OUTPUT_FOLDER/Predictions
mkdir -p $prediction_output_folder
# echo $prediction_output_folder
prognosais_model_folder=$MODEL_FOLDER'/prognosais_model'
config_file=$MODEL_FOLDER'/config_prognosais_model.yaml'
python3 /get_predictions.py $prognosais_model_folder $registration_folder $prediction_output_folder $config_file

mv $prediction_output_folder/Results $OUTPUT_FOLDER
rm -r $OUTPUT_FOLDER/PSNET*
rm -r $prediction_output_folder/Samples
rm -r $prediction_output_folder/config.yml
rm -r $prediction_output_folder/labels.txt
