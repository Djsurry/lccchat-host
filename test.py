x = 22
print("\nOriginal Number: ", x)
print("Left aligned (width 10)   :"+"{:< 76d}".format(x));
print("Right aligned (width 10)  :"+"{:76d}".format(x));
print("Center aligned (width 10) :"+"{:^76d}".format(x));
print()
