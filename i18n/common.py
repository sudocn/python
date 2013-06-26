import os.path
import xml.etree.ElementTree as ET

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
    ET.register_namespace("xliff", "urn:oasis:names:tc:xliff:document:1.2")
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
