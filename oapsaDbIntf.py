
import creds
import mysql.connector

class oapsaEscholIF:
    queryArks = "select id, external_id from arks where source = 'ojs' and external_id in ('{param}')"
    queryAttrs = "select id, attrs->>'$.pub_submit', attrs->>'$.pub_accept', attrs->>'$.pub_publish', attrs  from items where id in ('{param}')"
    updateAttrs = "update items set attrs = JSON_SET(attrs,'$.pub_submit','{param1}', '$.pub_accept','{param2}', '$.pub_publish', '{param3}') where id = '{param4}'"
    setAttrs = "update items set attrs = JSON_OBJECT('pub_submit','{param1}', 'pub_accept','{param2}', 'pub_publish','{param3}') where id = '{param4}'"
    #updateAttrs = "update items set attrs = JSON_SET(attrs,'$.pub_submit','{param1}', attrs->>'$.pub_accept','{param2}') where id = '{param4}'"
    def __init__(self):
        print("connect to eschol DB here")

        self.cnxn = mysql.connector.connect(user=creds.escholDB.username, 
                              password=creds.escholDB.password,
                              host=creds.escholDB.server,
                              database=creds.escholDB.database,
                              port=creds.escholDB.port)

        self.cursor = self.cnxn.cursor()

    def getjscholIds(self, articleIds):
        print("get the journal ids for given ojs article ids")        
        joined_ids = "','".join(list(map(str, articleIds)))
        query = self.queryArks.format(param=joined_ids)
        self.cursor.execute(query)
        idToArk = {}
        for row in self.cursor:
            idToArk[row[1]] = row[0]

        print(str(len(articleIds)) + " Ids with Ark " + str(len(idToArk)))
        return idToArk

    def getItemAttrs(self, arks):
        print("get item attrs for all the items  in the journal")
        joined_arks = "','".join(arks)
        query = self.queryAttrs.format(param=joined_arks)
        self.cursor.execute(query)
        arkToDates = {}
        for row in self.cursor:
            arkToDates[row[0]] = (row[1], row[2], row[3], row[4])

        return arkToDates

    def updateDates(self, id, submitted, accepted, published, attrs):
        print("set item attrs with dates")

        if attrs is None:
            query = self.setAttrs.format(param1=submitted, param2=accepted, param3=published, param4=id)
        else:
            query = self.updateAttrs.format(param1=submitted, param2=accepted, param3=published, param4=id)
        #query = self.updateAttrs.format(param1=submitted, param2=accepted, param4=id)
        self.cursor.execute(query)
        self.cnxn.commit()


class oapsaOjsIF:
    queryJournalId = "SELECT journal_id, path FROM ojs.journals where path in ('{param}')"
    queryDates = """select articles.article_id, articles.date_submitted, edit_decisions.date_decided, 
                published_articles.date_published from articles, edit_decisions, published_articles 
                where (articles.article_id=edit_decisions.article_id and edit_decisions.article_id=published_articles.article_id 
                and articles.journal_id='{param}' and edit_decisions.decision='1')"""


    def __init__(self):
        print("connect to ojs DB here")

        self.cnxn = mysql.connector.connect(user=creds.ojsDB.username, 
                              password=creds.ojsDB.password,
                              host=creds.ojsDB.server,
                              database=creds.ojsDB.database,
                              port=creds.ojsDB.port)

        self.cursor = self.cnxn.cursor()

    def getJournalIds(self, jnames):
        print("get the journal ids")
        joined_names = "','".join(jnames)
        query = self.queryJournalId.format(param=joined_names)
        self.cursor.execute(query)
        nameToId = {}
        for row in self.cursor:
            nameToId[row[1]] = row[0]

        return nameToId


    def getDates(self, journalId):
        print("get the dates from OJS for published accepted journal items")
        query = self.queryDates.format(param=journalId)
        self.cursor.execute(query)
        idToDates = {}
        for row in self.cursor:
            idToDates[row[0]] = (row[1], row[2], row[3])

        return idToDates