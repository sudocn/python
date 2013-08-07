import os, sys
import csv

branch_fname = r"z:\main-3.3.log"
main_fname = r"z:\3.3-main.log"
mantis_fname = r"C:\Documents and Settings\cpeng\Desktop\cpeng.csv"

def pr2mantis(pr, fname):
    with open(fname, mode="r", encoding="utf-8") as f:
        #f.seek(2) #skip BOM
        f.readline() # skip first line
        reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            id = int(row[0])
            if id in pr:
                print(id, row[1], row[3], row[15],sep=',')
    

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
    main = get_pr_list(main_fname)
    print(len(branch), branch)
    print(len(main), main)
    
    main_uniq = main - branch
    print("PRs in Main not in BRANCH:")
    print(len(main_uniq), main_uniq)

    branch_uniq = branch - main
    print("PRs in BRANCH not in MAIN:")
    print(len(branch_uniq), branch_uniq)
    
    common = main & branch
    print("PRs in both BRANCH and MAIN:")
    print(len(common), common)
    
    pr2mantis(main_uniq, mantis_fname)

if __name__ == "__main__":
    main()