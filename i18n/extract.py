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
def merge_dicts(*dicts):
    dc = {}
    for key in dicts[0]:
        dc[key] = [x.get(key,"") for x in dicts]    
    
    # strings exist in Non-English resources but no in 
    # English resource are obsoleted resources.
    for i,d in enumerate(dicts[1:]):
        obsoleted = d.keys() - dicts[0].keys()
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

        dicts = []
        for lang in languages:
            abspath = os.path.join(base, res, lang, f)
            dicts.append(extract_xml(abspath))

        '''
        abspath = os.path.join(base, res, languages[1], f)
        dict1 = extract_xml(abspath)

        abspath = os.path.join(base, res, languages[2], f)
        dict2 = extract_xml(abspath)
        '''
           
        dict_all = merge_dicts(*dicts)
        for k in sorted(dict_all.keys()):
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