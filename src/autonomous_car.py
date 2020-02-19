import cv2
import time
import modi
from lane_tracker import LaneTracker
from object_detector import ObjectDetector

class AutonomousCar(object):
    
    def __init__(self):
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, 320)
        self.camera.set(4, 240)
        self.camera.set(5, 60)
        
        self.tracker = LaneTracker(self)
        self.detector = ObjectDetector(self)

        self.bundle = None
        self.length = 0
    
    def __enter__(self):
        print("----------------------------------------------------------")
        if len(self.bundle.modules) == nb_modules:
            print("Modules are connected:")
            for module in self.bundle.modules:
                print(type(module))
        else:
            print("Modules are not connected properly!")
            print(f"Number of connected Modules: {self.length}")
            self.__exit__(self,None,None)
            #raise ValueError('Cannot initialize MODI modules.')
        print("----------------------------------------------------------")
        
    def __exit__(self,type,value,traceback):
        self.bundle.close()
        
    def run(self):
        """nb_modules == number of modules to use, excluding the network module."""
        m = MODI_Connector(nb_modules=1)
        mot = m.bundle.motors[0]
        i = 0
        while self.camera.isOpened():
            _, image_lane = self.camera.read()
            h,w = image_lane.shape[:2]
            m = cv2.getRotationMatrix2D((w/2,h/2),180,1)
            image_lane = cv2.warpAffine(image_lane,m,(w,h))
            image_objs = image_lane.copy()
            i += 1

            image_objs = self.process_object(image_objs)
            show_image('Detected Objects', image_objs)

            image_lane = self.process_lane(image_lane)
            show_image('Lane Lines', image_lane)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                
                mot.set_torque(0,0)
                self.camera.release()
                cv2.destroyAllWindows()
                break
    
    def process_object(self, image):
        image = self.detector.process_objects_on_road(image)
        return image
    
    def process_lane(self, image):
        image = self.tracker.follow_lane(image)
        return image
    
    def turn_left(self):
        mot.set_torque(30,30)
    
    def turn_right(self):
        mot.set_torque(-30,-30)
    
    def go_straight(self):
        mot.set_torque(20,20)
        time.sleep(0.01)
    
    def stop(self):
        mot.set_torque(0,0)
        time.sleep(0.01)
    
        
    
    
def show_image(title, frame):
    cv2.imshow(title, frame)
    
