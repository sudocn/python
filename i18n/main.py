import os, sys, os.path
import xml.etree.ElementTree as ET
#from tempfile import TemporaryFile 
#from xml.sax.saxutils import unescape
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

def normalize_text(text):
    if text is None:
        return ""
    if text.startswith('"'):
        text = text[1:]
    if text.endswith('"'):
        text = text[:-1]
    # join multiple lines
    text = text.replace('\r', '\n')
    text = text.replace('\n', '')
    return text

def extract_text(e, parent_name, dc):
    if len(e) == 0: # No sub-element
        return normalize_text(e.text)
    else:
        if e.tag == "string":
            #print(e.attrib["name"] + " " + str(len(e)))
            pass
        elif e.tag == "item":
            #print(parent_name + " " + str(len(e)))
            pass  
        # xliff parsing
        '''
        for sub in e:
            if sub.tag in ("font", "b", "u") : continue
            index = 0
            try:
                name = parent_name + ".xliff." + sub.attrib["id"].lower()
            except:
                print(ET.tostring(e))
                name = parent_name + ".xliff." + str(index)
                index += 1
            #print(name)
            dc[name] = normalize_text(sub.tail)
        '''
        text = ET.tostring(e, encoding="unicode")
        start = text.index(">")
        end = text.rindex("<")
        text = text[start+1:end]
        #print(text)
        return normalize_text(text)
    
"""
    <plurals name="in_num_hours">
        <item quantity="one">in 1 hour</item>
        <item quantity="other">in <xliff:g id="count">%d</xliff:g> hours</item>
    </plurals>
"""
def do_plurals(e, dc):
    prefix = "plurals." + e.attrib["name"]
    for item in e:
        if item.tag == "item":
            name = prefix + "." + item.attrib["quantity"]
            text = extract_text(item, name, dc)
            dc[name] = text
"""
    <string-array name="postalAddressTypes">
        <item>Home</item>
        <item>Work</item>
        <item>Other</item>
        <item>Custom</item>
    </string-array>
"""
def do_string_array(e, dc):
    prefix = "array." + e.attrib["name"]
    index = 0
    for item in e:
        if item.tag == "item":
            name = prefix + "." + str(index)
            text = extract_text(item, name, dc)
            index += 1
            dc[name] = text

"""
    <string name="fcComplete">Feature code complete.</string>
    <string name="cfTemplateForwardedTime"><xliff:g id="bearer_service_code">{0}</xliff:g>: <xliff:g id="dialing_number">{1}</xliff:g> after <xliff:g id="time_delay">{2}</xliff:g> seconds</string>
"""
def do_string(e, dc):
    name = e.attrib["name"]
    text = extract_text(e, name, dc)
    """
    multiple string with the same "name",
    use "product" key to distinguish it

    <string name="app_label" product="tablet">Mobile Network Configuration</string>
    <string name="app_label" product="default">Phone/Messaging Storage</string>
    """    
    if "product" in e.attrib:
        name += ".product." + e.attrib["product"]
    #print(name, text)
    if name in dc:
        print("!!!Warnning: duplicate name: ", name)
    if len(text) == 0:
        pass#print("!!!Warnning: key %s has no text content" % name)
        
    #continue
    dc[name] = text

def extract_xml(f):
    print("processing ", f)
    if not os.path.exists(f):
        return {}
    
    dc = {}
    tree = ET.parse(f)
    root = tree.getroot()
    for child in root:
        if child.tag == "string":
            do_string(child, dc)
        if child.tag == "string-array":
            do_string_array(child, dc)
        if child.tag == "plurals":
            do_plurals(child, dc)
    return dc

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
        print("!!!Error: uniq string names ni Non-Englisth resources")
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