import os, os.path
#import xml.etree.ElementTree as ET
from common import extract_xml
import csv

res_root = r"C:\Documents and Settings\cpeng\Desktop\string-resources"
language_array = ["values", "values-zh-rCN", "values-hi"]
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
def merge_dict3(dict1, dict2, dict3):
    dc = {}
    for key in dict1:
        v1 = dict1[key]
        if key in dict2: 
            v2 = dict2[key]
            del dict2[key] 
        else: 
            v2 = ""
        if key in dict3: 
            v3 = dict3[key]
            del dict3[key] 
        else: 
            v3 = ""
        dc[key] = [v1, v2, v3]    
    
    if len(dict2) > 0 or len(dict3) > 0:
        print("!!!Warning: unique string names in Non-English resources")
        if len(dict2) > 0: print(dict2.keys())
        if len(dict3) > 0: print(dict3.keys())
    return dc
                
def process_app(base, res):
    csv_writer.writerow([])
    csv_writer.writerow([res])
    flist = os.listdir(os.path.join(base, res, 'values'))
    print(flist)
    for f in flist:
        csv_writer.writerow([f])
        # English
        abspath = os.path.join(base, res, "values", f)
        dict_en = extract_xml(abspath)
        # Chinese
        abspath = os.path.join(base, res, "values-zh-rCN", f)
        dict_zh = extract_xml(abspath)
        # Hindi
        abspath = os.path.join(base, res, "values-hi", f)
        dict_hi = extract_xml(abspath)
        
        dict_all = merge_dict3(dict_en, dict_zh, dict_hi)
        for k in dict_all:
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
        process_app(res_root, d)
    #process_app(res_root, r"frameworks\base\core\res\res")
    fp.close()
       
if __name__ == "__main__":
    main()