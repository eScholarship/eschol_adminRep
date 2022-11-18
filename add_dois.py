import xml.etree.ElementTree as ET
from xml.dom import minidom

import subprocess, shutil, os, csv

cdir = os.getcwd()
tmp_dir = os.path.join(cdir, "tmp_meta")

if not os.path.isdir(tmp_dir):
    os.mkdir(tmp_dir)

with open("doi_map1.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row["EZID Target"]
        doi = row["IJCP DOI"]
        ark = "qt" + url.split("/")[-1]

        meta_filename = f'{ark}.meta.xml'
        #meta_filepath = meta_filename
        meta_filepath = f'/apps/eschol/erep/data/13030/pairtree_root/{ark[0:2]}/{ark[2:4]}/{ark[4:6]}/{ark[6:8]}/{ark[8:10]}/{ark}/meta/{ark}.meta.xml'
        tmp_filepath = os.path.join(tmp_dir, meta_filename)

        tree = ET.parse(meta_filepath)
        ET.register_namespace("uci", "http://www.cdlib.org/ucingest")

        root = tree.getroot()

        # get an existing doi element
        doi_element = root.find("doi")

        # only do this if no doi element or the value is none
        if doi_element == None or doi_element.text == "null":
            print(f'Adding DOI: {ark}')
            # if no doi element exists create one and put it after the "authors" element
            if doi_element == None:
                index = list(root).index(root.find("authors")) + 1
                doi_element = ET.Element("doi")
                root.insert(index, doi_element)

            doi_element.text = doi

            x = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ", newl='', encoding='utf-8')

            # write file to temp dir
            with open(tmp_filepath, 'wb') as f:
                f.write(x)

            # validate xml
            result = subprocess.call(['java', '-jar','./control/xsl/jing.jar', '-c', './schema/uci_schema.rnc', tmp_filepath], cwd='/apps/eschol/erep/xtf')
            # Too many files fail validation due to problems that don't cause 
            # indexing to fail so just watch the output for unexpected errors
            #if result != 0:
            #    print(f'validation failed: {ark} {doi}')
            #else:
            #    print(f'validation successful: {ark} {doi}')

            shutil.copyfile(meta_filepath, tmp_filepath + ".202211")
            shutil.move(tmp_filepath, meta_filepath)
            result = subprocess.call(['erepredo', 'index', ark])
            if result != 0:
                print(f'index failed: {ark} {doi}')
        else:
            print(f'*** Item already has doi: {ark} {doi} {doi_element.text}')

