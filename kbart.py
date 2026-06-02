from datetime import date
import os
import csv

import mysql.connector
from mysql.connector import errorcode

import creds

OUTDIR = os.environ.get("OUTDIR")

url_template = "https://escholarship.org/uc/{}"
fname_template = "CDL_Global_eScholarship_{}.txt"

cheaders = ["publication_title", # units.name
            "print_identifier", # ISSN
            "online_identifier", # e-ISSN units.eissn
	        "date_first_issue_online", # min_issue.published
	        "num_first_vol_online", # min_issue.volume
	        "num_first_issue_online", # min_issue.issue
	        "date_last_issue_online", # date of publication for the final issue of an archived journal
	        "num_last_vol_online", # volume number of most recent volume of archived journal
	        "num_last_issue_online", # issue number of most recent volume of archived journal
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
SELECT units.name as title, units.id, units.attrs->>'$.issn' as issn, units.attrs->>'$.eissn' as eissn, units.status as status, first.published as fp, first.volume as fv, first.issue as fi, first.n as fn, last.published as lp, last.volume as lv, last.issue as li, last.n as ln
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
    WHERE units.type = 'journal' and units.status != 'hidden'
"""

freq_q = "SELECT count(*) as total FROM (SELECT YEAR(published), count(*) as c FROM issues WHERE unit_id = '{unit_id}' GROUP BY YEAR(published) HAVING c > 1) as t"

index_html = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>KBART file for CDL eScholarship serials</title>
    </head>
    <body>
        <h1>KBART file for CDL eScholarship serials</h1>
        <a href="{0}">{0}</a>
    </body>
</html>
"""

try:
    cnx = mysql.connector.connect(user=creds.escholDB.username,
                                  password=creds.escholDB.password,
                                  host=creds.escholDB.server,
                                  database=creds.escholDB.database,
                                  port=creds.escholDB.port,
                                  auth_plugin="mysql_native_password")

    cursor = cnx.cursor(dictionary=True)

    cursor.execute(q)

    journals = []
    for r in cursor:
        result = {
            "publication_title": r["title"],
            "print_identifier": r["issn"].decode("utf-8") if r["issn"] else "",
            "online_identifier": r["eissn"].decode("utf-8") if r["eissn"] else "",
            "date_first_issue_online": r["fp"],
            "title_url": url_template.format(r["id"]),
            "title_id": r["id"],
            "coverage_depth": "fulltext",
            "publisher_name": "eScholarship Publishing",
            "publication_type": "serial",
            "access_type": "F"
        }

        if r["fn"] != b"issue_only":
            result["num_first_vol_online"] = r["fv"]
        if r["fn"] != b"volume_only":
            result["num_first_issue_online"] = r["fi"]

        if r["status"] == "archived":
            result["date_last_issue_online"] = r["lp"]
            if r["ln"] != b"issue_only":
                result["num_last_vol_online"] = r["lv"]
            if r["ln"] != b"volume_only":
                result["num_last_issue_online"] = r["li"]
        journals.append(result)

    for j in journals:
        # if there are multiple issues in any year
        # include the month in the date format
        cursor.execute(freq_q.format(unit_id=j["title_id"]))
        result = cursor.fetchone()
        date_format = "%Y-%m" if result["total"] > 0 else "%Y"
        j["date_first_issue_online"] = j["date_first_issue_online"].strftime(date_format)
        if "date_last_issue_online" in j:
            j["date_last_issue_online"] = j["date_last_issue_online"].strftime(date_format)

    filename = fname_template.format(date.today().strftime("%Y-%m-%d"))
    with open(os.path.join(OUTDIR, "index.html"), "w") as f:
        f.write(index_html.format(filename))

    with open(os.path.join(OUTDIR, filename), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cheaders, restval="")
        writer.writeheader()
        writer.writerows(journals)

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()
