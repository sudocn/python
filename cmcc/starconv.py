import sys, base64

cmcc_c1="9e88MXQ3K1yTPuHo4gUId0ncM7eL5yB9ou5DySuF9YCuXSUQnYt4dLVanKpsHOcUhfC45oV5K2RlUA8IPwBlKw=="

def print_raw(raw):
    index=0
    for c in raw:
        #print str(int(c))
        sys.stdout.write("%02x " % (ord(c)))
        index += 1
        if (index % 8) == 0:
            if (index % 16) == 0:
                sys.stdout.write("\n")
            else:
                sys.stdout.write("- ")

def aes_cbc_decode(msg):
    raw=[]
    raw = base64.standard_b64decode(cmcc_c1)
    print_raw(raw)
    print base64.standard_b64encode(raw)


def main():
    aes_cbc_decode(cmcc_c1)
    print "pycharm is wonderful!"

if __name__ == '__main__':
    main()