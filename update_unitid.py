import sys
import os
from escholIF import escholIF
import xml.etree.ElementTree as ET
from xml.dom import minidom

import subprocess, shutil

cdir = os.getcwd()
tmp_dir = os.path.join(cdir, "tmp_meta")

if not os.path.isdir(tmp_dir):
    os.mkdir(tmp_dir)

class UpdateUnitIdImpl:
    oldunitid = None
    newunitid = None

    def __init__(self, oldId, newId):
        self.oldunitid = oldId
        self.newunitid = newId

    def getfilepaths(self, ark):
        meta_filename = f'{ark}.meta.xml'
        meta_filepath = f'/apps/eschol/erep/data/13030/pairtree_root/{ark[0:2]}/{ark[2:4]}/{ark[4:6]}/{ark[6:8]}/{ark[8:10]}/{ark}/meta/{ark}.meta.xml'
        tmp_filepath = os.path.join(tmp_dir, meta_filename)
        return meta_filepath, tmp_filepath

    def getUpdateXml(self, filepath):
        tree = ET.parse(filepath)
        ET.register_namespace("uci", "http://www.cdlib.org/ucingest")

        root = tree.getroot()

        # get an existing doi element
        entity_element = root.find("context/entity")

        # only do this if no doi element or the value is none
        if entity_element is not None:
            if entity_element.get("id") == self.oldunitid:
                print(f'Updating entity id')
                entity_element.set('id', self.newunitid)
                return minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ", newl='', encoding='utf-8')
            else:
                print(f'Skipping {filepath} has old unit {entity_element.get("id")}')
        else:
            print(f'Skipping {filepath} because context entity not found')
        return None

    def saveUpdatedFile(self, meta_filepath, tmp_filepath, data):
        with open(tmp_filepath, 'wb') as f:
            f.write(data)
        # validate xml
        result = subprocess.call(['java', '-jar','./control/xsl/jing.jar', '-c', './schema/uci_schema.rnc', tmp_filepath], cwd='/apps/eschol/erep/xtf')
        # Too many files fail validation due to problems that don't cause
        # indexing to fail so just watch the output for unexpected errors
        if result != 0:
            print(f'validation failed')
        else:
            print(f'validation successful')

        shutil.copyfile(meta_filepath, tmp_filepath + ".202507")
        shutil.move(tmp_filepath, meta_filepath)
        return

    def update_unitid(self):
        print("update unitid")

        # call escholintf to get the list of ids
        x = escholIF()
        itemids = x.getItemsFromUnit(newid)
        #itemids = ["qtttz6m94b"]
        for ark in itemids:
            try:
                meta_filepath, tmp_filepath = self.getfilepaths(ark)
                updatedtext = self.getUpdateXml(meta_filepath)
                if updatedtext:
                    self.saveUpdatedFile(meta_filepath, tmp_filepath, updatedtext)
                    result = subprocess.call(['erepredo', 'index', ark])
                    if result != 0:
                        print(f'index failed: {ark}')
            except Exception as e:
                print(f'caught an exception: {e}')
        return

print("start")


# Go to work.
if len(sys.argv) < 3:
  sys.stderr.write("Usage: %s oldunitid newunitid\n" % sys.argv[0])
  sys.stderr.write("... where example of newunitid is tise etc.\n")
  sys.exit(1)

oldid = sys.argv[1]
newid = sys.argv[2]

print(f'old unit id is {oldid} and {newid}')

x = UpdateUnitIdImpl(oldid, newid)
x.update_unitid()

print("end")
