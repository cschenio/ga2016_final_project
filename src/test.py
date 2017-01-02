import cost_function as cf
import pic
target_image = pic.pic2rgb("../data/img03.jpg", 50, 50)
cf.set_target_image(target_image)
s = "(H 0.73 (V 0.451 (H 0.963 (L color)(L color))(V 0.549 (L color)(L color)))(L color))"
matrix = cf.to_array(s, 50, 50, 1)
#print(matrix)
pic.rgb2pic(matrix, 'LAB', "./master_piece.png")
