import cv2

class VideoCamera(object):
    # A class to manage the video stream of the application
    def __init__(self):
        #Initial video capture from webcam
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        #Release video capture
        self.video.release()
    
    def getFrame(self):
        #Read frame from video stream
        ret, frame = self.video.read()
        #Flip frame horizontally to elimate mirror effect
        frame = cv2.flip(frame,1)
        #Resize video frame
        frame = cv2.resize(frame,None,fx=0.6,fy=0.6,
        interpolation=cv2.INTER_AREA)
        #Encode the frame to jpb
        ret, jpeg = cv2.imencode('.jpg',frame)
        return jpeg.tobytes()
    
    def saveFrame(self,name):
        ret, frame = self.video.read()
        frame = cv2.flip(frame,1)
        frame = cv2.resize(frame,None,fx=0.6,fy=0.6,
        interpolation=cv2.INTER_AREA)
        path = "static/images/"
        #Write the frame as image to disk
        cv2.imwrite(path + name + '.jpg',frame)

    def returnFrame(self):
        ret, frame = self.video.read()
        frame = cv2.flip(frame,1)
        frame = cv2.resize(frame,None,fx=0.6,fy=0.6,
        interpolation=cv2.INTER_AREA)
        return frame
