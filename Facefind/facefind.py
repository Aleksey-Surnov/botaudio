import os
import cv2

class Lookforface():

    def __init__(self, file_name: str, model_name: list):
        self.file_name = file_name
        self.model_name = model_name

    def get_face(self):
        image = cv2.imread(self.file_name)
        for model in self.model_name:
            clf = cv2.CascadeClassifier(os.path.abspath('./model/'+f'{model}'))
            faces = clf.detectMultiScale(
                image,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces)!=0: return True
        return False



