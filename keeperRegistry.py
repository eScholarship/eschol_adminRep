from escholIF import escholIF
from datetime import date
print("run this keeper registry report")

x = escholIF()
all = x.getUnitsForKeepers();
f = open("keeper_report.txt", "w")
f.write("eISSN,ISSN,Title of the resource,Publisher of the resource,Archive starting date,Archive ending date,Status of archiving process (archived),Holdings,Address of the archived resource (URL or other),Updating date\n")
for id in all:
    line = ''
    if all[id][0]:
        line += str(all[id][0].decode('utf-8'))
    line += ','
    if all[id][1]:
        line += str(all[id][1].decode('utf-8'))
    line += ','
    line += str(all[id][2].replace(',',' ')) + ','
    line += 'eScholarship Publishing,'
    min,max = x.getMinMaxYear(id)
    if not min or not max:
        continue
    if min:
        line += str(min)
    line += ','
    if max:
        line += str(max)
    line += ','
    line += 'archived,'

    y,z = x.getFirstVolIssue(id)
    if y and z:
        line += y + ':' + z + '-'
    else:
        line += 'none:'
    y,z = x.getLastVolIssue(id)
    if y and z:
        line += y + ':' + z + ','
    else:
        line += 'none,'
    
    line += 'https://escholarship.org/uc/' + str(id) + ','
    z = date.today()
    line += str(z.strftime("%m/%d/%Y")) + '\n'
    
    f.write(line)
    
print("done")
f.close()