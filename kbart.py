import creds
import mysql.connector
from mysql.connector import errorcode

from datetime import date

url_template = "https://escholarship.org/uc/{}"

cheaders = ["publication_title", # units.name
            "print_identifier", # ISSN
            "online_identifier", # e-ISSN units.eissn
	    "date_first_issue_online", # min issues.published
	    "num_first_vol_online", # min_issue.volume
	    "num_first_issue_online", # min_issue.issue
	    "date_last_issue_online", # max issues.published
	    "num_last_vol_online", # max_issue.volume
	    "num_last_issue_online", # max_issue.issue
	    "title_url", # "https://escholarship.org/uc/" + units.id
            "first_author",
	    "title_id", # units.id
            "embargo_info",
	    "coverage_depth", # fulltext
	    "notes", 
	    "publisher_name", # eScholarship Publishing
	    "publication_type", # serial
            "date_monograph_published_print",
            "date_monograph_published_online",
            "monograph_volume",
	    "monograph_edition",
	    "first_editor",
            "parent_publication_title_id",
	    "preceding_publication_title_id",
	    "access_type"] # F (free)

q = \
"""
SELECT units.name as title, units.id, units.attrs->>'$.issn' as issn, units.attrs->>'$.eissn' as eissn, first.published as fp, first.volume as fv, first.issue as fi, first.n as fn, last.published as lp, last.volume as lv, last.issue as li, last.n as ln
    FROM units 
    LEFT JOIN 
        (SELECT issues.unit_id, issues.volume, MIN(issues.issue) as issue, issues.published, issues.attrs->>'$.numbering' as n
         FROM issues 
         INNER JOIN 
            (SELECT unit_id, MIN(published) as min_pub FROM issues GROUP BY unit_id) as min
         ON issues.unit_id = min.unit_id and issues.published = min.min_pub
         GROUP BY issues.unit_id) as first
    ON units.id = first.unit_id
    INNER JOIN 
        (SELECT issues.unit_id, issues.volume, MAX(issues.issue) as issue, issues.published, issues.attrs->>'$.numbering' as n
         FROM issues 
         INNER JOIN 
             (SELECT unit_id, MAX(published) as max_pub FROM issues GROUP BY unit_id) as max
         ON issues.unit_id = max.unit_id and issues.published = max.max_pub
         GROUP BY unit_id) as last
    ON units.id = last.unit_id
    WHERE units.type = 'journal' and units.status = 'active'
"""

freq_q = "SELECT YEAR(published), count(*) as c FROM issues WHERE unit_id = '{unit_id}' GROUP BY YEAR(published) HAVING c > 1"

try:
    cnx = mysql.connector.connect(user=creds.escholDB.username,
                                  password=creds.escholDB.password,
                                  host=creds.escholDB.server,
                                  database=creds.escholDB.database,
                                  port=creds.escholDB.port)

    cursor = cnx.cursor(dictionary=True)

    cursor.execute(q)

    journals = []
    for r in cursor:
        journals.append({'title': r['title'],
                         'issn': r['issn'] if r['issn'] else "",
                         'eissn': r['eissn'] if r['eissn'] else "",
                         'fpub': r['fp'],
                         'fvol': r['fv'] if r['fn'] != b'issue_only' else "",
                         'fissue': r['fi'] if r['fn'] != b'volume_only' else "",
                         'lpub': r['lp'],
                         'lvol': r['lv'] if r['ln'] != b'issue_only' else "",
                         'lissue': r['li'] if r['ln'] != b'volume_only' else "",
                         'url': url_template.format(r['id']),
                         'id': r['id']})

    for j in journals:
        cursor.execute(freq_q.format(unit_id=j['id']))
        i = 0
        for r in cursor:
            i += 1
        if i == 0:
            j['fpub'] = j['fpub'].strftime("%Y")
            j['lpub'] = j['lpub'].strftime("%Y")
        else:
            j['fpub'] = j['fpub'].strftime("%Y-%m")
            j['lpub'] = j['lpub'].strftime("%Y-%m")
                
    print("\t".join(cheaders))
    for j in journals:
        outr = [j['title'],
                j['issn'] if not isinstance(j['issn'], bytes) else j['issn'].decode('utf-8'),
                j['eissn'] if not isinstance(j['eissn'], bytes) else j['eissn'].decode('utf-8'),
                j['fpub'],
                j['fvol'],
                j['fissue'],
                j['lpub'],
                j['lvol'],
                j['lissue'],
                j['url'],
                "",
                j['id'],
                "",
                "fulltext",
                "",
                "eScholarship Publishing",
                "serial",
                "", "", "", "", "", "", "",
                "F"]
        print("\t".join(outr))

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()
