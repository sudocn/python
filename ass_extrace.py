# extract text from .ass video sub file
import sys
filename = "/Users/cpeng/Downloads/230616/Secret.Garden.E01.720p.HDTV.x264.ass"
def main(fname):
    with open(fname,"r") as f:
        begin = False
        while True > 0:
            if not begin:
                line1 = f.readline()
                if not line1.startswith("[Events]"):
                    continue
                f.readline()
                begin = True

            line1 = f.readline()
            line2 = f.readline()

            arr1 = line1.split(",", 9)
            arr2 = line2.split(",", 9)

            while (arr1[1] != arr2[1]):
                print(">> %s" % arr1[9].strip())
                line1 = line2
                line2 = f.readline()
                arr1 = line1.split(",", 9)
                arr2 = line2.split(",", 9)


            if (arr1[1] == arr2[1]):
                print("%s" % arr2[9].strip())
                print("%s" % arr1[9].strip())
                print

            if len(line1) == 0:
                break


if __name__ == "__main__":
    main(filename)
