from collections import OrderedDict


aa = OrderedDict()

aa[7] = 8
aa[8] = 28
aa[29] = 239
aa[33] = [2,5,6]

bb = {}

bb[7] = 9
bb[20] = 28

print(aa)
print(bb)

print(aa[33][2])