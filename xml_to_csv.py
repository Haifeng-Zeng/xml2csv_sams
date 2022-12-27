#import xml
import xml.etree.ElementTree as ET
import csv
#import sys
#import re


# v1.0



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

def add_dict(node, arr) :
    dict1 = dict()
    for child in node :
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

def write_file(directory, node) :
    search_path = ".//" + node.tag
    to_write = list()
    to_add = root_res.findall(search_path)
    
#    print(type(to_add),type(to_add[0]))
    for item in to_add :
        add_dict(item, to_write)
#        print("node added:",type(item),type(root_res))
        item.set("to_output", "Done")
    
        file_name = node.get("path") + "_" + node.tag
#       print(file_name)
        file_name = remove_ns(file_name)
#    print(file_name)
        file_name = directory + file_name + ".csv"
        file_name = file_name.replace("/","_")

#        print(type(to_write))
#        print(type(to_write[0]))

        with open(file_name, 'w') as csvfile:
            fieldnames = to_write[0].keys()
            writer = csv.writer(csvfile, dialect = "excel")
            #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            #writer.writeheader()
            writer.writerow(fieldnames)
            for d in to_write:
#                print(d.values())
                writer.writerow(d.values())  
    

#        ET.dump(child)

#tree_res = ET.parse("C:\\Scripts\\xml\\multi_response.xml")

tree_res = ET.parse("C:\\Scripts\\xml\\b.xml")

#ET.dump(root_res)
#sys.exit(0)
#iter_root = root.iter()
#dict1 = {}

#req_xml_file = "C:\\Scripts\\xml\\multi_request.xml"
#res_xml_file = "C:\\Scripts\\xml\\multi_response.xml"

tree_req = ET.parse("C:\\Scripts\\xml\\multi_request.xml")
#tree_res = ET.parse("C:\\Scripts\\xml\\multi_response.xml")
tree_res = ET.parse("C:\\Scripts\\xml\\b.xml")

root_req = tree_req.getroot()
root_res = tree_res.getroot()

# skip most outer levels of xml
#while root_req and "managed-element" not in root_req.tag :
#     root_req = root_req[0]
while root_res and "managed-element" not in root_res.tag :
     root_res = root_res[0]

#ET.dump(root_res)

#q_req = list()
#q_req.append(root_req)
#q_req.append("end")

# Add all available paramter to leaf level nodes; add path of every level; add to_output info
#add_keys(root_res,"managed-element",{})
add_keys(root_res,"", "", {})

#ET.dump(root_res)


#tree_res.write("C:\\Scripts\\xml\\c.xml")


q_res = list()
q_res.append(root_res)
while q_res :
    curr_p = q_res.pop(0)
    for child in curr_p :
        if child.get("to_output") == "False" :
            q_res.append(child)
        elif child.get("to_output") == "True" :
            write_file("C:\\Scripts\\xml\\", child)

#ET.dump(root_res)
