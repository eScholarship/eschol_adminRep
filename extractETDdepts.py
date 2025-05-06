from escholIF import escholIF
import os.path as osp
filefolder = "/apps/eschol/erep/data/13030/pairtree_root/"
codeToCampusMapping = {
    "0028":"UCB",	
    "0029":"UCD",	
    "0030":"UCI",	
    "1660":"UCM",	
    "0032":"UCR",	
    "0031":"UCLA",	
    "0035":"UCSB",	
    "0036":"UCSC",	
    "0033":"UCSD",	
    "0034":"UCSF"	
    }

def getText(line):
    print("extracting text")
    print(line)
    parts = line.split('>')
    parts = parts[1].split('<')
    return parts[0]

def extractDepartment(id):
    print("Extract info for escholid " + id)
    filepath = filefolder + id[0:2] +'/'+ id[2:4] + '/'+ id[4:6]+'/'+ id[6:8] +'/'+ id[8:10]+ '/' + id +'/meta/'+ id + '.meta.xml'
    if not osp.exists(filepath):
        raise RuntimeError(filepath + ' not found')
    f = open(filepath, "r", errors='ignore')
    inst_code = None
    inst_contact = None
    while True:
        line = f.readline()
        if '</DISS_inst_code>' in line:
            inst_code = getText(line)
        if '</DISS_inst_contact>' in line:
            inst_contact = getText(line)
        if not line:
            break
        if inst_code and inst_contact:
            break

    f.close()
    return inst_code, inst_contact

def createReport():
    fo = open('etd_dept_report.txt',"w")
    x = escholIF()
    ids = x.getETDids()
    #ids = ['qt09v531h1', 'qt0nd877w2', 'qt0ts2206g']
    for escholId in ids:
        code, contact = extractDepartment(escholId)
        if code and contact:
           output = f'{escholId}, {codeToCampusMapping[code]}, {contact}\n'
           print(output)
           fo.write(output)

    fo.close()

print("start")
createReport()
print("done")
