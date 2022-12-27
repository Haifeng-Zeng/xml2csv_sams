
import xml.etree.ElementTree as ET
import csv
import sys
#import xml.dom.minidom as pretty
#import re


# v2.0 add comparation to request data



# output columns should be same as request
# there might be special charachters in output


def add_keys(node, parent_path, parent_tag, carry_in) :
     # add all parameters to leaf level
     # add 2 attributes: "path" indicates the hierarchy level; "to_output" indicates if children of this node should be printed, values are: "True", "False", "Done"

    to_output = "True"
    local_keys = dict()
    
    # update path info of current level
    
    current_path = parent_path + "/" + parent_tag
    node.set("path", current_path)

    # Add parameters from parent to current level
    index = 0
    for k in carry_in.keys() :
        ele = ET.Element(k)
        ele.text = carry_in[k]
#        print("new node")
#        ET.dump(ele)
        node.insert(index,ele)
        index += 1
#        ET.SubElement(node, k).text = carry_in[k]

    
    # Read all parameters of current level
    for child in node :
        if list(child) :
            to_output = "False"
        else :
            local_keys[child.tag] = child.text
    
    node.set("to_output", to_output)

    for child in node :
        if list(child) :
            add_keys(child, current_path, node.tag, local_keys)
#    ET.dump(node)
#    print("Aaaa")

def add_dict(node, arr) :
    dict1 = dict()
    for child in node :
#        if child.get("to_output") == "True" :
        dict1[remove_ns(child.tag)] = child.text
    arr.append(dict1)

def remove_ns(source) :
    target = ""
    output = True
    for ch in source :
        if ch != "}" and not output :
            continue
        if ch == "{" :
            output = False
        elif ch == "}" :
            output = True
        else :
            target += ch
    return target

def write_file(node) :
    if node.get("to_output") != "True" :
#        if node.get("to_output") != "False" :
#            print("Found False: ", node.tag)
        return
    if "report-config-entries" not in node.get("path") :
        return
    
    to_write = list()
    
    #Find by tag
    search_tag = ".//" + node.tag
    to_add = root_res.findall(search_tag)

    # get attribute "path" of node
    search_path = node.get("path")

    for item in to_add :
        if item.get("to_output") == "True" and item.get("path") == search_path :
            add_dict(item, to_write)
#        print("node added:",type(item),type(root_res))
            item.set("to_output", "Done")
    
    file_name = node.get("path") + "_" + node.tag
    file_name = remove_ns(file_name)
    file_name = file_name + ".csv"
    file_name = file_name.replace("/","_")

#    print(file_name)
#    print(type(to_write[0]))

    full_keys = set()

# Add missing keys if the key is missing
    for item in to_write :
        full_keys = full_keys.union(set(item.keys()))
    
    for item in to_write :
        current_keys = set(item.keys())
        for k in full_keys.difference(current_keys) :
            item[k] = ""

    with open(file_name, 'w', newline = "", encoding="utf-8") as csvfile:
        # use dictWriter, on python 3
        #writer = csv.DictWriter(csvfile, fieldnames=to_write[0].keys())
        #writer.writeheader()
        #writer.writerows(to_write)

        # use dictWriter, on python 2.6.6
        fileds = list(to_write[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fileds)
        #writer.writerow(fileds)
        writer.writerows(to_write)

    
def merge_keys_req(node_res, node_req) :

    res_set = set()
    req_set = set()
    for child in node_res :
        if list(child) :
            merge_keys_req(child, node_req)
        else :
            res_set.add(child.tag)
    
    for item in node_req.iter(node_res.tag) :
        if item.tag == node_res.tag :
            break
    for child in item :
        if not list(child) :
            req_set.add(child.tag)
    #print(item.tag)
    
    #print(len(res_set), len(req_set))
    #print("res_set: ", res_set)
    #print("req_set: ",req_set)
    for item in req_set.difference(res_set) :
        ele = ET.Element(item)
        ele.text = "_"
        node_res.append(ele)
    
    

req_enabled = False
req_file = ""

'''
if len(sys.argv) < 2 :
    print("Usage:\n", sys.argv[0], "<response file> [request command file]\n")
    sys.exit(0)
elif len(sys.argv) == 2 :
    res_file = sys.argv[1]
elif len(sys.argv) == 3 :
    req_file == sys.argv[2]
    req_enabled = True
else :
    print("Only tow parameters are allowed at most")
    sys.exit(0)
'''

#req_file = "C:\\Scripts\\xml\\multi_request.xml"
res_file = "C:\\Scripts\\xml\\b.xml"
#es_file = "C:\\Scripts\\xml\\EastSyracuseMedium1USM_ACPF_71910100.xml"

tree_res = ET.parse(res_file)

root_res = tree_res.getroot()

# Add all available paramter to leaf level nodes; add path of every level; add to_output info


# skip most outer levels of xml until "Managed-Element" id reached
while root_res and "managed-element" not in root_res.tag :
     root_res = root_res[0]
tree_res = ET.ElementTree(root_res)
root_res = tree_res.getroot()

add_keys(root_res,"", "", {})
#tree_res.write("C:\\Scripts\\xml\\a.xml")
#dom = pretty.parse("C:\\Scripts\\xml\\a.xml")
#pretty_xml_as_string = dom.toprettyxml()


if req_enabled :
    tree_req = ET.parse(req_file)
    root_req = tree_req.getroot()
    while root_req and "managed-element" not in root_req.tag :
        root_req = root_req[0]
    tree_req = ET.ElementTree(root_req)
    add_keys(root_req,"", "", {})
    merge_keys_req(root_res,root_req)

#ET.dump(tree_res)

q_res = list()
q_res.append(root_res)
while q_res :
    curr_p = q_res.pop(0)
    for child in curr_p :
        if child.get("to_output") == "Done" :
#            print(child.tag, child.get("to_output"), " had been written")
            continue
        elif child.get("to_output") == "False" :
#            print("Add to queue:", child.tag, child.get("to_output"))
            q_res.append(child)
        elif child.get("to_output") == "True" :
            write_file(child)
 
#tree_res.write("C:\\Scripts\\xml\\a.xml")



#print(pretty_xml_as_string)