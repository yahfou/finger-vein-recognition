import cv2
import numpy as np
import os
import skimage.filters as filters
from skimage import morphology
import random
import re
from natsort import natsorted
import PySimpleGUI as sg


#--------------------------ROI 範圍設定----------------------------------------
imgx = 30    # 左上原點 x                                                    
imgy = 34    # 左上原點 y                                        

imgw = 620   # 寬                                                    
imgh = 175   # 高                                             
#------------------------------------------------------------------------------


array_of_img = {}

alpha = 55          # 匹配閾值，根據需求在錯誤接受和錯誤拒絕之間取捨

lamd = 2.7961       # 較小的銳化倍率

ural = 4.5644       # 較大的銳化倍率

con_th = 9.8886     # 控制第一次篩選寬鬆值(越大越寬鬆)
    



def read_directory(directory_name):
    
    for filename in natsorted(os.listdir(directory_name)):   
        img = cv2.imread(directory_name + "/" + filename,cv2.IMREAD_GRAYSCALE) 
        array_of_img[filename] = img
        

#------------------------------------------影像處理-----------------------------------------------------------------
clahe = cv2.createCLAHE(clipLimit=10.1, tileGridSize=(4,4)) 

def imgprcess(img):
    
    reimg = img[imgy:imgh, imgx:imgw]    # ROI截取                                  
    imgray = cv2.cvtColor(reimg,cv2.COLOR_RGB2GRAY)                          
    sharp = filters.unsharp_mask(imgray, radius=10.0,
                                  amount=lamd, multichannel=False,          
                                  preserve_range=False)
    sharp = (255*sharp).clip(0,255).astype(np.uint8)                      
    sharp_2 = filters.unsharp_mask(sharp, radius=10,
                                  amount=ural, multichannel=False,          
                                  preserve_range=False)
    sharp_2 = (255*sharp_2).clip(0,255).astype(np.uint8)                     
    bi_1 = cv2.bilateralFilter(sharp_2,5,50,50)
    clahe_img = clahe.apply(bi_1)  
    dilation = cv2.dilate(clahe_img, np.ones((2,2), np.uint8) , iterations = 1)
    sharp_3 = filters.unsharp_mask(dilation, radius=10,
                                  amount=lamd, multichannel=False,           
                                  preserve_range=False)
    sharp_3 = (255*sharp_3).clip(0,255).astype(np.uint8)                
    bi_2 = cv2.bilateralFilter(sharp_3,5,50,50)
    dilation_2 = cv2.dilate(bi_2, np.ones((2,2), np.uint8) , iterations = 2)   
    erode = cv2.erode(dilation_2, np.ones((3,3), np.uint8), iterations = 3)   
    dilation_3 = cv2.dilate(erode, (3,3), iterations = 3)                   
    sharp_4 = filters.unsharp_mask(dilation_3, radius=50,
                                  amount=lamd, multichannel=False,     
                                  preserve_range=False)
    sharp_4 = (255*sharp_4).clip(0,255).astype(np.uint8)              
    bi_3 = cv2.bilateralFilter(sharp_4,1,10,10)
    erode_2 = cv2.erode(bi_3, np.ones((3,3), np.uint8), iterations = 1)      
    blur = cv2.GaussianBlur(erode_2, (5, 5), 24)                          
    _,binary = cv2.threshold(blur,101,255,cv2.THRESH_BINARY_INV)           
    binary[binary==255] = 1                                                  
    skeleton0 = morphology.skeletonize(binary)                      
    skeleton = skeleton0.astype(np.uint8)       
                  
    return skeleton
#-------------------------------------------------------------------------------------------------------------------




#------------------------------------分支點檢測----------------------------------------------------------------------
def search_branchpoints(imskel):
    
    cx = [-1,-1, 0, 1, 1, 1, 0,-1,-1]
    cy = [ 0,-1,-1,-1, 0, 1, 1, 1, 0] 
    n_row, n_col = imskel.shape
    imbrp = np.zeros((n_row, n_col), dtype=np.uint8)
    branchpoints = 0
    for ix in range(1, n_row-1):  
        for iy in range(1, n_col-1):         
            if imskel[ix,iy] == 1:               
                COUNT = 0                
                for ic in range(8):                    
                    change = np.logical_xor(imskel[ix+cx[ic],iy+cy[ic]],                                            
                                            imskel[ix+cx[ic+1],iy+cy[ic+1]])
                    if change:                        
                        COUNT = COUNT + 1                        
                if COUNT >= 6:                    
                    imbrp[ix,iy] = 1                    
                    branchpoints = branchpoints + 1  
                    
    return imbrp, branchpoints
#-------------------------------------------------------------------------------------------------------------------


read_directory("XXX/XXX/XXX.../feature_dataset")    # 將此處路徑改為你設定的特徵圖資料庫路徑
read_test_directory = "XXX/XXX/XXX.../test_dataset"    # 將此處路徑改為你設定的測試資料庫路徑


rese = {}
e_rese = {}

FA = 0
FR = 0


#-------------------------------GUI設定-----------------------------------------------------------------------------
layout = [   
    [sg.Text("手指靜脈辨識器")],   
    [sg.Image(key="-IMAGE-")],  
    [sg.Button("載入靜脈圖像"),sg.Text("", size=(80, 1), key="-FILENAME-")],  
    [sg.Button('開始比對'),sg.Text("", size=(80, 1), key="-resu-")],
]
window = sg.Window("手指靜脈辨識器", layout)
#-------------------------------------------------------------------------------------------------------------------

while True:

    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    if event == "載入靜脈圖像":
        tfilename = random.choice(os.listdir(read_test_directory))
        timg = cv2.imread(os.path.join(read_test_directory, tfilename))         # 讀取測試圖像
        gui_img = cv2.imencode(".png", timg)[1].tobytes()
        window["-IMAGE-"].update(data=gui_img)
        window["-FILENAME-"].update('所選圖像為: '+ tfilename)
    elif event == '開始比對':
        teimg = imgprcess(timg)
        imbrp, branchpoints = search_branchpoints(teimg)
        rese.clear()
        e_rese.clear()
        imbrp, branchpoints = search_branchpoints(teimg)
        
        for filename, gdimg in array_of_img.items():    # 分支點重疊率差異度計算
            COUNT = np.sum(np.logical_and(imbrp, gdimg))
            con = 100*COUNT/branchpoints
            rese[filename] = con
            tmp = max(rese.values())
            con_les = tmp - con_th
            
        rese_th = {k:v for k,v in rese.items() if v > con_les and v <= tmp}

        for efilename, e_gdimg in rese_th.items():    # 提取匹配結果
            
            info_match = efilename
            info_match = re.findall('[0-9]{1,}' , info_match)
            brchpt = int(info_match[2])
            brre = branchpoints - brchpt
            abs_brre = abs(brre)
            e_rese[efilename] = abs_brre
            minJ = min(e_rese, key= e_rese.get)
            bestMatchName = re.findall('[0-9]{1,}' , minJ)
            mannumber = int(bestMatchName[0])
            man_finger = int(bestMatchName[1])
            title = re.findall('[0-9]{1,}' , tfilename)
            user_finger = title[3]
            int_user_finger = int(user_finger)
            user = title[2]
            ifuser = int(user)
            
            
#---------------------------------判斷邏輯--------------------------------------------------------------------------
        

        if tmp >= alpha and mannumber == ifuser and man_finger == int_user_finger:     # 正確接受
          
            window["-resu-"].update('比對結果: 正確接受')
            
        elif tmp < alpha and mannumber != ifuser and man_finger != int_user_finger:    # 正確拒絕
            
            window["-resu-"].update('比對結果: 錯誤拒絕')
        
        elif tmp >= alpha and mannumber != ifuser and man_finger != int_user_finger:   # 錯誤接受
            
            window["-resu-"].update('比對結果: 錯誤接受')
            
        elif tmp < alpha and mannumber == ifuser and man_finger == int_user_finger:    # 錯誤拒絕
        
            window["-resu-"].update('比對結果: 錯誤拒絕')

        elif tmp >= alpha and mannumber == ifuser and man_finger != int_user_finger:   # 錯誤接受
        
            window["-resu-"].update('比對結果: 錯誤接受')
            
        elif tmp >= alpha and mannumber != ifuser and man_finger == int_user_finger:   # 錯誤接受
        
            window["-resu-"].update('比對結果: 錯誤接受')
        
        elif tmp < alpha and mannumber != ifuser and man_finger == int_user_finger:    # 錯誤拒絕
            
            window["-resu-"].update('比對結果: 錯誤拒絕')

        elif tmp < alpha and mannumber == ifuser and man_finger != int_user_finger:    # 錯誤拒絕
        
            window["-resu-"].update('比對結果: 錯誤拒絕')
            
        else:
            window["-resu-"].update('比對結果: BUG')
            
#------------------------------------------------------------------------------------------------------------------

window.close()
