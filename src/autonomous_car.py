import cv2
import time
import modi
from lane_tracker import LaneTracker
from object_detector import ObjectDetector



class MODI_Connector(object):

    def __init__(self, nb_modules=0):
        print('Start initializing MODI instance')
        self.bundle = None
        self.length = nb_modules
    
    def __enter__(self):
        self.bundle = modi.MODI()
        print("----------------------------------------------------------")
        
        if len(self.bundle.modules) == self.length:
            print("Modules are connected:")
            for module in self.bundle.modules:
                print(type(module))
            print(self)
            
        else:
            print("Modules are not connected properly!")
            print("Number of connected Modules: {self.length}")
            print("----------------------------------------------------------")
            self.__exit__(self,None,None)
            
        print("----------------------------------------------------------")
        
        return self.bundle
        
    def __exit__(self,type,value,traceback):
        del self
    
class AutonomousCar(object):
    def __init__(self):
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, 320)
        self.camera.set(4, 240)
        self.camera.set(5, 60)
        
        self.tracker = LaneTracker(self)
        self.detector = ObjectDetector(self)
        
        self.mot = None
        
    def run(self):
        """nb_modules == number of modules to use, excluding the network module."""
        with MODI_Connector(1) as m:
            self.mot = m.motors[0]
        
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
        self.mot.set_torque(30,30)
    
    def turn_right(self):
        self.mot.set_torque(-30,-30)
    
    def go_straight(self):
        self.mot.set_torque(20,20)
        time.sleep(0.01)
    
    def stop(self):
        self.mot.set_torque(0,0)
        time.sleep(0.01)
    
        
    
    
def show_image(title, frame):
    cv2.imshow(title, frame)
    
