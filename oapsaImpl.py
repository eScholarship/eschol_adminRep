
import oapsaDbIntf

class oapsaController:
    # a list of journals to enable for OASPA
    journalIds = ['psf','fb']
    ojsIf = oapsaDbIntf.oapsaOjsIF()
    escholIf = oapsaDbIntf.oapsaEscholIF()
    def __init__(self):
        print("lets do the work")
        self.nameToIds = self.ojsIf.getJournalIds(self.journalIds)
        for name in self.nameToIds:
            self.getDataFromOJS(self.nameToIds[name])
            self.getDataFromJschol()
            self.updateJscholAsNeeded()

    def getDataFromOJS(self, jid):
        print("get data from OJS")
        self.ojsData = self.ojsIf.getDates(jid)

    def getDataFromJschol(self):
        print("get relevant info from Jschol")
        articleIds = self.ojsData.keys()
        # get the article ids to query arks
        self.idToArk = self.escholIf.getjscholIds(articleIds)
        self.escholData = self.escholIf.getItemAttrs(self.idToArk.values())

    def updateJscholAsNeeded(self):
        print("update attrs in jschol")
        for id in self.idToArk:
            ojsDates = self.ojsData[int(id)]
            escholDates = self.escholData[self.idToArk[id]]
            if ojsDates[0] is None or ojsDates[1] is None or ojsDates[2] is None:
                print("skipping items with null dates " + id)
            else:
                sdate = str(ojsDates[0].strftime("%m-%d-%Y"))
                adate = str(ojsDates[1].strftime("%m-%d-%Y"))
                pdate = str(ojsDates[2].strftime("%m-%d-%Y"))

                if escholDates[0] is None or escholDates[0].decode('utf-8') != sdate or escholDates[1].decode('utf-8') != adate or escholDates[2].decode('utf-8') != pdate:
                    self.escholIf.updateDates(self.idToArk[id], sdate, adate, pdate, escholDates[3])

print("starting oapsa")

ctrl = oapsaController()

print("ending oapsa")