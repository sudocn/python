import os, os.path
#import xml.etree.ElementTree as ET
from common import extract_xml
import csv

res_root = r"C:\Documents and Settings\cpeng\Desktop\string-resources"
languages = ["values", "values-zh-rCN", "values-hi"]
fp = open("d:\\ttt.csv", mode="w", newline="", encoding="utf-8")
csv_writer = csv.writer(fp, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

def find_dirs(res_root):
    tmp = []
    for root, dirs, files in os.walk(res_root):
        if "values" in dirs:
            #print (os.path.relpath(root, res_root))
            tmp.append(os.path.relpath(root, res_root))
    return tmp

def find_files():
    for root, dirs, files in os.walk(res_root):
        for f in files:
            rel_path = os.path.relpath(root,res_root)
            abs_path = os.path.join(root, f)
            print(os.path.join(rel_path, f))

# 3 way dictionary merge 
def merge_dict3(dict0, dict1, dict2):
    dc = {}
    for key in dict0:
        dc[key] = [dict0[key], dict1.get(key,""), dict2.get(key,"")]    
    
    # strings exist in Non-English resources but no in 
    # English resource are obsoleted resources.
    for i,d in enumerate((dict1, dict2)):
        obsoleted = d.keys() - dict0.keys()
        if len(obsoleted) > 0:
            print("!!!Warning: unique string names in Non-English resources: " + languages[i+1])
            print(obsoleted)

    return dc
                
def process_app(base, res):
    flist = os.listdir(os.path.join(base, res, 'values'))
    print(flist)
    for f in flist:
        csv_writer.writerow([])
        csv_writer.writerow([res])
        csv_writer.writerow([f])
        # English
        abspath = os.path.join(base, res, "values", f)
        dict0 = extract_xml(abspath)
        # Chinese
        abspath = os.path.join(base, res, languages[1], f)
        dict1 = extract_xml(abspath)
        # Hindi
        abspath = os.path.join(base, res, languages[2], f)
        dict2 = extract_xml(abspath)
        
        dict_all = merge_dict3(dict0, dict1, dict2)
        for k in sorted(dict_all):
            it = dict_all[k]
            #print('%s, "%s", "%s", "%s"'%(k,it[0],it[1],it[2]), file=fp)
            #print(k,it, file=fp)
            csv_writer.writerow([k] + list(it))
        print(len(dict_all))
            
def main():
    #find_files()
    apps = find_dirs(res_root)
    for d in apps:
        print(d)
        #if "Camera" in d:
        process_app(res_root, d)
    #process_app(res_root, r"frameworks\base\core\res\res")
    fp.close()
       
if __name__ == "__main__":
    main()