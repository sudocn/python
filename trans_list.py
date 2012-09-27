#configures

Accept_New_Vars = False

#read input file
infile = open("c:\\_work\\filelist", 'r')
print infile
inlines = infile.readlines()
infile.close()

def comment(line):
#    return None
    return '#' + line

def brace(line):
    return '(' + line.rstrip() + ')'

def flaten(array):
    result = ''
    for l in array:
        result += " " + l
    return result.lstrip()

def relpace_environs(line, env):
    for k in env.keys():
        name = "$" + k
        if (name in line):
            line = line.replace(name, env[k])
        name = "${" + k + "}"
        if (name in line):
            line = line.replace(name, env[k])
        
    return line


in_if = False
outlines = []
environs ={"RELEASEPATH": "",
           "RELEASENAME": "MBX-Qtopia431-D2008-07-30-Fiji-Demo-Pre",
           "RELEASEMAKETMPPATH": ""}
for line in inlines:
    line = line.strip()
    
    if len(line) == 0 :
        out = ""
    elif line[0] == '#':
        out = line
    elif (line[0:3] == 'if '):
        out = comment(line)
        in_if = True
    elif (line[0:2] == 'fi'):    
        out = comment(line)
        in_if = False
#    elif in_if:
#        out = comment(line)
    elif line[0:3] == 'cd ':
        out = comment(line)
    elif "=" in line:  #assignment
        out = line
        if Accept_New_Vars:
            arr = line.split("=")
            environs[arr[0].strip()] = relpace_environs(arr[1].strip(), environs)
    else:
        arr = line.split()
        if arr[0] == 'cp':
            arr.pop(0)
            if arr[0][0] == '-': arr.pop(0)
            out = flaten(arr)
        else:
            out = brace(line)

        out = relpace_environs(out, environs)

    outlines.append(out)

print environs

#output to file
outfile = open("c:\\_work\\filelist2", 'w')
for line in outlines:
    if not (line is None): outfile.write(line + "\n")
outfile.close()

