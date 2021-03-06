# -*- coding: utf-8 -*-
"""
Created on Fri Feb 02 16:06:33 2018

@author: mira
"""

print("[INFO] START")

import file_manager_metacentrum as fm
import CNN_evaluator
import CNN_boxes_evaluator
import numpy as np
import h5py

print("[INFO] Vse uspesne importovano - OK")


def evaluate_hogs_only(experiment_foldername, checkpoint=False):
    """ Ohodnoceni natrenovaneho modelu podle vsech moznych kriterii """

    # nacteni dat
    hdf_filename = experiment_foldername+"/test_results.hdf5"
    hdf_file = h5py.File(hdf_filename, 'r')
    test_data = hdf_file['test_data']
    test_labels = hdf_file["test_labels"]
    test_predictions = hdf_file["test_predictions"]

    # --- Vlastni hodnotici metody ---
    eval_fname = "/evaluation-checkpoint.json" if checkpoint else "/evaluation.json"
    my_eval_vocab = {}
    try:
        my_eval_vocab = fm.load_json(experiment_foldername+eval_fname)
    except:
        pass
    
    # HoGovsky evaluate
    _, _, _, _, boxes_eval = CNN_boxes_evaluator.evaluate_nms_results_overlap(test_data, 
                                                                              test_labels, 
                                                                              test_predictions)
    my_eval_vocab.update({"boxes": boxes_eval})
    # ulozeni vysledku
    fm.save_json(my_eval_vocab, experiment_foldername+eval_fname)


def save_results(model, test_data, test_labels,
                 path="experiments/", dtype=np.float):
    
    test_predicted_labels = model.predict(test_data)
    
    test_results_path = path if path.endswith(".hdf5") else path + "test_results.hdf5"
    hdf5_file = h5py.File(test_results_path , mode='w')
    hdf5_file.create_dataset("test_data", test_data.shape, np.uint8)
    hdf5_file["test_data"][...] = test_data
    hdf5_file.create_dataset("test_labels", test_labels.shape, np.uint8)
    hdf5_file["test_labels"][...] = test_labels
    hdf5_file.create_dataset("test_predictions", test_predicted_labels.shape, dtype)
    hdf5_file["test_predictions"][...] = test_predicted_labels
    hdf5_file.close()


def save_results_predicted(test_predicted_labels, hdf_file, dtype=np.float,
                           path="experiments/"):
    
    # nacteni dat
    test_data = hdf_file['test_data']
    test_labels = hdf_file["test_labels"]    
    
    test_results_path = path if path.endswith(".hdf5") else path + "test_results.hdf5"
    hdf5_file = h5py.File(test_results_path , mode='w')
    hdf5_file.create_dataset("test_data", test_data.shape, np.uint8)
    hdf5_file["test_data"][...] = test_data
    hdf5_file.create_dataset("test_labels", test_labels.shape, np.uint8)
    hdf5_file["test_labels"][...] = test_labels
    hdf5_file.create_dataset("test_predictions", test_predicted_labels.shape, dtype)
    hdf5_file["test_predictions"][...] = test_predicted_labels
    hdf5_file.close()
    


def save_results_predicted_reduced(test_predicted_labels, dtype=np.float,
                                   path="experiments/"):
    """ Ulozi jen test_predictions """
    test_results_path = path if path.endswith(".hdf5") else path + "test_results.hdf5"
    hdf5_file = h5py.File(test_results_path , mode='w')
    hdf5_file.create_dataset("test_predictions", test_predicted_labels.shape, dtype)
    hdf5_file["test_predictions"][...] = test_predicted_labels
    hdf5_file.close()


def evaluate_all(hdf_file, model, experiment_foldername, 
                 save_predictions=True, checkpoint=False, predict=True, 
                 batch_size=8):
    """ Ohodnoceni natrenovaneho modelu podle vsech moznych kriterii """

    # nacteni dat
    test_data = hdf_file['test_data']
    test_labels = hdf_file["test_labels"]
    
    # ohodnoceni Keras
    evaluation = model.evaluate(x=test_data, y=test_labels, batch_size=batch_size)
    print(model.metrics_names, evaluation)
    # ulozeni do souboru
    eval_vocab = {}
    for i in range(len(model.metrics_names)):
        eval_vocab[model.metrics_names[i]] = evaluation[i]
    model_eval_fname = "/model_evaluation-checkpoint.json" if checkpoint else "/model_evaluation.json"
    fm.save_json(eval_vocab, experiment_foldername + model_eval_fname)
    
    # --- Ohodnoceni vlastnimi metrikami ---
    
    if predict:
        print("[INFO] Probiha predikce testovacich dat...")
        test_predicted_labels = model.predict(test_data, batch_size=batch_size)
        del model
      
    else:
        del model
        print("[INFO] Probiha nacitani testovacich dat...")
        tr_fname = "/test_results-checkpoint.hdf5" if checkpoint else "/test_results.hdf5"
        hdf_file.close()          # uzavre se puvodni soubor s testovacimi daty
        hdf_file = h5py.File(experiment_foldername + tr_fname, 'r')
        test_data = hdf_file['test_data']
        test_labels = hdf_file["test_labels"]
        test_predicted_labels = hdf_file["test_predictions"]
    
    print("[INFO] Hotovo.")
    
    # ulozeni vysledku
    if save_predictions and predict:
        tr_fname = "/test_results-checkpoint.hdf5" if checkpoint else "/test_results.hdf5"
        save_results_predicted(test_predicted_labels, hdf_file, 
                               dtype=np.float32,
                               path=experiment_foldername + tr_fname)
                               
                              
    # --- Vlastni hodnotici metody ---
    my_eval_vocab = {}                            
    # Jaccard similarity
    JS, values = CNN_evaluator.evaluate_JS(test_labels, test_predicted_labels,
                                           save_Js=True)
    JS_fname = "/JS_values-checkpoint.json" if checkpoint else "/JS_values.json"
    fm.save_json(values, experiment_foldername + JS_fname)  # ulozeni JS hodnot
    my_eval_vocab.update(JS)
    # HoGovsky evaluate
    _, _, _, _, boxes_eval = CNN_boxes_evaluator.evaluate_nms_results_overlap(test_data, 
                                                                              test_labels, 
                                                                              test_predicted_labels)
    my_eval_vocab.update({"boxes": boxes_eval})
    # ulozeni mezivysledku
    eval_fname = "/evaluation-checkpoint.json" if checkpoint else "/evaluation.json"
    fm.save_json(my_eval_vocab, experiment_foldername + eval_fname)
    # accuracy per pixel
    ApP = CNN_evaluator.accuracy_per_pixel(test_labels, test_predicted_labels)
    my_eval_vocab["per_pixel_accuracy"] = ApP
    AMat_soft = CNN_evaluator.accuracy_matrix(test_labels,
                                              test_predicted_labels).tolist()
    my_eval_vocab["accuracy_matrix_soft"] = AMat_soft
    AMat_onehot = CNN_evaluator.accuracy_matrix(test_labels, 
                                                test_predicted_labels, 
                                                mode="onehot",
                                                batch_size=50).tolist()
    my_eval_vocab["accuracy_matrix_onehot"] = AMat_onehot
    # ulozeni vysledku
    fm.save_json(my_eval_vocab, experiment_foldername + eval_fname)