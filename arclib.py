import os

def extract(fullname):    
    ar = "ararc.exe "
    os.chdir(os.path.dirname(fullname))
    ofiles = os.popen(ar + " t " + fullname).readlines()
    #print ofiles
    ofiles = map(lambda x: x.strip(), ofiles)
    #print ofiles
    ofiles =  filter(lambda x: x.endswith(".o"), ofiles)
    #print ofiles

    print "total %d .o files" % len(ofiles)
    for o in ofiles:
        print o
        os.popen(ar + " x " + fullname + " " + o).readlines()
    os.remove(fullname)
    return ofiles

# extract all files for .a archive
def ar_x(afile):
    base = os.path.basename(afile)
    path, ext = os.path.splitext(afile)
    fullname = os.path.join(path, base)
    print "path %s"%(path)
    os.mkdir(path)
    os.popen("copy " + afile + " " + fullname).readlines()
    ofiles = extract(fullname)
    return path,ofiles

# replace objs in .a archive
def ar_r(path, archive, objs):
    ar = "ararc.exe -r "
    os.chdir(path)
    print "Archiving: ",
    for obj in objs:
        print obj,
        os.popen(ar + archive + " " + obj)
        

def compare(a, b):
    import filecmp
    files = os.listdir(a)
    #print files
    for o in files:
        #print "comparing %s..." % o ,
        if not filecmp.cmp(os.path.join(a,o), os.path.join(b,o)):
            print o , "not same"
        else:
            print "remove same file %s" % o
            os.remove(os.path.join(a,o))
            os.remove(os.path.join(b,o))                      

# disassemble all .o files in path
def disassemble(path):
    files = os.listdir(path)
    files =  filter(lambda x: x.endswith(".o"), files)
    os.chdir(path)
    for o in files:
        os.popen("elfdumparc.exe -T " + o + " > " + o + ".asm").readlines()
        
def _strip_single_file(fullname):
    strip = "striparc.exe"
    os.chdir(os.path.dirname(fullname))
    os.popen(strip + " -ld " + fullname).readlines()

def strip(path, objs):
    print "Striping: ",
    for obj in objs:
        print obj,
        _strip_single_file(os.path.join(path, obj))
    print "Done."

if __name__ == "__main__":
#    ar(r"c:\sti_gps_lib_0625.a")

    ar_x(r"c:\sti_gps_lib.a")
#    ar_x(r"c:\sti_gps_lib_0629.a")
#    compare(r"c:\sti_gps_lib_0629", r"c:\sti_gps_lib_0625_2")
    disassemble(r"c:\sti_gps_lib")
#    disassemble(r"c:\sti_gps_lib_0625_2")
    '''
    (path,objs) = ar_x(r"c:\libProtocolStack.a")
    strip(path, objs)
    ar_r(path, "libProtocolStack_strpped.a", objs)
    '''
    
