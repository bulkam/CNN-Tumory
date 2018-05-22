# Tumory
Liver lesions detector using CNN

## CNN
### Dataset
1. Insert CT data (.pklz format) into -> **CTs/** 
2. Generate image data.
```
cd CTs
python kerasdata_maker.py
cd ..
```

3. Create dataset (.hdf5 format) from generated images.
```
python keras_dataset_maker.py
```

This command creates dataset and stores it into the file **datasets/processed/aug_structured_data-liver_only.hdf5** 

### Model fitting
Choose an architecture and run proper script named as SegNet*ArchitectureType*.py
```
python *script_name*.py
```

This command fits a model using the selected architecture and evaluates it with several metrics.

The model will be saved in the folder **experiments/aug_structured_data-liver_only**/*experiment_name*/ as **model.hdf5**.

Evaluation results are then stored into the files **evaluation.json** and **model_evaluation.json** in the same folder as the model.

Example:
```
python SegNetIncp13_Morph.py --optimizer Adam --epochs 10 --batch_size 6 > SegNetIncp13_Morph.txt
```

This command fits the model with architecture _SegNetIncp13_Morph_ using _Adam_ optimizer, _10_ epochs and batch size _6_ and evaluates it with several metrics. 

All outputs are then written into the file **SegNetIncp13_Morph.txt**.

### Load fitted model and evaluate it
```
python ReEvaluate_trained_model.py *path_to_model_file*
```

- This command loads existing model and evaluate it on the training set which is stored in the file **datasets/processed/aug_structured_data-liver_only.hdf5**

- Argument *path_to_model_file* should contain the name of the folder where the model is stored and it has to be defined.

- The resulting predictions will be saved in this folder with the name **test_results.hdf5**.

- Evaluation results are then stored into the files **evaluation.json** and **model_evaluation.json** in the folder, where the model is stored.

### Visualize results predicted by CNN
```
python keras_result_explorer.py *path_to_model_file*
```

##### This command:
1. loads **_path_to_model_file_/test_results.hdf5**
2. extracts images
3. visualizes results and stores them into **_path_to_model_file_/images/**

Argument *path_to_model_file* should contain the name of the folder where the model is stored and it has to be defined.


## Configuration

Many settings such as paths to saving/loading some files or parameters of the most of used methods are writen in two configuration files:
1. **CTs/Configuration/config.json** - contains paths and parameters which are associated with the process of creating dataset.
2. **configuration/CT.json** - contains paths and parameters mostly associated with the methods used for the image processing, feature extraction and classification.
