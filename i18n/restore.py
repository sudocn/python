import os, sys, os.path
#import xml.etree.ElementTree as ET
from lxml import etree
from common import extract_xml
import csv

orig_root = r"C:\Documents and Settings\cpeng\Desktop\string-resources"
out_root =  r"C:\Documents and Settings\cpeng\Desktop\out-resources"
translated_text=r"D:\translation 20130606-Hindi.txt"

def translate_element(e, dc):
    def do_string(e, dc):
        name = e.attrib["name"]
        if name not in dc:
            return False
        
        if len(e) == 0:  #simple string
            e.text = dc.get(name)
        else:
            xml = dc.get(name)
            text = etree.tostring(e, encoding ="unicode", method="xml")
            start = text.index(">")
            end = text.rindex("<")
            text = text[:start+1] + xml + text[end:]
            new = etree.XML(text)
            
            for s in e:
                e.remove(s)
            e.extend(list(new))
        return True
    
    def do_string_array(e, dc):
        print("string array not implemented!")
        pass
    
    def do_plurals(e, dc):
        print("plurals not implemented!")
        pass

    if e.tag == "string":
        do_string(e, dc)
    if e.tag == "string-array":
        do_string_array(e, dc)
    if e.tag == "plurals":
        do_plurals(e, dc)     
    
def full_translate(inpath, outpath, dc):
    tree = etree.parse(inpath)
    for child in tree.getroot():
        translate_element(child, dc)

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    tree.write(outpath, encoding="utf-8", xml_declaration=True, method="xml")
                
def partial_translate(inpath, refpath, outpath, dc):
    dict_in = extract_xml(inpath)
    dict_ref = extract_xml(refpath)
    key_ref = dict_ref.keys()
    
    inc = dc.keys() - key_ref    
    identical = set()
    for k in inc:
        if dc[k] == dict_in[k]:
            identical.add(k)
    
    inc -= identical
    if len(inc) == 0:
        print("No new translations added, skip")
        return
            
    print(len(inc), inc)

    def find_elem_by_id(tree, id):
        e = None
        if "." in id: # needs transform
            if ".product." in id:
                ss = id.split(".", 3)
                xpath = "string[@name='%s'][@product='%s']"% (ss[0],ss[2])
                e = tree.find(xpath)
            elif id.startswith("array."):
                ss = id.split(".", 3)
                xpath = "string-array[@name='%s']"%ss[1]
                e = tree.find(xpath)
            elif id.startswith("plurals."):
                #TODO
                print("!!! ERROR: plurals not supported yet !!!")
            else:
                print("!!! complex representation !!! " + id)
        else:
            xpath = "string[@name='%s']"%id
            e = tree.find(xpath)
        return e
    
    appendix = []        
    tree1 = etree.parse(inpath)
    for id in inc:
        elem = find_elem_by_id(tree1, id)
        if not elem is None:
            appendix.append(elem)
    
    for e in appendix:
        pass#translate_element(e, dc)
                
    tree2 = etree.parse(refpath)
    tree2.getroot().extend(appendix)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    tree2.write(outpath, encoding="utf-8", xml_declaration=True, method="xml")
   
    
def main():
    etree.register_namespace("xliff", "urn:oasis:names:tc:xliff:document:1.2")
    cur_dir = cur_file = ""
    with open(translated_text, mode="r", encoding="utf-16-le") as f:
        f.seek(2) #skip BOM
        reader = csv.reader(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #read_one(f)
        state = 0
        vocabulary = {}
        for row in reader:
            #print(row[0])
            id, content = row
            if state < 2:
                if state == 0: cur_dir = row[0]
                if state == 1: cur_file = row[0]
                state += 1
                continue
            
            if len(id) == 0: # end of a translation section 
                #print(os.path.join(cur_dir, cur_file))
                inpath = os.path.join(orig_root,cur_dir, "values", cur_file)
                refpath = os.path.join(orig_root,cur_dir, "values-hi", cur_file)
                outpath = os.path.join(out_root,cur_dir, "values-hi", cur_file)
                print(inpath)
                print(outpath)
                if os.path.exists(refpath):
                    partial_translate(inpath, refpath, outpath, vocabulary)
                else:
                    full_translate(inpath, outpath, vocabulary)
                
                '''
                Clear states
                '''
                state = 0
                vocabulary = {}
                print()
            elif len(content) == 0:
                print(id + " has no content")
            else:
                vocabulary[id] = content

if __name__ == "__main__":
    main()