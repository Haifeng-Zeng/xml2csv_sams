import csv
import sys
#import configparser # No configparser in python 2.6.6
import os
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


'''
def read_conf(conf_file) :
    # Read paramters to write to csv from configuration file
    # pipe sign "|" can be used to definde alias for a parameter in conf file
    
    f1delimiter = ","
    f2delimiter = ","
    join_dict = dict()
    f1_fields = list()
    f2_fields = list()
    with open(conf_file,"r") as f :
        lines = f.readlines()
    
    # remove newline from every line
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
            output_header = arr[1].split(",")
            for field in fields :
                file,_ = field.strip().split(".")
                if file in output_dict.keys() :
                    output_dict[file].append(field)
                else :
                    output_dict[file] = [field]
                # f1_list and f2_list defines columns to keep for later process
                if file == "f1" :
                    f1_fields.append(field)
                elif file == "f2" :
                    f2_fields.append(field)
        elif arr[0] == "join" :
            #set join
            f1field, f2field = arr[1].split("=")
            file_no, _ = f1field.split(".")
            if file_no == "f1" :
                key = f1field
                if f1field not in f1_fields :
                    f1_fields.append(f1field)
            elif file_no == "f2" :
                value = f1field
                if f1field not in f2_fields :
                    f2_fields.append(f1field)
            else :
                print("Error in join part of conf file")
                sys.exit(1)
            file_no, _ = f2field.split(".")
            if file_no == "f1" :
                key = f2field
                if f2field not in f1_fields :
                    f1_fields.append(f2field)
            elif file_no == "f2" :
                value = f2field
                if f2field not in f2_fields :
                    f2_fields.append(f2field)
            else :
                print("Error in join part of conf file")
                sys.exit(1)
            join_dict[key] = value
        elif arr[0] == "delimiter" :
            file, symbol = arr[1].split("=")
            if file == "f1seperator" :
                f1delimiter = symbol.strip()
            elif file == "f2seperator" :
                f2delimiter = symbol.strip()
        elif arr[0] == "filter" :
            #set filter, not needed now
            pass
        else :
            print("Parsing conf file error!")
            sys.exit(1)
    
    return(join_dict, f1delimiter, f2delimiter, f1_fields, f2_fields, output_header)
'''

def read_csv(file, delimiter, fields, file_no) :
    
#    delimiter = ","
    res_list = list()
    
    if file_no == 1 :
        prefix = "f1"
    elif file_no == 2 :
        prefix = "f2"
    else :
        print("file_no can only be 1 or 2")
        sys.exit(1)
    
    with open(file) as csvfile :
        dict_reader = csv.DictReader(csvfile, delimiter = delimiter)
        dict_list = list(dict_reader)
    for item in dict_list :
        tmp_dict = dict()
        for k in item :
            key = prefix + "." + k
            print(key)
            if key in fields :
                tmp_dict[key] = item[k]
            else :
                print(key)
                print(fields)
        res_list.append(tmp_dict)
        
    return(res_list)


def orgnize_list(list_of_dict) :
    # re-orgnize list of dictionary to speed up query
    res_dict = dict()
    for item in list_of_dict :
        a = item["f2.USM_ID"]
        key = "f1."+ item["f2.USM_ID"] + "_f1." + item["f2.NE_ID"]
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
        key2 = "f1." + item1["f1.USM_ID"] + "_f1." + item1["f1.NE_ID"]
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

#conf_file = "c:\\scripts\\xml\\Combine\\radio_asl.conf"
#file1_name = "c:\\scripts\\xml\\combined_alu.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\asl.csv"
#output_file = "c:\\scripts\\xml\\combined_asl.csv"

conf_file = "c:\\scripts\\xml\\6 files\\conf_2_3.conf"
file1_name = "c:\\scripts\\xml\\6 files\\CONF_FILE_2_eutran-cell-fdd-tdd.csv"
file2_name = "c:\\scripts\\xml\\6 files\\CONF_FILE_3_positioning-conf-info.csv"
output_file = "c:\\scripts\\xml\\6 files\\out1.csv"
# ########################


# Test class
configer = configFile(conf_file)
print(configer.f1_delimiter)
print(configer.f2_delimiter)
print(configer.output_delimiter)
print(configer.join_dict)
print(configer.f1_fields)
print(configer.f2_fields)
print(configer.output_header)




# Global variables
#join_dict = dict()
#output_dict = dict()
# ######################


#(join_dict, f1delimiter, f2delimiter, f1fields, f2fields, output_header) = read_conf(conf_file)

file1_list = read_csv(file1_name, configer.f1_delimiter, configer.f1_fields, 1)
file2_list = read_csv(file2_name, configer.f2_delimiter, configer.f2_fields, 2)
file2_dict = orgnize_list(file2_list)
#print(file2_dict)

write_list = combine_dict(configer.join_dict, configer.output_dict, file1_list, file2_dict)

write_file_266(write_list, output_file, configer.output_header, ",")
#combine_dict(mapping_dict, file1_dict, file2_dict)
#print(file1_dict)

