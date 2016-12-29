from PIL import Image, ImageDraw
from sys import argv
import numpy as np
from skimage.color import lab2rgb, rgb2lab


def pic2rgb(filename, width = 100, height = 100):

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
    labcolor_img = rgb2lab(nim2)

    return labcolor_img
    

def rgb2pic(im_array, format='LAB'):

    ans_pic = "master_piece.jpg"
    rgb_img=[]
    row, col = len(im_array), len(im_array[0])
    
    if format != 'RGB':
        rgb_img=lab2rgb(im_array)
    rgb_img=np.array(rgb_img, dtype=np.uint8).reshape(row, col, 3)
    im = Image.fromarray(rgb_img,'RGB')
    im.save(ans_pic)
    
    print('save GA as: ',ans_pic)
    

#rgb2pic(pic2rgb("1.jpg"),'labcolor')