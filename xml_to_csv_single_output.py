
import xml.etree.ElementTree as ET
import csv
import sys
#import xml.dom.minidom as pretty
#import re

# v2.0 add comparation to request data



# output columns should be same as request
# there might be special charachters in output


def add_keys(node, parent_path, parent_tag, carry_in) :
     # add all parameters to all level
     # add 3 attributes: "path" indicates the hierarchy level; "shortPath" id path without NS; "to_output" indicates if children of this node should be printed, values are: "True", "False", "Done"

    if not list(node) :
        return

    leaf_branch = True
    local_keys = dict()
    
    # find if current level is leaf branch
    for child in node :
        if list(child) :
            leaf_branch = False
            break
    
    # update path info of current level
    current_path = parent_path + "/" + node.tag
 
    node.set("path", current_path)
    node.set("shortPath",remove_ns(current_path))
    #print("general: ", node.get("shortPath"))

    # Add parameters from parent to current level
    if not leaf_branch :
        node.set("to_output", "False") 
        index = 0
        for k in carry_in.keys() :
            ele = ET.Element(k)
            ele.text = carry_in[k]
            node.insert(index,ele)
            index += 1
        for child in node :
            if list(child) :
                continue
            local_keys[child.tag] = child.text
        for child in node :
            if list(child) :
                add_keys(child, current_path, node.tag, local_keys)
        return

    # if current branch is a leaf branch
    node.set("to_output", "True")
    #print(node.tag,node.get("shortPath"))
    index = 0
    for k in carry_in.keys() :
        ele = ET.Element(k)
        ele.text = carry_in[k]
        ele.set("to_output","inherited")
        ele.set("path", current_path+"/"+ele.tag)
        ele.set("shortPath",remove_ns(current_path+"/"+ele.tag))
        node.insert(index,ele)
        index += 1
    for child in node :
        if not child.get("to_output") :
            child.set("to_output","True")
            child.set("path", current_path+"/"+child.tag)
            child.set("shortPath",remove_ns(current_path+"/"+child.tag))

def add_dict(node, arr) :
    
    if not list(node) :
        return
    if not node.get("to_output") or node.get("to_output") == "False":
        for child in node :
            add_dict(child, arr)
    
    dict1 = dict()
    for k in para_list :
        dict1[k] = ""
    
    for child in node :
        l1 = child.get("shortPath")
        if l1 :
            l2 = l1.split("/")
            l3 = l2[-1]
            if l3 in para_list :
                if dict1[l3] != "" :
                    dict1[l3] = child.text
                else :
                    arr.append(dict1)
            
def add_dict2(node, arr) :
    
    queue = list()
    queue.append(node)
    while queue :
        p = queue.pop(0)
        if not list(p) :
            continue
        if not p.get("to_output") or p.get("to_output") == "False":
            for child in p :
                queue.append(child)
            continue
        dict1 = dict()
        to_add = False
        for k in para_list :
            dict1[k] = ""
    
        for child in p :
            l1 = child.get("shortPath")
            if l1 :
                l2 = l1.split("/")
                l3 = l2[-1]
                if l3 in para_list :
                    dict1[l3] = child.text
                    if child.get("to_output") == "True" :
                        to_add = True
        if to_add :
#            print("add: ", dict1)
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

def write_file(write_list, file_name) :

    with open(file_name, 'w', newline = "", encoding="utf-8") as csvfile:
        # use dictWriter, on python 3
        writer = csv.DictWriter(csvfile, fieldnames=write_list[0].keys())
        writer.writeheader()
        writer.writerows(write_list)

        # use dictWriter, on python 2.6.6
#        fileds = list(write_list[0].keys())
#        print(fileds)
#        writer = csv.DictWriter(csvfile, fieldnames=fileds)
#        writer.writerow(fileds)
#        writer.writerows(write_list)

    
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
    
def collect_all_para(node, output_list):
    
    if not list(node) :
        return
    
    if not node.get("to_output") or node.get("to_output") == "False" :
        for child in node :
            collect_all_para(child, output_list)
    
    
    if node.get("to_output") == "True" :
        key = node.get("path")
        if key not in all_para.keys() :
            all_para[key] = []
            short_para[key] = []
#        print(all_para[key])
        for child in node :
            if child.get("path") in all_para[key] :
                continue
            for line in output_list :
                if line in child.get("shortPath") :
                    all_para[key].append(child.get("path"))
                    short_para[key].append(child.get("shortPath"))


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
#res_file = "C:\\Scripts\\xml\\b.xml"
res_file = "C:\\Scripts\\xml\\data\\RochesterMedium1USM_ACPF_70900100.xml"
#res_file = "C:\\Users\\user\\WorkSamsung\\xml\\data\\RochesterMedium1USM_ACPF_70900100.xml"
#res_file = "C:\\Users\\user\\WorkSamsung\\xml\\b.xml"
output_conf_file = "C:\\Scripts\\xml\\output.conf"
#output_conf_file = "C:\\Users\\user\\WorkSamsung\\xml\\output.conf"
tree_res = ET.parse(res_file)

output_file_name = "C:\\Scripts\\xml\\result.csv"

root_res = tree_res.getroot()

# Add all available paramter to leaf level nodes; add path of every level; add to_output info


# skip most outer levels of xml until "Managed-Element" id reached
while root_res and "managed-element" not in root_res.tag :
     root_res = root_res[0]
tree_res = ET.ElementTree(root_res)
root_res = tree_res.getroot()


all_para = dict()
short_para = dict()
output_conf_list = list()
f = open(output_conf_file,"r")
output_conf_list = f.readlines()
for i in range(len(output_conf_list)) :
    output_conf_list[i] = output_conf_list[i].strip()


#print(output_list)

add_keys(root_res,"", "", {})
#ET.dump(root_res)
collect_all_para(root_res, output_conf_list)
#print(output_conf_list)
#print(all_para)

para_list = list()
for k in all_para.keys() :
    for para in all_para[k] :
        l1 = remove_ns(para)
        l2 = l1.split("/")
        l3 = l2[-1]
        if l3 not in para_list :
            para_list.append(l3)
#print(para_list)
output_list = list()
add_dict2(root_res, output_list)
#print(output_list)
write_file(output_list,output_file_name)

'''
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
'''