import cost_function as cf
import pic_sk as pic
target_image = pic.pic2rgb("../data/img03.jpg", 50, 50)
cf.set_target_image(target_image)

s = "(H 0.7 (V 0.3 (L color) (V 0.5 (L color) (L color))) (L color))"
matrix = cf.to_array(s, 50, 50, 1)
print(matrix)
pic.rgb2pic(matrix)
