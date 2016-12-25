from PIL import Image, ImageDraw
from sys import argv
import numpy as np
from colormath.color_objects import sRGBColor, LabColor, XYZColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

def pic2rgb(filename):

    width = 100
    height = 100
    new_pic = "resized.jpg"
    
    im = Image.open(filename)
    print ('input pic: ', im.format, im.size, im.mode)
    if im.mode!='RGB': 
        print('Please use RGB format picture.')
        quit()


    nim2 = im.resize( (width, height), Image.BILINEAR )
    nim2.save(new_pic)
    nim2 = Image.open(new_pic)
    print ('conver to: ', nim2.format, nim2.size, nim2.mode)
    print('save as: %s'%new_pic, '\n')
    
    nim2=np.asarray(nim2)
    row, col = len(nim2), len(nim2[0])
    labcolor_img=[]
    
    for i in range(row):
        for j in range(col):
            labcolor_img.append(convert_color(sRGBColor(nim2[i][j][0], nim2[i][j][1], nim2[i][j][2], True), LabColor))
        
    labcolor_img = np.array(labcolor_img).reshape(row, col)

    return labcolor_img

def rgb2pic(im_array, filename):
    ans_pic = filename
    im = Image.fromarray(im_array,'RGB')
    im.save(ans_pic)
    print('save GA as: ',ans_pic)
