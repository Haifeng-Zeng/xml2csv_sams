#!/usr/bin/python

import csv
import sys
#import configparser # No configparser in python 2.6.6
#import os
import argparse
#import glob
#import platform


class configFile :
    
    def __init__(self, file_name) :
        self.f1_delimiter = ","
        self.f2_delimiter = ","
        self.output_delimiter = ","
        self.join_dict = dict()
        self.f1_fields = list()
        self.f2_fields = list()

        self.output_dict = dict()

        with open(file_name,"r") as f :
            lines = f.readlines()
    
        for line in lines :
            line = line.strip()
            if len(line) == 0 :
                continue
            arr = line.split(":")
            if len(arr) != 2 :
                print("conf error at: ", line)
                sys.exit(1)
            if arr[0].strip() == "fields" :
                # set fileds
                fields = arr[1].split(",")
                self.output_header = arr[1].split(",")
                for field in fields :
                    file,_ = field.strip().split(".")
                    if file in self.output_dict.keys() :
                        self.output_dict[file].append(field)
                    else :
                        self.output_dict[file] = [field]
                    # f1_list and f2_list defines columns to keep for later process
                    if file == "f1" :
                        self.f1_fields.append(field)
                    elif file == "f2" :
                        self.f2_fields.append(field)
            elif arr[0] == "join" :
                #set join
                f1field, f2field = arr[1].split("=")
                file_no, _ = f1field.split(".")
                if file_no == "f1" :
                    key = f1field
                    if f1field not in self.f1_fields :
                        self.f1_fields.append(f1field)
                elif file_no == "f2" :
                    value = f1field
                    if f1field not in self.f2_fields :
                        self.f2_fields.append(f1field)
                else :
                    print("Error in join part of conf file")
                    sys.exit(1)
                file_no, _ = f2field.split(".")
                if file_no == "f1" :
                    key = f2field
                    if f2field not in self.f1_fields :
                        self.f1_fields.append(f2field)
                elif file_no == "f2" :
                    value = f2field
                    if f2field not in self.f2_fields :
                        self.f2_fields.append(f2field)
                else :
                    print("Error in join part of conf file")
                    sys.exit(1)
                self.join_dict[key] = value
            elif arr[0] == "delimiter" :
                file, symbol = arr[1].split("=")
                if file == "f1seperator" :
                    self.f1_delimiter = symbol.strip()
                elif file == "f2seperator" :
                    self.f2_delimiter = symbol.strip()
                elif file == "outseperator" :
                    self.output_delimiter = symbol.strip()
            elif arr[0] == "filter" :
                #set filter, not needed now
                pass
            else :
                print("Parsing conf file error!")
                sys.exit(1)
    

def read_command_line_args() :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", "-c", action="store", dest="conf_file", type=str , help="configuration file, mandatory, mandatory")
    parser.add_argument("--output", "-o", action="store", dest="output_file", type=str , help="output csv file, mandatory")
    parser.add_argument("--delimiter", "-d", action="store", dest="delimiter", type=str , help="Delimiter to seperate fields, optional")
    parser.add_argument("file1", help="1st file, mandatory")
    parser.add_argument("file2", help="2nd file, mandatory")
    
    args = parser.parse_args()
    conf_file, output_file, file1, file2 = args.conf_file, args.output_file, args.file1, args.file2

    return(conf_file, output_file, file1, file2)


def read_csv(file, delimiter, fields, file_no) :
    
#    delimiter = ","
    res_list = list()
    
#    if file_no == 1 :
#        prefix = "f1"
#    elif file_no == 2 :
#        prefix = "f2"
#    else :
#        print("file_no can only be 1 or 2")
#        sys.exit(1)
    
    with open(file) as csvfile :
        dict_reader = csv.DictReader(csvfile, delimiter = delimiter)
        dict_list = list(dict_reader)
    for item in dict_list :
        tmp_dict = dict()
        for k in item :
#            key = prefix + "." + k
            if k in fields :
                tmp_dict[k] = item[k]
        res_list.append(tmp_dict)
        
    return(res_list)


def orgnize_list(list_of_dict) :
    # re-orgnize list of dictionary to speed up query
    res_dict = dict()
    for item in list_of_dict :
# below is used in v1
#        key = "f1."+ item["f2.USM_ID"] + "_f1." + item["f2.NE_ID"]
# above is used in v1
        key = "f1."+ item["f2.USM_ID"]
# above is used in v2
        if key in res_dict.keys() :
            res_dict[key].append(item)
        else :
            res_dict[key] = [item]
    return(res_dict)


def combine_dict(join_dict, output_dict, file1_list, file2_dict) :
    
    result_list = list()
    for item1 in file1_list :
        res_item = item1
        for key in output_dict["f2"] :
            res_item[key] = ""
# below is used in v1
#        key2 = "f1." + item1["f1.USM_ID"] + "_f1." + item1["f1.NE_ID"]
# above is used in v1
        key2 = "f1."+ item1["f1.USM_ID"]
# above is used in v2
        if key2 in file2_dict.keys():
            for item2 in file2_dict[key2] :
                match = True
                for k in join_dict.keys() :
                    if item1[k] != item2[join_dict[k]] :
                        match = False
                if match :
                    for k2 in output_dict["f2"] :
                        res_item[k2] = item2[k2]
                    break
        result_list.append(res_item)
    
    return(result_list)


def combine_dict2(join_dict, output_dict, file1_list, file2_list) :
    # To speed up query, create index for file2 using dict
    f1_join_keys = list()
    f2_join_keys = list()
    
    for k in join_dict :
        f1_join_keys.append(k)
        f2_join_keys.append(join_dict[k])
    
    f2_dict = dict()
    for item in file2_list :
        key = ""
        for ele in f2_join_keys :
            key += item[ele] + "_"
        if key not in f2_dict.keys() :
            f2_dict[key] = [item]
        else :
            f2_dict[key].append(item)
    
    # Start to combine file1 and file2
    for f1_item in file1_list :
        key = ""
        for k in f1_join_keys :
            key += f1_item[k] + "_"
        if key in f2_dict.keys() :
            f2_item = f2_dict[key][0]
        
        res_dict = dict()
#        for k in configer.output_header :
#            if k in 


        

    


def write_file_266(write_list, file_name, header, delimiter) :
    # re-orgnize write_list, replace full path names of parameter with short names
#    delimiter = ","

    output_header = list()
    for line in header :
        line = line.replace("f1.","")
        line = line.replace("f2.","")
        output_header.append(line)

    line = delimiter.join(output_header)
    with open(file_name, 'w') as csvfile:
        csvfile.write(line+"\n")
        for item in write_list :
            arr = list()
            for k in header :
                arr.append(item[k])
            line = delimiter.join(arr)
            csvfile.write(line+"\n")





# Test variables
#conf_file = "c:\\scripts\\xml\\Combine\\radio_alu.conf"
#file1_name = "c:\\scripts\\xml\\Combine\\radio.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\alu.csv"
#output_file = "c:\\scripts\\xml\\combined_alu.csv"

conf_file = "c:\\scripts\\xml\\Combine\\combine_enb_f1_3_2.conf"
file1_name = "c:\\scripts\\xml\\Combine\\combined_1_2_3.csv"
file2_name = "c:\\scripts\\xml\\Combine\\FSU_du-cpri-port-entries.csv"
output_file = "c:\\scripts\\xml\\Combine\\report.csv"

#conf_file = "c:\\scripts\\xml\\Combine\\radio_samsung.conf"
#file1_name = "c:\\scripts\\xml\\combined_asl.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\samsung.csv"
#output_file = "c:\\scripts\\xml\\combined_samsung.csv"
# ########################


# Test class
#configer = configFile(conf_file)
#print(configer.f1_delimiter)
#print(configer.f2_delimiter)
#print(configer.output_delimiter)
#print(configer.join_dict)
#print(configer.f1_fields)
#print(configer.f2_fields)
#print(configer.output_header)


#(conf_file, output_file, file1_name, file2_name) = read_command_line_args()

configer = configFile(conf_file)

# Global variables
#join_dict = dict()
#output_dict = dict()
# ######################


file1_list = read_csv(file1_name, configer.f1_delimiter, configer.f1_fields, 1)
file2_list = read_csv(file2_name, configer.f2_delimiter, configer.f2_fields, 2)
#file2_dict = orgnize_list(file2_list)
#print(file2_dict)

#write_list = combine_dict(configer.join_dict, configer.output_dict, file1_list, file2_dict)
write_list = combine_dict2(configer.join_dict, configer.output_dict, file1_list, file2_list)

write_file_266(write_list, output_file, configer.output_header, ",")


