import cv2
import os
import re

directory_name = 'XXX/XXX/XXX.../PLUS-FV3-LED/PALMAR/01'    # 修改為存放PLUS-FV3-LED資料庫的位置

for filename in os.listdir(directory_name):
    for finger in os.listdir(directory_name+'/'+filename):
        img = cv2.imread(directory_name+'/'+ filename +'/'+ finger)
        title = re.findall('[0-9]{1,}' , finger)
        man_type = title[2]
        finger_type = title[3]
        
        if finger_type == '02':            
            cv2.imwrite('XXX/XXX/XXX.../dataset/02/'+man_type+'/'+finger,img)    # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置
            
        if finger_type == '03':
            cv2.imwrite(XXX/XXX/XXX.../dataset/03/'+man_type+'/'+finger,img)     # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置
            
        if finger_type == '04':
            cv2.imwrite('XXX/XXX/XXX.../dataset/04/'+man_type+'/'+finger,img)    # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置
            
        if finger_type == '07':
            cv2.imwrite('XXX/XXX/XXX.../dataset/07/'+man_type+'/'+finger,img)    # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置
            
        if finger_type == '08':
            cv2.imwrite('XXX/XXX/XXX.../dataset/08/'+man_type+'/'+finger,img)    # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置
        
        if finger_type == '09':
            cv2.imwrite('XXX/XXX/XXX.../dataset/09/'+man_type+'/'+finger,img)    # 修改為dataset的位置
            cv2.imwrite('XXX/XXX/XXX.../test_dataset/'+finger,img)               # 修改為test_dataset(輸入測試用)的位置

