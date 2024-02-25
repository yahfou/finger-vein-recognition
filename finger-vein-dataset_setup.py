import cv2
import numpy as np
import os
import skimage.filters as filters
from skimage import morphology




#--------------------------ROI 範圍設定----------------------------------------
imgx = 30    # 左上原點 x                                                    
imgy = 34    # 左上原點 y                                        

imgw = 620   # 寬                                                    
imgh = 175   # 高                                             
#------------------------------------------------------------------------------


array_of_img = []

lamd = 2.7961     

ural = 4.5644     


def read_directory(directory_name):
    
    for filename in os.listdir(directory_name):  
        img = cv2.imread(directory_name + "/" + filename)
        array_of_img.append(img)
        
        

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



rect_size = 20    # 重疊覆蓋範圍

brach = []


for f_type in range(2,10):
    
    if f_type == 5 or f_type == 6:
        continue 
    finger = str(f_type).zfill(2)
    
    for man_num in range(1, 61):
        man = str(man_num).zfill(3)
        read_directory('C:/Users/yahfou/Desktop/dataset/'+finger+'/'+ man )

        blank_image = np.zeros((141, 590, 3), dtype=np.uint8)
        blank_image1 = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
        blank_image2 = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
        blank_image3 = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
        blank_image4 = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
        blank_image5 = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
        
        
#------------------------------------特徵圖製作----------------------------------------------------------------------
        for yy, gdimg in enumerate(array_of_img):
            pimg = imgprcess(gdimg)
            retval, labels, stats, centroids = cv2.connectedComponentsWithStats(pimg, connectivity=8)  
            imbrp, branchpoints = search_branchpoints(pimg)
            brach.append(branchpoints)
            br_mean = np.mean(brach)
            
            blank_image = blank_image1 if yy == 0 else blank_image2 if yy == 1 \
                else blank_image3 if yy == 2 else blank_image4 if yy == 3 else blank_image5
                
            for i in range(imbrp.shape[0]):
                for j in range(imbrp.shape[1]):
                    if imbrp[i][j] != 0:    
                        x, y = j - rect_size // 2, i-rect_size // 2     
                        blank_image = cv2.rectangle(blank_image, (x, y), (x+rect_size, y+rect_size), 1, -1)
            if yy == 0:      
                cc = blank_image     
            else:      
                cc += blank_image

            BRP = cc >= 3*np.ones(np.shape(cc))    # 若重疊像素大於3則保留於特徵圖中
            BRP = BRP.astype(int)
            br_mean = int(br_mean)
            
        array_of_img.clear()
        
        cv2.imwrite('C:/Users/yahfou/Desktop/feature_dataset/'+man+'_'+finger+'_'+str(br_mean)+'.png',BRP)
#-------------------------------------------------------------------------------------------------------------------
    
