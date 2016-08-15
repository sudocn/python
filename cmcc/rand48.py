import sys

def_seed = [0x330e, 0xabcd, 0x1234]
def_mult = [0xe66d, 0xdeec, 0x0005]
def_add  = 0x000b

rand48_seed = [0x330e, 0xabcd, 0x1234]
rand48_mult = [0xe66d, 0xdeec, 0x0005]
rand48_add = def_add

def srand48(seed):
    seed[0] = def_seed[0]
    seed[1] = seed % 65536
    seed[2] = seed[1] / 65536
    mult[0] = def_mult[0]
    mult[1] = def_mult[1]
    mult[2] = def_mult[2]
    add = def_add

def lrand48():
    dorand48(rand48_seed)
    result = rand48_seed[2] * 32768 + rand48_seed[1] / 2
    return result

def dorand48(xseed):
    temp= [0,0]
    accu = rand48_mult[0] * xseed[0] + rand48_add
    temp[0] = accu % 65536
    accu >>= 16
    accu += rand48_mult[0] * xseed[1] + rand48_mult[1] * xseed[0]
    temp[1] = accu % 65536
    accu >>= 16
    accu += rand48_mult[0] * xseed[2] + rand48_mult[1] * xseed[1] + rand48_mult[2] * xseed[0]
    xseed[0] = temp[0]
    xseed[1] = temp[1]
    xseed[2] = accu % 65536


def test():
    for i in range(0,10):
        print "%x" % lrand48()

if __name__ == "__main__":
    test()