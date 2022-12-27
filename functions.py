import xml.etree.ElementTree as ET
import os
import copy

def write_file(filename: str):
    if os.path.exists(filename) :
        pass
        # open file to append
    else :
        pass
        # create a new file and write file header

def add_keys(node, parent_path) :
#    print("NODE: ", node.tag,":", node.text)
    leaf_level = "True"
    ET.SubElement(node,"path").text = parent_path
    local_keys = dict()
    for child in node :
        if not list(child) :
            print(child.tag, ":", child.text)
            local_keys[child.tag] = child.text
    for child in node :
        if list(child) :
#            for k in local_keys.keys() :
            print("non-leaf: ", child.tag)
#            print(len(local_keys))
            _, tag_tailer = child.tag.split("}")
            ET.SubElement(child,"path").text = parent_path + "_" + tag_tailer
            for k in local_keys.keys() :
#                print("aaa: ",k,":",local_keys[k])
                ET.SubElement(child, k).text = local_keys[k]
#            ET.dump(a)
#    ET.dump(node)
    for child in node :
        if list(child) :
            _, tag_tailer = child.tag.split("}")
            add_keys(child,parent_path+"_"+tag_tailer)
            leaf_level = False
    if leaf_level :
        print("leaf")
        ET.SubElement(node,"leaf_level").text = "True"
    else :
        ET.SubElement(node,"leaf_level").text = "False"

#        ET.dump(child)

tree_res = ET.parse("C:\\Scripts\\xml\\multi_response.xml")
root_res = tree_res.getroot()
#iter_root = root.iter()
#dict1 = {}

# skip most outer levels of xml
#while root_req and "managed-element" not in root_req.tag :
#     root_req = root_req[0]
while root_res and "managed-element" not in root_res.tag :
     root_res = root_res[0]

add_keys(root_res,"managed-element")

#ET.dump(root_res)