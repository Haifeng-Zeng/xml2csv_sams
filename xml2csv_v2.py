#!/usr/bin/python

#####################################################################
# AUTHOR : Haifeng Zeng <haifeng.zeng@partner.sea.samsung.com> 
# PURPOSE: Convert Yang Command output to csv format
# UPDATED: 2023-02-08
#####################################################################

#####################################################################
# Change History
# v1: Initial version
#
# v2:   1. add error file write possibility
#       2. check file name format and report error
#       3. add special character escaping
#       4. fix the bug when reading 0 byte file
# ################################################################## 

import xml.etree.ElementTree as ET
import csv
import sys
#import configparser # No configparser in python 2.6.6
import os
import argparse
import glob
import platform

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


def read_command_line_args() :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", "-c", action="store", dest="conf_file", type=str , help="configuration file, mandatory")
    parser.add_argument("--output", "-o", action="store", dest="output_file", type=str , help="output csv file, mandatory")
    parser.add_argument("--cmdfile", "-m", action="store", dest="cmd_file",type=str , help="command file, optional")
    parser.add_argument("--errfile", "-e", action="store", dest="err_file",type=str , help="error log file, optional")

    parser.add_argument("res_files", nargs="+", help="response file(s), mandatory")

    if platform.system() == "Windows" :
        # for windows
        #parser.add_argument("third_files", help="Read xml files")
        res_files = glob.glob(args.third_files)
        pass
    elif platform.system() == "Linux" :
        #for linux
        #parser.add_argument("third_files", nargs='+', help="Read xml files")
        pass
    elif platform.system() == "Darwin" :
        pass
    else :
        print("Unkown OS")
        sys.exit(1)
    
    args = parser.parse_args()
#    print(args)
    err_file = "err.csv"
    cmd_file, conf_file, output_file, err_file, res_files = args.cmd_file, args.conf_file, args.output_file, args.err_file,args.res_files

    return(cmd_file, conf_file, output_file, err_file, res_files)


def read_conf(conf_file) :
    # Read paramters to write to csv from configuration file
    # pipe sign "|" can be used to definde alias for a parameter in conf file
    
    para_dict = dict()
    with open(conf_file,"r") as f :
        lines = f.readlines()
    
    # remove newline from every line
    for i in range(len(lines)) :
        lines[i] = lines[i].strip()
    
    # remove comments starting with #
    for i in range(len(lines)) :
        lines[i] = lines[i].split("#")[0]

    pathes = list()
    # remove empty lines
    for line in lines :
        if len(line) > 0:
            pathes.append(line)
    
    for line in pathes :
        path = line.split(":")
        if "|" in path[0] :
            l1 = path[0].split("|")
            path = l1[0]
        else :
            l1 = path[0].split("/")
        alias = l1[-1]
        para_dict[path[0]] = ([path[1], alias])
    return(para_dict)
    

def validate_conf_file(req_file, para_dict):
    # check if any parameter defined in conf file missing from command file
    
    # list for parameter in conf file but missing in request file
    #generate para_set to include all parameters to be exported to csv
    
    root_req = read_tree_from_xml(req_file)
    
    if not root_req :
        sys.exit(1)

    add_path(root_req,"")
    
    para_set = set(para_dict.keys())

    stack = list()
    stack.append(root_req)
    while stack :
        if not para_set :
            return True
        p = stack.pop()
        path = p.get("path")
        if path in para_set :
            para_set.remove(path)
    
        for child in p :
            stack.append(child)

    if not para_set :
        return True
    else :
        for para in para_set :
            print(para, " not in commad file!")
        return False


def read_tree_from_xml(xml_file) :
    try :
        tree = ET.parse(xml_file)
    except :
        print("Open file ", xml_file, " Failed!")
        exit(1)
    root = tree.getroot()
    queue = list()
    queue.append(root)
    while queue:
        p = queue.pop(0)
        if "managed-element" in p.tag :
            return(p)
        for child in p :
            queue.append(child)
    if not root :
        print("Parsing ",xml_file, " failed")
        return(None)
    else :
        ET.dump(p)
        return(p)


def read_tree_from_xml2(xml_file) :
    try :
        tree = ET.parse(xml_file)
    except :
        print("Open file ", xml_file, " Failed!")
        exit(1)
    root = tree.getroot()
    while True:
        if not list(root) and remove_ns(root.tag) == "data" :
            node = ET.Element("managed-element")
            return(node)
	for child in root :
            if  remove_ns(root.tag) == "data" and child is None :
                node = ET.Element("managed-element")
                for child in root :
                    node.append(child)
                return(node)
            elif remove_ns(child.tag) == "rpc-error" :
                return(None)
            elif remove_ns(child.tag) == "data" :
                root = child
            elif remove_ns(child.tag) == "managed-element" :
                return child
            else :
                node = ET.Element("managed-element")
                for child in root :
                    node.append(child)
                return(node)


def read_tree_from_xml3(xml_file) :
    try :
        tree = ET.parse(xml_file)
    except :
        print("Open file ", xml_file, " Failed!")
        exit(1)
    root = tree.getroot()
    while True:
#        if not root :
#            return(None)
        for child in root :
#            print(list(root))
            if remove_ns(child.tag) == "rpc-error" :
                return(None)
            elif remove_ns(child.tag) == "data" :
                if list(child) :
                    root = child
                else :
                    return(child)
            elif remove_ns(child.tag) == "managed-element" :
	            return(child)
            else :
                ele = ET.Element("managed-element")
                for child in root :
                    ele.append(child)
                return(ele)


def add_path(node, parent_path) :
     # define 1 attribute: "path" indicates the hierarchy level without name space;
     # add path attribute to all node without child 

    if not node or not list(node) :
        return

    # update path info of current level
    current_path = parent_path + "/" + remove_ns(node.tag)
 
    node.set("path", current_path)

    if current_path in para_dict.keys() :
        if para_dict[current_path][0] == 'uniq' :
            node.set("uniq", "True")
        elif para_dict[current_path][0] == 'non-uniq' :
            node.set("uniq", "False")
    
    for child in node :
        child_path = current_path + "/" + remove_ns(child.tag)
        child.set("path", child_path)
        if child_path in para_dict.keys() :
            child.set("processed", "No")
            if para_dict[child_path][0] == 'uniq' :
                child.set("uniq", "True")
            elif para_dict[child_path][0] == 'non-uniq' :
                child.set("uniq", "False")
        if list(child) :
            add_path(child, current_path)
    return


def add_to_write(write_list,usm_id, ne_id):
    write_dict = dict()
    write_dict["USM_ID"] = usm_id
    write_dict["NE_ID"] = ne_id
    for item in write_list :
        write_dict[item.get("path")] = item.text
        item.set("processed", "Yes")
    return(write_dict)


def add_to_write_2(input_dict,usm_id, ne_id):
    write_dict = dict()
    write_dict["USM_ID"] = usm_id
    write_dict["NE_ID"] = ne_id
    for k, v in input_dict.items() :
        write_dict[k] = v
#        item.set("processed", "Yes")
    return(write_dict)


def create_output(node, para_dict, usm_id, ne_id) :
    paras = list(para_dict.keys())
    stack = list()
    
    output_list = list()
    para_index = 0
    para_index_max = len(paras) 
    curr_path_list = list()
    stack.append(node)
    while stack :
        p = stack.pop()
        queue = list()
        for child in p :
            queue.append(child)
        while queue :
            stack.append(queue[-1])
            queue.pop()
        
        curr_path = p.get("path")

        if curr_path in curr_path_list :
            # add missing parameter, if current paramters are not printed
            if output_list[-1].get("processed") == "No" :
                while para_index < para_index_max :
                    k = paras[para_index].split("/")
                    ele = ET.Element(k[-1])
                    ele.text = ""
                    ele.set("uniq", para_dict[paras[para_index]])
                    ele.set("path", paras[para_index])
                    output_list.append(ele)
                    curr_path_list.append(paras[para_index])
                    para_index += 1

                csv_list.append(add_to_write(output_list, usm_id, ne_id))
            
                # pop uniq element from output_dict while curr_key_list[-1] is uniq
                #while output_list[-1].get("path") == curr_path :
            while output_list[-1].get("path") != curr_path:
                output_list.pop()
                curr_path_list.pop()
                para_index -= 1
            output_list.pop()
            curr_path_list.pop()
            para_index -= 1
            
            output_list.append(p)
            curr_path_list.append(p.get("path"))
            para_index += 1

        if para_index == para_index_max :
            csv_list.append(add_to_write(output_list, usm_id, ne_id))
            # pop uniq element from output_dict while curr_key_list[-1] is uniq
            while output_list[-1].get("uniq") == "True" :
                output_list.pop()
                curr_path_list.pop()
                para_index -= 1

        if curr_path == paras[para_index] :
            output_list.append(p)
            curr_path_list.append(curr_path)
            para_index += 1
    
    if len(output_list) == para_index_max :
        csv_list.append(add_to_write(output_list, usm_id, ne_id))


def create_output_2(node, para_dict, usm_id, ne_id) :
    key_list = list(para_dict.keys())
    output_dict = dict()
    filled_keys = list()
    for k in key_list :
        output_dict[k] = ""

    stack = list()
    stack.append(node)
    while stack :
        p = stack.pop()
        queue = list()
        for child in p :
            queue.append(child)
        while queue :
            stack.append(queue[-1])
            queue.pop()
        
        path = p.get("path")
        if path not in key_list :
            continue
        
        # if current paramter already has value, output current output_dict and clear uniq values
        if path in filled_keys :
            csv_list.append(add_to_write_2(output_dict, usm_id, ne_id))

            for k in para_dict.keys() :
                if para_dict[k][0] == "uniq" :
                    output_dict[k] == ""
                    
            while filled_keys[-1] != path :
                output_dict[filled_keys[-1]] = ""
                filled_keys.pop()
        
        # when current paramter value is empty
        output_dict[path] = p.text
        filled_keys.append(path)
    
    csv_list.append(add_to_write_2(output_dict, usm_id, ne_id))


def create_output_3(node, output_dict) :
    local_dict = output_dict.copy()

    curr_path = node.get("path")
    need_push = False
    for pathes in para_dict.keys() :
        if curr_path in pathes :
            need_push = True
            break
    
    if not need_push :
        return

    queue = list()
    for child in node :
        if list(child) :
            queue.append(child)
            continue
        path = child.get("path")
        if path in para_dict.keys() :
            local_dict[path] = child.text

    if not queue :
        all_keys = local_dict.keys()
        for k in para_dict.keys() :
            if k not in all_keys :
                local_dict[k] = ""
        csv_list.append(add_to_write_2(local_dict, usm_id, ne_id))
    else :
        for child in queue :
            create_output_3(child, local_dict)


def create_output_4(node, output_dict) :
    local_dict = output_dict.copy()

    queue = list()
    for child in node :
        path = child.get("path")
        if list(child) :
            for pathes in para_dict.keys() :
                if path in pathes :
                    queue.append(child)
                    break
        if path in para_dict.keys() :
            local_dict[path] = child.text

    if not queue :
        all_keys = local_dict.keys()
        for k in para_dict.keys() :
            if k not in all_keys :
                local_dict[k] = ""
        csv_list.append(add_to_write_2(local_dict, usm_id, ne_id))
    else :
        for child in queue :
            create_output_4(child, local_dict)


def write_file(write_list, file_name) :
    # re-orgnize write_list, replace full path names of parameter with short names
    
    short_name_write_list = list()
    for dict1 in write_list :
        dict2 = dict()
        for k, v in dict1.items() :
            if k in ("USM_ID", "NE_ID") :
                dict2[k] = dict1[k]
            else :
                dict2[para_dict[k][1]] = v
        short_name_write_list.append(dict2)


    #print(short_name_write_list)

    with open(file_name, 'w', newline = "", encoding="utf-8") as csvfile:
        # use dictWriter, on python 3
        writer = csv.DictWriter(csvfile, fieldnames=short_name_write_list[0].keys())
        writer.writeheader()
        writer.writerows(short_name_write_list)


def write_file_266(write_list, file_name, conf_file) :
    # re-orgnize write_list, replace full path names of parameter with short names
    delimeter = ","

    short_name_write_list = list()
    for dict1 in write_list :
        dict2 = dict()
        for k, v in dict1.items() :
            if k in ("USM_ID", "NE_ID") :
                dict2[k] = dict1[k]
            else :
                if v is None :
                    v = ""
                dict2[para_dict[k][1]] = v
        short_name_write_list.append(dict2)

    with open(conf_file,"r") as f :
        lines = f.readlines()
    
    lines2 = list()
    for i in range(len(lines)) :
        lines[i] = lines[i].strip()
    if len(lines[i]) == 0 :
        continue
    if len(lines[i]) == 0 :
        continue
    lines[i] = lines[i].split(":")[0]
    if len(lines[i].split("|")[0]) > 0 :
	    lines2.append(lines[i].split("|")[0])

    header = list()
    header.append("USM_ID")
    header.append("NE_ID")
    for i in range(len(lines2)) :
        header.append(para_dict[lines2[i]][1])

   # print(short_name_write_list)
    line = delimeter.join(header)
    with open(file_name, 'w') as csvfile:
        csvfile.write(line+"\n")
        for item in short_name_write_list :
            arr = list()
            for k in header :
                arr.append(item[k])
            line = delimeter.join(arr)
            csvfile.write(line+"\n")
        

def process_error_file(file_name) :
    tree = ET.parse(file_name)
    root = tree.getroot()
    dict1 = dict()
    queue = list()
    queue.append(root)
    while queue :
        p = queue.pop(0)
        if remove_ns(p.tag) not in  ("rpc-reply", "rpc-error") :
            dict1[remove_ns(p.tag)] = p.text
        for child in p :
            queue.append(child)
    dict1["USM_ID"] = usm_id
    dict1["NE_ID"] = ne_id
    return(dict1)


def write_error_list(write_list, file_name) :
    
    if not write_list :
        return
    
    delimeter = ","

    header = ["USM_ID","NE_ID","error-tag","error-type","error-severity","error-message"]
   
    line = delimeter.join(header)
    with open(file_name, 'w') as csvfile:
        csvfile.write(line+"\n")
        for item in write_list :
            arr = list()
            for k in header :
                arr.append(item[k])
            line = delimeter.join(arr)
            csvfile.write(line+"\n")


def add_quote(s) :
    if '"' in s :
        s = s.replace('"','\"')
    if "," in s :
        s = '"' + s + '"'
    return s


(req_file, conf_file, output_file, err_file, res_files) = read_command_line_args()

#req_file = "C:\\Scripts\\xml\\cmd.xml"
#res_files = ["C:\\Scripts\\xml\\re-BloomingtonLarge1USM_DU_5160143.xml","C:\\Scripts\\xml\\re-EastSyracuseMedium1USM_DU_10148.xml","C:\\Scripts\\xml\\re-YonkersSmall1USM_DU_4620050.xml"]
#res_files = ["C:\\Scripts\\xml\\YonkersSmall1USM_eNB_85709.xml"]
#res_files = ["C:\\Scripts\\xml\\BloomingtonLarge1USM_eNB_101001.xml"]
#conf_file = "C:\\Scripts\\xml\\conf.conf"
#output_file = "C:\\Scripts\\xml\\out.csv"

para_dict = read_conf(conf_file)

#print(para_dict)

if req_file :
    if not validate_conf_file(req_file, para_dict) :
        sys.exit(1)

csv_list = list()
error_list = list()

for res_file in res_files:
    (line, _) = os.path.splitext(os.path.basename(res_file))
    line = line.split("_")
    if len(line) != 3 :
        print("File name foramt of ", res_file, " is not correct")
        continue
    usm_id = line[0]
    ne_id = line[1] + "_" + line[2]
#    print(res_file)
    res_root = read_tree_from_xml3(res_file)
#    if not res_root :
    if res_root is None :
        print("Parsing ", res_file, " failed")
        error_list.append(process_error_file(res_file))
        continue
    add_path(res_root,"")
#    ET.dump(res_root)
    output_dict = dict()
    create_output_4(res_root, output_dict) 


#output_file_name = "results.csv"
write_file_266(csv_list, output_file, conf_file)
if error_list :
    write_error_list(error_list, err_file)
#print(csv_list)
#ET.dump(res_root)
