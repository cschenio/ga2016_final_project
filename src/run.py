import cost_function as cf
import genetic_programming as gp
import monte_carlo as mc
import pic

# global setting
x = 20
y = 20

target_image = pic.pic2rgb("../data/img03.jpg", x, y)
cf.set_target_image(target_image)

# gp

horizontal = gp.cut('H',2)
vertical = gp.cut('V',2)
env = gp.enviroment([horizontal, vertical], ["L color"],
                    target_image, size = 1000, maxcut = 6, maxdepth = 3)
s_gp, cost_gp = env.envolve(maxgen = 100)
print("Best solution in GP: ", cost_gp)
print(s_gp)
pic.rgb2pic(cf.to_array(s_gp, x, y, 1), 'LAB', "../data/output/img03_gp.png")

print("NFE(GP) = ", env.get_nfe())

# mc
# for i in range(1000):
#     s_mc, cost_mc = mc.monte_carlo(1, 15, target_image)
#     #print("Best solution in MC: ", cost_mc)
#     print(cost_mc)

#pic.rgb2pic(cf.to_array(s_mc, x, y, 1), 'LAB', "../data/output/img03_mc.png")
