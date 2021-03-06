# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 17:01:02 2017

@author: mira
"""

import os
import copy
import numpy as np
import re
import logging

import skimage.io

import glob
import json

from imutils import paths
import imutils

import random
import pickle
import cPickle


def load_json(name):
    """ Nacte .json soubor a vrati slovnik """
    filepath = os.path.dirname(os.path.abspath(__file__))+"/"+str(name)
    mydata = {}
    with open(filepath) as d:
        mydata = json.load(d)
        d.close()
    return mydata
 
   
def zapis_json(jsondata,  name):
    """ Ulozi slovnik do .json souboru """
    filepath = os.path.dirname(os.path.abspath(__file__))+"/"+str(name)
    with open(filepath, 'w') as f:
        json.dump(jsondata, f)


def save_obj(obj, name):
    """ Ulozi data do .pkl souboru """
    filepath = os.path.dirname(os.path.abspath(__file__))+"/"+str(name)
    with open(filepath, 'wb') as f:
        f.write(cPickle.dumps(obj))
        f.close()


def load_obj(name):
    """ Nact data z .pkl souboru """
    filepath = os.path.dirname(os.path.abspath(__file__))+"/"+str(name)
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def load_image(name):
    """ Nacte a vrati obrazek """
    suffix = re.findall(r'\.{1}\w+', name)[0]
    
    if suffix in [".pkl", ".pklz"]:
        return load_obj(name).astype(float)
    
    elif suffix in [".jpg", ".png"]:
        return skimage.io.imread(name, as_grey=True).astype(float)


def save_image(img, name):
    """ Ulozi obrazek jako objekt nebo jako png """
    
    suffix = re.findall(r'\.{1}\w+', name)[0]
    
    if suffix in [".pkl", ".pklz"]:
        save_obj(img.astype("uint8"), name)
    
    elif suffix in [".jpg", ".png"]:
        skimage.io.imsave(name, img.astype("uint8"))


class DATAset:
    
    def __init__(self, configpath="configuration/", configname="CT.json"):
        
        self.config_path = configpath + configname
        self.config = self.precti_json(configpath + configname)

        self.orig_images_path = self.config["images_path"]
        self.annotated_images_path = self.config["annotated_images_path"]
        self.negatives_path = self.config["negatives_path"]
        self.test_images_path = self.config["test_images_path"]
        self.HNM_images_path = self.config["HNM_images_path"]
        self.masks_path = self.config["masks_path"]
        self.evaluation_test_images = self.config["evaluation_test_images_path"]
        
        self.annotations_path = self.config["annotations_path"] # file with bounding boxes
        
        self.orig_images = list()
        self.annotated_images = list()
        self.negatives = list()
        self.test_images = list()
        self.HNM_images = list()
        self.evaluation_test_images = list()
        
        self.annotations = dict() # bounding boxes
        
        self.features = list()    # HOG, SIFT, SURF, ... features
        # incializace logovani
        self.init_logging()       


    def create_dataset_CT(self):
        """ Vytvori cely dataset - CT rezy
                - obrazky uz vytvorime rucne predem
                - nebudou se menit casto """

        self.orig_images = [self.config["images_path"]+imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+self.config["images_path"]) if imgname.endswith('.pklz')]
        self.negatives = [self.config["negatives_path"]+imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+self.config["negatives_path"]) if imgname.endswith('.pklz')]
        self.test_images = [self.config["test_images_path"]+imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+self.config["test_images_path"]) if imgname.endswith('.pklz')]
        self.HNM_images = [self.config["HNM_images_path"]+imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+self.config["HNM_images_path"]) if imgname.endswith('.pklz')]       
        self.annotations = self.precti_json(self.annotations_path)
        self.evaluation_test_images = [self.config["evaluation_test_images_path"]+imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+self.config["evaluation_test_images_path"]) if imgname.endswith('.pklz')]

        print "Vytvoren dataset"
    
    
    def create_dataset_classic(self):
        """ Vytvori cely dataset - klasicky priklad """
        unprocessed_images_path = self.config["unprocessed_images_path"]
        unprocessed_negatives_path = self.config["unprocessed_negatives_path"]
        unprocessed_test_images_path = self.config["unprocessed_test_images_path"]
        
        print "Vytvarim obrazky..."
        self.prepare_images(unprocessed_images_path, self.orig_images_path, self.orig_images)
        print "Vytvarim negativni obrazky..."  
        self.prepare_images(unprocessed_negatives_path, self.negatives_path, self.negatives)
        print "Vytvarim testovaci obrazky..." 
        self.prepare_images(unprocessed_test_images_path, self.test_images_path, self.test_images)
        print "Zpracovavam anotace..."
        self.annotations = self.load_annotated_images()
        print "Hotovo"

        
    def precti_json(self, name):
        """ Nacte .json soubor a vrati slovnik """
        return load_json(name)
     
       
    def zapis_json(self, jsondata,  name):
        """ Ulozi slovnik do .json souboru """
        zapis_json(jsondata,  name)

    
    def save_obj(self, obj, name):
        """ Ulozi data do .pkl souboru """
        save_obj(obj, name)


    def load_obj(self, name):
        """ Nacte data z .pkl souboru """
        return load_obj(name)
    
    
    def load_image(self, name):
        """ Nacte a vrati obrazek """
        return load_image(name)
    
    
    def save_image(self, img, name):
        """ Ulozi obrazej jako objekt nebo jako png """
        save_image(img, name)
    
    
    def init_logging(self):
        """ Inicializuje logovani """
        
        logging.basicConfig(filename=self.config["log_file_path"], 
                            level=logging.INFO, 
                            format='%(asctime)s %(levelname)-8s %(message)s', 
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    
    
    def log_info(self, info_message):
        """ Zaloguje zpravu """
        
        logging.info(info_message)
    
        
    def upload_config(self, configname, new_config):
        """ Aktualizuje konfiguracni soubor .json
            -> prida nove polozky a aktualizuje stare """
        
        config = dict()
        try:
            config = self.precti_json(configname)
        except:
            pass
        
        # aktualizace konfigurace
        config.update(new_config)
        
        # zapise json do zase do souboru
        self.zapis_json(config, configname)
    
    
    def prepare_images(self, source_path, target_path, processed_images):
        """ Nacte obrazky a ulozi je ve vhodne forme (sede atd.) 
            -> navic je ulozi take do prislusneho seznamu v teto tride """
            
        images = list(paths.list_images(source_path))
        for i, imgname in enumerate(images):
            img_orig = skimage.io.imread(images[i], 0)
            gray_orig = skimage.color.rgb2gray(img_orig)
            gray_orig = skimage.img_as_ubyte(gray_orig)
            
            image_target_path = target_path + os.path.basename(imgname)
            
            skimage.io.imsave(image_target_path, gray_orig)
            processed_images.append(image_target_path)

    
    def load_annotated_images(self):
        """ Nacte anotovane obrazky a spocita bounding boxy -> 
            -> ty pote vrati a zaorven ulozi do jsonu """
        
        if not self.orig_images:
            self.orig_images = list(paths.list_images(self.orig_images_path))
        self.annotated_images = list(paths.list_images(self.annotated_images_path))
        
        boxes = dict()
        for i, imgname in enumerate(self.annotated_images):
            
            img_anot = skimage.io.imread(imgname, as_grey=True)
            gray_anot = skimage.color.rgb2gray(img_anot)
            gray_anot = skimage.img_as_float(gray_anot)
            img_orig = skimage.io.imread(self.orig_images[i], as_grey=True)
            gray_orig = skimage.color.rgb2gray(img_orig)
            gray_orig = skimage.img_as_float(gray_orig)
            
            difference = np.abs(gray_anot - gray_orig)
    
            coords = np.where(difference>0.1)
            (y, h, x, w) = min(coords[0]), max(coords[0]), min(coords[1]), max(coords[1])
            #boxes[self.orig_images[i]] = {"x":x, "w":w, "y":y, "h":h}
            boxes[self.orig_images[i]] = list()
            boxes[self.orig_images[i]].append((y, h, x, w))
            
        self.zapis_json(boxes, self.annotations_path)
        return boxes
        
    
    def make_pngs(self, foldername, suffix=".pklz"):
        """ Vytvori slozku PNG v dane slozce a tam ulozi vsechny pklz soubory v PNG """
        
        # vytvoreni cesty
        PNG_path = self.config["PNG_path"]+foldername
        newpath = str(os.path.dirname(os.path.abspath(__file__)))+'/'+PNG_path
        # vytvorit slozku, pokud neexistuje
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        # seznam obrazku
        imgnames = [foldername + imgname for imgname in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"+foldername) if imgname.endswith(suffix)]
        
        # ukladani obrazku
        for imgname in imgnames:
            img = self.load_image(imgname)
            name = re.findall('[^\/]*\.pkl.*', imgname)[0][:-len(suffix)]
            skimage.io.imsave(newpath+name+'.png', img.astype("uint8"))