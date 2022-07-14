from escholIF import escholIF

print("run this admin report")

x = escholIF()
all = x.getUnits();
f = open("report.txt", "w")
f.write("id,name,status,datefirstInEschol,numIssues, issues in 2022, issues in 2021, min year, max year, num articles, avg per year, num peer reviewed, percent reviewed, eissn, issn, CC url, doaj, downloads 2022, hits 2022, downloads 2021, hits 2021, downloads 2020, hits 2020\r\n")
for id in all:
    line = id + ','
    line += str(all[id][0].replace(',', ' ')) + ','
    line += str(all[id][1]) + ','

    y = x.dateFirstInEschol(id)
    line += str(y) + ','
    y = x.getNumIssues(id)
    line += str(y) + ','
    y = x.numCurrentIssues(id,'2022')
    line += str(y) + ','
    y = x.numCurrentIssues(id,'2021')
    line += str(y) + ','
    min,max = x.getMinMaxYear(id)
    line += str(min) + ','
    line += str(max) + ','
    a = x.getNumArticle(id)
    line += str(a) + ','
    if min and max and max > min:
        line += str(a/(max-min)) + ','
    else:
        line += 'None,'

    y = x.getPeerReviewed(id)
    line += str(y) + ','
    if a and y and a != 0:
        line += str(100*y/a) + ','
    else:
        line += 'None,'

    y,z = x.getIssn(id)
    line += str(y) + ','
    line += str(z) + ','

    y = x.getCCRights(id)
    line += str(y) + ','
    y = x.getDoaj(id)
    line += str(y) + ','
    y,z = x.getQueryStats(id,'2022')
    line += str(y) + ','
    line += str(z) + ','
    y,z = x.getQueryStats(id,'2021')
    line += str(y) + ','
    line += str(z) + ','
    y,z = x.getQueryStats(id,'2020')
    line += str(y) + ','
    line += str(z) + '\r\n'
    f.write(line)
    
print("done")
f.close()