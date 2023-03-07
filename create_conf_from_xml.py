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


def read_command_line_para() :
    
#    global req_file, res_file, conf_file
    parser = argparse.ArgumentParser()
    
    if platform.system() == "Windows" :
        # for windows
        parser.add_argument("xml_files", help="Read xml files")
    elif platform.system() == "Linux" :
        #for linux
        parser.add_argument("xml_files", nargs='+', help="Read xml files")
    elif platform.system() == "Darwin" :
        pass
    else :
        print("Unkown OS")
        sys.exit(1)
    
    args = parser.parse_args()


    xml_files = args.xml_files_name
    if platform.system() == "Windows" :
        xml_files = glob.glob(args.xml_files)
    
    
    return(xml_files)


def read_tree_from_response(xml_file) :
    try :
        tree = ET.parse(xml_file)
    except :
        print("Open file ", xml_file, " Failed!")
        exit(1)
    root = tree.getroot()
    while True :
        if remove_ns(root.tag) == "rpc-error" :
            return(None)
        elif remove_ns(root.tag) == "rpc-reply" :
            root = root[0]
        elif remove_ns(root.tag) == "data" :
            root = root[0]
        elif remove_ns(root.tag) == "managed-element" :
            return root
        # no "managed-element" appears in xml
        else :
            node = ET.Element("managed-element")
            for child in root :
                node.append(child)
            return(node)

#    while queue:
#        p = queue.pop(0)
#        if "managed-element" in p.tag :
#            return(p)
#        for child in p :
#            queue.append(child)
#    if not root :
#        print("Parsing ",xml_file, " failed")
#        return(None)
#    else :
#        return(p)


def add_path(node, parent_path) :
     # define 1 attribute: "path" indicates the hierarchy level without name space;
     # add path attribute to all node without child 

    if not node or not list(node) :
        return

    # update path info of current level
    current_path = parent_path + "/" + remove_ns(node.tag)
 
    node.set("path", current_path)
    
    for child in node :
        child_path = current_path + "/" + remove_ns(child.tag)
        child.set("path", child_path)
        if list(child) :
            add_path(child, current_path)
    return

dict_all = dict()
#files = read_command_line_para()
files = ["C:\\Scripts\\xml\\y.xml"]
for file in files :
    root = read_tree_from_response(file)
    if not root :
        print("Parsing ", file, " filed!")
        continue
    add_path(root,"")
    queue = list()
    queue.append(root)
    while queue :
        p = queue.pop(0)
        for child in p :
            if list(child) :
                queue.append(child)
                continue
            #arr = p.get("path").split("/")
            #para = arr[-1]
            para = remove_ns(child.tag)
            #path = "/".join(arr[:-1])
            path = p.get("path")
            path += "/"
        
            if path not in dict_all.keys() :
                dict_all[path] = [para]
            else :
                if para not in dict_all[path] :
                    dict_all[path].append(para)

for k in dict_all.keys() :
    for para in dict_all[k] :
        print(k + para)


