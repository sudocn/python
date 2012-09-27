import os


isdbt_parser = r"C:\_Work\isdbt\isdbpar\debug\isdbpar.exe"
isdbt_stream = r"C:\Documents and Settings\cpeng\Desktop\ISDB-T"

def conv_file(dirname, fname):
#    print dirname, fname
    ext = os.path.splitext(fname)[1].lower()
    if ext == '.ts' or ext == '.trp':
        print fname
        cmd = isdbt_parser + ' "' + fname + '"'
        os.popen(cmd).readlines()
    
def walk(arg, dirname, fnames):
    os.chdir(dirname)
    for f in (fnames):
        conv_file(dirname, f)
    
outlist = []
def main():
#    os.chdir(isdbt_stream)
#    files = os.listdir(".")
#    recursive_list_files(isdbt_stream, outlist)
    print "ts files"
    os.path.walk(isdbt_stream, walk, "*fff*")
    
if __name__ == "__main__":
    main()
