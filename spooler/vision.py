import cv2
import numpy

CV2_CAM_INDEX = 0
RED_MIN = 0
RED_MAX = 30

class Vision:

    def __init__(self):
        self.camera = cv2.VideoCapture(CV2_CAM_INDEX)
    
    ## Find lateral distribution of the target color
    def lateral(self):
        (s,rgb) = self.camera.read()
        if s:
            hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
            sat_min = hsv[:,:,1].mean()
            val_min = hsv[:,:,2].mean()
            hue_min = numpy.array([RED_MIN, sat_min, val_min], numpy.uint8)
            hue_max = numpy.array([RED_MAX, 255, 255], numpy.uint8)
            excess_red = cv2.inRange(hsv, hue_min, hue_max)
            arr = excess_red.sum(axis=0)
            return (arr, rgb)
        else:
            return None
    
    ## Cluster array to filter to single points
    def cluster(self, array):
        filtered = (array > numpy.mean(array))
        print filtered
        
    ## Display image
    def display(self, image):
        cv2.imshow('', image)
        cv2.waitKey(0)
        pass
        
if __name__ == '__main__':
    vision = Vision()
    (arr, img) = vision.lateral()
    filt = vision.cluster(arr)
    vision.display(img)
