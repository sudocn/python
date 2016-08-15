import os, sys
import csv

branch_fname = r"z:\after24.txt"
mantis_fname = r"C:\Documents and Settings\cpeng\Desktop\cpeng.csv"

def pr2mantis(pr, fname):
    pr_copy = list(pr)[:]
    with open(fname, mode="r", encoding="utf-8") as f:
        #f.seek(2) #skip BOM
        f.readline() # skip first line
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            id = int(row[0])
            if id in pr_copy:
                print(id, row[1], row[3], row[15],sep=',')
                pr_copy.remove(id)
                
    if len(pr_copy) > 0:
        print("Those ", len(pr_copy), "ids not found: ", pr_copy)

def get_pr_list(fname):
    pr = []
    with open(fname, "r", encoding="utf-8") as f:
        for line in f:
            if (not "[PR]" in line) and (not "[CR]" in line): continue
            start = line.index(":") + 1
            end = line.index("[DESCRIPTION")            
            #rint(line[start:end], end="")
            pr.append(int(line[start:end]))
    print(pr)
    return set(pr)
    
def main():
    branch = get_pr_list(branch_fname)

    print(len(branch), branch)
    
    pr2mantis(branch, mantis_fname)

if __name__ == "__main__":
    main()