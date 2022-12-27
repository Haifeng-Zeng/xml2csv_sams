import xml.etree.ElementTree as ET
import csv
import sys

res_file = "C:\\Scripts\\xml\\YonkersSmall1USM_ACPF_85945000.xml"
tree1 = ET.parse(res_file)

root1 = tree1.getroot()

ET.dump(tree1)
while root1 and "managed-element" not in root1.tag :
     root1 = root1[0]
tree1 = ET.ElementTree(root1)

print("second dump")
ET.dump(tree1)