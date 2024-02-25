import cv2
import os
import re

directory_name = 'C:/Users/yahfou/Desktop/PLUS-FV3-LED/PALMAR/01'

for filename in os.listdir(directory_name):
    for finger in os.listdir(directory_name+'/'+filename):
        img = cv2.imread(directory_name+'/'+ filename +'/'+ finger)
        title = re.findall('[0-9]{1,}' , finger)
        finger_type = title[3]
        
        if finger_type == '02':            
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/02/'+finger,img)
            
        if finger_type == '03':
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/03/'+finger,img)
            
        if finger_type == '04':
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/04/'+finger,img)
            
        if finger_type == '07':
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/07/'+finger,img)
            
        if finger_type == '08':
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/08/'+finger,img)
        
        if finger_type == '09':
            cv2.imwrite('C:/Users/yahfou/Desktop/dataset/09/'+finger,img)
                
            
            
