#!/usr/bin/python

# cooments

import csv
import sys
#import configparser # No configparser in python 2.6.6
#import os
import argparse
import time


#############################################################################
# AUTHOR : Haifeng Zeng <haifeng.zeng@partner.sea.samsung.com> 
# PURPOSE: combine two csv files into one, accordig to used-defied conf file 
# UPDATED: 2023-02-08
#############################################################################

#############################################################################
# Change History
# v1: Initial version
#
# v2:   1. add key for records in file2 to speed up query
#       2. user can define alias for any column name in conf file
#############################################################################

class configFile :
    
    def __init__(self, file_name) :
        self.f1_delimiter = ","
        self.f2_delimiter = ","
        self.output_delimiter = ","
        self.join_dict = dict()
        self.f1_fields = list()
        self.f2_fields = list()
        self.alias = dict()

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
                for i in range(len(self.output_header)) :
                    if "|" in self.output_header[i] :
                        self.output_header[i], _ = self.output_header[i].split("|")
                for field in fields :
                    alia = None
                    if "|" in field :
                        field, alia = field.split("|")
                    file,_ = field.strip().split(".")
                    if file in self.output_dict.keys() :
                        self.output_dict[file].append(field)
                    else : 
                        self.output_dict[file] = [field]
                    if alia:
                        self.alias[field] = alia
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


def read_csv(file, delimiter, fields, file_no) :
    
#    delimiter = ","
    
    T1 = time.time()
    
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
#            if key in fields :
            tmp_dict[key] = item[k]
        res_list.append(tmp_dict)

    print("read file ", file, ": ", time.time() - T1)    
    
    return(res_list)

def combine_dict(join_dict, output_dict, file1_list, file2_list) :
    
    # create dict on file2 to speed up query

    T1 = time.time()
    join_list_f1 = list()
    join_list_f2 = list()
    for k in join_dict :
        join_list_f1.append(k)
        join_list_f2.append(join_dict[k])
    
#    key_join_length = len(join_list_f1)
    f2_dict = dict()
    for item in file2_list :
        key = ""
        for k in join_list_f2 :
            key += item[k] + "_"

        if key in f2_dict.keys() :
            f2_dict[key].append(item)
            print(key, " has more than 1 values")
        else :
            f2_dict[key] = [item]
    
    print("create index only: ", time.time() - T1)

    T1 = time.time()    
    # start qury file2 on f2_dict
    result_list = list()
    for item1 in file1_list :
        res_item = dict()
        for k in output_dict["f1"] :
            res_item[k] = item1[k]
        key = ""
        for k in join_list_f1 :
            key += item1[k] + "_"
        item2 = dict()
        if key in f2_dict.keys() :
            item2 = f2_dict[key][0]
            for k in output_dict["f2"] :
                res_item[k] = item2[k]
        else:
            for k in output_dict["f2"] :
                res_item[k] = ""
        result_list.append(res_item)
    
    print("combine two dictionaries only: ", time.time() - T1)

    return(result_list)


def write_file_266(write_list, file_name, header, delimiter) :
    # re-orgnize write_list, replace full path names of parameter with short names
#    delimiter = ","

    T1 = time.time()
    
    output_header = list()
    for line in header :
        if line in configer.alias.keys() :
            line = configer.alias[line]
        else :
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
#	    print(arr)
            line = delimiter.join(arr)
            csvfile.write(line+"\n")
    
    print("write file only: ", time.time() - T1)





# Test variables
#conf_file = "c:\\scripts\\xml\\Combine\\radio_alu.conf"
#file1_name = "c:\\scripts\\xml\\Combine\\radio.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\alu.csv"
#output_file = "c:\\scripts\\xml\\combined_alu.csv"

#conf_file = "c:\\scripts\\xml\\Combine\\comb.conf"
#file1_name = "c:\\scripts\\xml\\Combine\\short_earfnc.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\short_frequency-band-indicator.csv"
#output_file = "c:\\scripts\\xml\\Combine\\rep.csv"

#conf_file = "c:\\scripts\\xml\\Combine\\radio_samsung.conf"
#file1_name = "c:\\scripts\\xml\\combined_asl.csv"
#file2_name = "c:\\scripts\\xml\\Combine\\samsung.csv"
#output_file = "c:\\scripts\\xml\\combined_samsung.csv"
# ########################


(conf_file, output_file, file1_name, file2_name) = read_command_line_args()

configer = configFile(conf_file)

# Global variables
#join_dict = dict()
#output_dict = dict()
# ######################


file1_list = read_csv(file1_name, configer.f1_delimiter, configer.f1_fields, 1)
file2_list = read_csv(file2_name, configer.f2_delimiter, configer.f2_fields, 2)
#print(file2_dict)

#write_list = combine_dict(configer.join_dict, configer.output_dict, file1_list, file2_dict)
write_list = combine_dict(configer.join_dict, configer.output_dict, file1_list, file2_list)

write_file_266(write_list, output_file, configer.output_header, ",")



