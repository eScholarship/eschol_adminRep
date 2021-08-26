import creds
import mysql.connector

# get the list of journel along with their title
# 

########################################
#
# Gets the series, group info from eschol DB 
#
########################################
class escholIF:
    queryUnits = "select id, name, status from units where type = 'journal'"
    queryDateFirst = "SELECT min(published) FROM items where id in (select item_id from unit_items where unit_id = '{param}')"
    queryNumIssues = "select count(*) from issues where unit_id = '{param}'"
    queryCurrentIssueCount = "select count(*) from issues where extract(Year from published) = '{param1}' and unit_id = '{param}'"
    queryNumArticle = "select count(*) from unit_items where unit_id = '{param}'"
    queryMinMaxYear = "select extract(Year from min(published)), extract(Year from max(published)) from issues where unit_id = '{param}'"
    queryPeerReviewed = "select count(*) from items where attrs->>'$.is_peer_reviewed' = 'true' and id in (select item_id from unit_items where unit_id = '{param}')"
    queryISSN = "select attrs->>'$.eissn', attrs->>'$.issn' from units where id = '{param}'"
    queryDoiNums = "SELECT count(*) FROM items where id in (select item_id from unit_items where unit_id = '{param}') and attrs->>'$.doi' is not null"
    queryCCRights = "select rights from items where id in (select item_id from unit_items where unit_id = '{param}') and rights is not null order by published limit 1"
    queryDoaj = "select attrs->>'$.doaj' from units where id = '{param}'"
    queryStats = "select sum(attrs->>'$.dl'), sum(attrs->>'$.hit')  from unit_stats where month like '{param1}%' and unit_id = '{param}' and attrs->>'$.dl' is not null and attrs->>'$.hit' is not null"

    queryForKeeper = "select id, attrs->>'$.eissn', attrs->>'$.issn', name from units where type = 'journal' and (attrs->>'$.eissn' is not null or attrs->>'$.issn' is not null)"
    queryLastVolIssue = "select volume, issue from issues where unit_id = '{param}' and published = (select max(published) from issues where unit_id = '{param}' and volume !='0') order by CAST(volume AS SIGNED) DESC, CAST(issue as SIGNED) DESC limit 1"
    queryFirstVolIssue = "select volume, issue from issues where unit_id = '{param}' and published = (select min(published) from issues where unit_id = '{param}'  and volume !='0') order by CAST(volume AS SIGNED), CAST(issue as SIGNED) limit 1"

    queryJournalItemsWithDoi = "select id, attrs->>'$.doi' from items where attrs->>'$.doi' is not null and id in (select item_id from unit_items where unit_id in (select id from units where type='journal'))"

    def __init__(self):
        print("connect to eschol DB here")

        self.cnxn = mysql.connector.connect(user=creds.escholDB.username, 
                              password=creds.escholDB.password,
                              host=creds.escholDB.server,
                              database=creds.escholDB.database,
                              port=creds.escholDB.port)

        self.cursor = self.cnxn.cursor()

    def getJournalItemsWithDoi(self):
        print("read JournalItemsWithDoi")
        self.cursor.execute(self.queryJournalItemsWithDoi)
        idsDois = {}
        for row in self.cursor:
            idsDois[row[0]] = str(row[1].decode('utf-8'))

        return idsDois


    def getUnits(self):
        print("read all the Elements related groups")
        self.cursor.execute(self.queryUnits)
        groupSeries = {}
        for row in self.cursor:
            groupSeries[row[0]] = (row[1], row[2])

        return groupSeries

    def getUnitsForKeepers(self):
        print("read all the units with ISSN")
        self.cursor.execute(self.queryForKeeper)
        groupSeries = {}
        for row in self.cursor:
            groupSeries[row[0]] = (row[1], row[2], row[3])

        return groupSeries

    def getFirstVolIssue(self, unitid):
        print("read first vol issues")
        # number of issues for this unitid
        # number of years between first and last year
        query = self.queryFirstVolIssue.format(param=unitid)
        self.cursor.execute(query)
        vol = None
        issue = None
        for row in self.cursor:
            vol = row[0]
            issue = row[1]

        return vol, issue

    def getLastVolIssue(self, unitid):
        print("read last vol issues")
        # number of issues for this unitid
        # number of years between first and last year
        query = self.queryLastVolIssue.format(param=unitid)
        self.cursor.execute(query)
        vol = None
        issue = None
        for row in self.cursor:
            vol = row[0]
            issue = row[1]

        return vol, issue

    def dateFirstInEschol(self, unitid):
        print("read first in eschol")
        query = self.queryDateFirst.format(param=unitid)
        self.cursor.execute(query)
        minPubDate = None
        for row in self.cursor:
            minPubDate = row[0]
        return minPubDate

    def getNumIssues(self, unitid):
        print("read num issues")
        # number of issues for this unitid
        # number of years between first and last year
        query = self.queryNumIssues.format(param=unitid)
        self.cursor.execute(query)
        count = None
        for row in self.cursor:
            count = row[0]
        return count

    def numCurrentIssues(self, unitid, year):
        print("read current year issues")
        query = self.queryCurrentIssueCount.format(param=unitid, param1=year)
        self.cursor.execute(query)
        count = None
        for row in self.cursor:
            count = row[0]
        return count



    def getMinMaxYear(self, unitid):
        print("read minmax years issues")
        # number of issues for this unitid
        # number of years between first and last year
        query = self.queryMinMaxYear.format(param=unitid)
        self.cursor.execute(query)
        minYear = None
        maxYear = None
        for row in self.cursor:
            minYear = row[0]
            maxYear = row[1]

        return minYear, maxYear

    def getNumArticle(self, unitid):
        print("read num articles")
        query = self.queryNumArticle.format(param=unitid)
        self.cursor.execute(query)
        count = None
        for row in self.cursor:
            count = row[0]
        return count

    def getPeerReviewed(self, unitid):
        print("read peer reviewed articles")
        query = self.queryPeerReviewed.format(param=unitid)
        self.cursor.execute(query)
        count = None
        for row in self.cursor:
            count = row[0]
        return count

    def getIssn(self, unitid):
        print("read issn")
        query = self.queryISSN.format(param=unitid)
        self.cursor.execute(query)
        eissn = None
        issn = None
        for row in self.cursor:
            eissn = row[0]
            issn = row[1]

        return eissn, issn

    #queryCCRights
    def getCCRights(self, unitid):
        print("read cc rights")
        query = self.queryCCRights.format(param=unitid)
        self.cursor.execute(query)
        rights = None
        for row in self.cursor:
            rights = row[0]
        return rights

    #queryDoaj
    def getDoaj(self, unitid):
        print("read cc rights")
        query = self.queryDoaj.format(param=unitid)
        self.cursor.execute(query)
        doaj = None
        for row in self.cursor:
            doaj = row[0]
        return doaj

    #queryStats
    def getQueryStats(self, unitid, year):
        print("read current year issues")
        query = self.queryStats.format(param=unitid, param1=year)
        self.cursor.execute(query)
        dl = None
        req = None
        for row in self.cursor:
            dl = row[0]
            req = row[1]
        return dl, req
