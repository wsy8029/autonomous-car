import edgetpu.detection.engine
import cv2
import logging
import time
from PIL import Image



class ObjectDetector(object):
    def __init__(self,
                 car=None,
                 model='../models/road_signs_quantized_edgetpu.tflite',
                 #model='../road_signs_quantized.tflite',
                 label='../models/road_sign_labels.txt',
                 width=320,
                 height=240):
        # model: This MUST be a tflite model that was specifically compiled for Edge TPU.
        
        self.width = width
        self.height = height
        self.car = car
        
        # initialize TensorFlow models
        with open(label, 'r') as f:
            pairs = (l.strip().split(maxsplit=1) for l in f.readlines())
            self.labels = dict((int(k), v) for k, v in pairs)
        
        # initial edge TPU engine
        logging.info('Initialize Edge TPU with model %s...' % model)
        self.engine = edgetpu.detection.engine.DetectionEngine(model)
        self.min_confidence = 0.30
        self.num_of_objects = 3
        logging.info('Initialize Edge TPU with model done.')
        
        # initialize open cv for drawing boxes
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.bottomLeftCornerOfText = (10, height - 10)
        self.fontScale = 1
        self.fontColor = (255, 255, 255)  # white
        self.boxColor = (0, 0, 255)  # RED
        self.boxLineWidth = 1
        self.lineType = 2
        self.annotate_text = ""
        self.annotate_text_time = time.time()
        self.time_to_show_prediction = 1.0  # ms
        
        
    def process_objects_on_road(self, frame):
        # Main entry point of the Road Object Handler
        logging.debug('Processing objects.................................')
        objects, final_frame = self.detect_objects(frame)
        self.control_car(objects)
        logging.debug('Processing objects END..............................')

        return final_frame
        
    def control_car(self, objects):
        logging.debug('Control car...')

        if len(objects) == 0:
            self.car.stop()

        contain_stop_sign = False
        for obj in objects:
            obj_label = self.labels[obj.label_id]
            
            print("**********obj_label : " , obj_label)
            if obj_label == "Stop" or obj_label == "Person" or obj_label == "Red":
                print("############################stop driving")
                self.car.stop()
            elif obj_label == "Limit 25":
                print("############################speed 25")
                self.car.go_straight()
            elif obj_label == "Limit 40":
                print("############################speed 40")
                self.car.go_straight()
            elif obj_label == "Green":
                print("############################Green")
                self.car.go_straight()
 
    def detect_objects(self, frame):
        logging.debug('Detecting objects...')

        # call tpu for inference
        start_ms = time.time()
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_RGB)
        objects = self.engine.DetectWithImage(img_pil, threshold=self.min_confidence, keep_aspect_ratio=True, relative_coord=False, top_k=self.num_of_objects)
        if objects:
            for obj in objects:
                height = obj.bounding_box[1][1]-obj.bounding_box[0][1]
                width = obj.bounding_box[1][0]-obj.bounding_box[0][0]
                logging.debug("%s, %.0f%% w=%.0f h=%.0f" % (self.labels[obj.label_id], obj.score * 100, width, height))
                box = obj.bounding_box
                coord_top_left = (int(box[0][0]), int(box[0][1]))
                coord_bottom_right = (int(box[1][0]), int(box[1][1]))
                cv2.rectangle(frame, coord_top_left, coord_bottom_right, self.boxColor, self.boxLineWidth)
                annotate_text = "%s %.0f%%" % (self.labels[obj.label_id], obj.score * 100)
                coord_top_left = (coord_top_left[0], coord_top_left[1] + 15)
                cv2.putText(frame, annotate_text, coord_top_left, self.font, self.fontScale, self.boxColor, self.lineType)
        else:
            logging.debug('No object detected')

        elapsed_ms = time.time() - start_ms

        annotate_summary = "%.1f FPS" % (1.0/elapsed_ms)
        logging.debug(annotate_summary)
        print(annotate_summary)
        cv2.putText(frame, annotate_summary, self.bottomLeftCornerOfText, self.font, self.fontScale, self.fontColor, self.lineType)


        return objects, frame
        