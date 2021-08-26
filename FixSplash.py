from escholIF import escholIF
import subprocess
import os.path as osp
import os

filefolder = "/apps/eschol/erep/data/13030/pairtree_root/"
s3copypath = "/apps/eschol/erep/xtf/control/tasks/s3copy.py"
localfolder = "/apps/eschol/subi/autodep/adminRep/"
BATCH_SIZE = 2000

def recreateSplash(id):
    if not osp.exists(s3copypath):
        raise RuntimeError('s3copypath not found')

    cmdout = subprocess.call(['python',s3copypath,'--force',id])
    print(cmdout)
    #for line in map(str, cmdout.splitlines()):
    #    print(line)

def saveFile(id, doi, fdata):
    print("save file")
    filepath = './newmeta/' + id + '.meta.xml'
    f = open(filepath, "w")

    for line in fdata: 
        f.write(line)
        if '</authors>' in line:
            f.write('   <doi>'+doi+'</doi>\n')
        #write line to file
        
    f.close()


def updateXml(id, doi):
    print("update xml " + id)
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
        if '</doi>' in line:
            print('doi present')
            doiPresent = True
        if '</authors>' in line:
            print('author present')
            authPresent = True
        if not line: 
            break
        fdata.append(line)
    f.close()
    if not doiPresent and authPresent:
        saveFile(id, doi, fdata)
        return True
    return False

def validateXml(id, doi):
    print("validate xml " + id)
    filepath = localfolder + 'newmeta/' + id + '.meta.xml'
    if not osp.exists(filepath):
        print('file not present')
        return
    result = subprocess.call(['java', '-jar','./control/xsl/jing.jar', '-c', './schema/uci_schema.rnc', filepath], cwd='/apps/eschol/erep/xtf')
    print(result)
    if result != 0:
        assert("VALIDATE FAILED for " + id)

def copyXml(id, doi):
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

def updateMetaFileWhereNeeded(idsdoi):
    print("updateMetaFileWhereNeeded")
    # update xml to introduce doi if the doi is not present
    filepath = './idsToFix.txt'
    f = open(filepath, "w")
    c = 0
    for id in idsdoi:
        print(id + "processing " + idsdoi[id])
        # call s3copy for this
        if updateXml(id, idsdoi[id]):
            validateXml(id, idsdoi[id])
            copyXml(id, idsdoi[id])
            f.write(id + '\n')
            c += 1
        if c > BATCH_SIZE:
            print("DONE WITH THE BATCH")
            break
    f.close()


print("run fix splash page")
x = escholIF()
# get the list of items where doi is present in DB
idsdoi = x.getJournalItemsWithDoi()

# for each of these run s3copy to get the splash page generated
#createidsToFix(idsdoi)
updateMetaFileWhereNeeded(idsdoi)

#for id in idsdoi:
    # call s3copy for this
    #recreateSplash(id)
    #break




