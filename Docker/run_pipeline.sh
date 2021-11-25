#!/bin/bash

mkdir -p /output/

cd /DeepDicomSort/Preprocessing
python3 preprocessing_pipeline.py

cd /DeepDicomSort/
python3 predict_from_CNN.py

python3 Rename_folders_from_predictions.py
python3 Sort_to_BIDS.py
