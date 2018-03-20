#! /usr/bin/env python

import argparse
import os
import cv2
import numpy as np
from tqdm import tqdm
from preprocessing import parse_annotation
from utils import draw_boxes, charm_draw_boxes, skillshot_count 
from frontend import YOLO
import json


os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"

argparser = argparse.ArgumentParser(
    description='Train and validate YOLO_v2 model on any dataset')

argparser.add_argument(
    '-c',
    '--conf',
    help='path to configuration file')

argparser.add_argument(
    '-w',
    '--weights',
    help='path to pretrained weights')

argparser.add_argument(
    '-i',
    '--input',
    help='path to an image or an video (mp4 format)')

def _main_(args):
 
    config_path  = args.conf
    weights_path = args.weights
    image_path   = args.input

    with open(config_path) as config_buffer:    
        config = json.load(config_buffer)

    ###############################
    #   Make the model 
    ###############################

    yolo = YOLO(architecture        = config['model']['architecture'],
                input_size          = config['model']['input_size'], 
                labels              = config['model']['labels'], 
                max_box_per_image   = config['model']['max_box_per_image'],
                anchors             = config['model']['anchors'])

    yolo2 = YOLO(architecture        = config['model']['architecture'],
                input_size          = config['model']['input_size'], 
                labels              = config['model']['labels'], 
                max_box_per_image   = config['model']['max_box_per_image'],
                anchors             = config['model']['anchors'])
    ###############################
    #   Load trained weights
    ###############################    

    print(weights_path)
    yolo.load_weights(weights_path) #feed in the main one, charm on can load on its own
    #yolo2.load_weights('charm_detector_3_12.h5')
    ###############################
    #   Predict bounding boxes 
    ###############################
    print('reading input')
    if image_path[-4:] == '.mp4':
        video_out = image_path[:-4] + '_detected' + image_path[-4:]

        video_reader = cv2.VideoCapture(image_path)

        nb_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_h = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_w = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))

        video_writer = cv2.VideoWriter(video_out,
                               cv2.VideoWriter_fourcc(*'MPEG'), 
                               30.0, 
                               (frame_w, frame_h))
        
        charm_count = 0 
        charm_wait = 0

        orb_count = 0
        orb_wait = 0

        for i in tqdm(range(nb_frames)):
            #can just make function that checks labels. 
            # and respits out the boxes? frames are at 60fps xD 
            # i+240 can be how long it delays those things for
            _, image = video_reader.read()
            
            boxes = yolo.predict(image)
            #boxes2 = yolo2.predict(image)
            #dont really have to draw the orb boxes... but can tally at the side or something

            image = draw_boxes(image, boxes, config['model']['labels'])
            #def skillshot_count(skillshot_name,skillshot_count,boxes,labels,frame_i,wait_i):
            
            charm_count, charm_wait = skillshot_count('charm',charm_count,boxes,config['model']['labels'],i,charm_wait)
            orb_count, orb_wait = skillshot_count('orb',orb_count,boxes,config['model']['labels'],i,orb_wait)


            label = 'Count of Orb of Deceptions: '+str(orb_count)
            cv2.putText(image, label, (0, 475),3,cv2.FONT_HERSHEY_PLAIN,
                                    (0,255,0), 2)
            label = 'Count of Charms: '+str(charm_count)
            cv2.putText(image, label, (0, 525),3,cv2.FONT_HERSHEY_PLAIN,
                                    (0,255,0), 2)

            video_writer.write(np.uint8(image))

        video_reader.release()
        video_writer.release()  
    else:
        image = cv2.imread(image_path)
        boxes = yolo.predict(image)
        boxes2 = yolo2.predict(image)

        image = draw_boxes(image, boxes, config['model']['labels'])
        image = charm_draw_boxes(image, boxes2, config['model']['labels'])

        print(len(boxes), 'boxes are found')

        cv2.imwrite(image_path[:-4] + '_detected' + image_path[-4:], image)

if __name__ == '__main__':
    args = argparser.parse_args()
    _main_(args)