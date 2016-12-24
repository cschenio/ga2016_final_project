from PIL import Image, ImageDraw
from sys import argv
import numpy as np

def pic2rgb(filename, width=400, height=400):
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

    im_array=np.asarray(nim2)
    print('numpy array shape: ',im_array.shape)
    #print('Example: the first row','\n')
    #print(im_array)
    return im_array

def rgb2pic(im_array, filename):
    ans_pic = filename
    im = Image.fromarray(im_array,'RGB')
    im.save(ans_pic)
    print('save GA as: ',ans_pic)
