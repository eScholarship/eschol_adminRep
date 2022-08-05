#from escholIF import escholIF
import subprocess
import os.path as osp
import os
import re

filefolder = "/apps/eschol/erep/data/13030/pairtree_root/"
localfolder = "/apps/eschol/subi/autodep/adminRep"
BATCH_SIZE = 2000


def saveFile(id, fdata):
    print("save file")
    filepath = './newmeta/' + id + '.meta.xml'
    f = open(filepath, "w")

    for line in fdata: 
        line = line.replace('$$',"DOUBLEDOLLAR").replace('$',"SINGLEDOLLAR")
        line = line.replace("DOUBLEDOLLAR",'$$')
        #f.write(line)
        x = re.split("SINGLEDOLLAR", line)
        newline = x[0]
        for i in range(len(x)-1):
            if i%2 == 0:
                # join with start dem
                newline = newline + '\(' + x[i+1] 
            else:

                newline = newline + '\)' + x[i+1]
        f.write(newline)
    f.close()


def updateXml(id):
    print("update xml " + id)

    updatedFile = localfolder + 'newmeta/' + id + '.meta.xml'

    if osp.exists(updatedFile):
        print("Processed file exists - skipping")
        return False
    # read all the lines from the file and save the set of line
    filepath = filefolder + id[0:2] +'/'+ id[2:4] + '/'+ id[4:6]+'/'+ id[6:8] +'/'+ id[8:10]+ '/' + id +'/meta/'+ id + '.meta.xml'
    if not osp.exists(filepath):
        raise RuntimeError(filepath + ' not found')
    f = open(filepath, "r")  
    fdata = []
    doiPresent = False
    authPresent = False
    while True: 
        line = f.readline() 
        if not line: 
            break
        fdata.append(line)
    f.close()
    saveFile(id, fdata)
    return True

def validateXml(id):
    print("validate xml " + id)
    filepath = localfolder + 'newmeta/' + id + '.meta.xml'
    if not osp.exists(filepath):
        print('file not present')
        return
    result = subprocess.call(['java', '-jar','./control/xsl/jing.jar', '-c', './schema/uci_schema.rnc', filepath], cwd='/apps/eschol/erep/xtf')
    print(result)
    if result != 0:
        assert("VALIDATE FAILED for " + id)

def copyXml(id):
    print("copy xml " + id)
    tempxml = localfolder + 'oldmeta/' + id + '.meta.xml'
    inxml = localfolder + 'newmeta/' + id + '.meta.xml'
    outxml = filefolder + id[0:2] +'/'+ id[2:4] + '/'+ id[4:6]+'/'+ id[6:8] +'/'+ id[8:10]+ '/' + id +'/meta/'+ id + '.meta.xml'

    if not osp.exists(inxml):
        print('file not present')
        return False
    os.popen('cp ' + outxml + ' ' + tempxml)
    os.popen('cp ' + inxml + ' ' + outxml)
    return True

def createidsToFix(idsdoi):
    print("create id file")
    filepath = './idsToFix.txt'
    f = open(filepath, "w")

    for id in idsdoi: 
        f.write(id + '\n')
        
    f.close()

def readidsToFix():
    print("read id file")
    filepath = './idsToFix.txt'
    f = open(filepath, "r")
    ids = []
    while True: 
        line = f.readline() 
        if not line: 
            break
        ids.append(line.strip())
        
    f.close()
    return ids

def updateMetaFileWhereNeeded(idsdoi):
    print("updateMetaFileWhereNeeded")
    # update xml to introduce doi if the doi is not present
    filepath = './idsDone.txt'
    f = open(filepath, "w")
    c = 0
    for id in idsdoi:
        print(id + " processing ")
        # call s3copy for this
        if updateXml(id):
            validateXml(id)
            copyXml(id)
            f.write(id + '\n')
            c += 1
        if c > BATCH_SIZE:
            print("DONE WITH THE BATCH")
            break
    f.close()


print("run fix MathJax delimiter")
#x = escholIF()
# get the list of items where doi is present in DB
#idsdoi = x.getJournalItemsWithDoi()

ids = readidsToFix()
#ids = ['qt0d89b1cc']
# for each of these run s3copy to get the splash page generated
#createidsToFix(idsdoi)
updateMetaFileWhereNeeded(ids)

#for id in idsdoi:
    # call s3copy for this
    #recreateSplash(id)
    #break




