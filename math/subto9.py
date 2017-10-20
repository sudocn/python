

def calc(num):
    a = int(num)
    b = int(str(num)[::-1])
    # print a, b
    if a > b:
        print a, " - ", b, " = ", a - b
        return a - b
    elif a < b:
        print b, " - ", a, " = ", b - a
        return b - a
    else:
        print "Final:", a
        return 0

num = input("Please input your number: ")


num = calc(num)
while num != 0:
    num = calc(num)
