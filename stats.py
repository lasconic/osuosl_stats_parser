import requests
from bs4 import BeautifulSoup
from string import Template
import datetime as dt
import os.path


def getLinkFromTd(td):
    a = td.find('a')
    return a['href']

def processUrl(url, d='', needle=''):
        #print url
        filename = d.replace("/", "") + ".html"
        print filename
        filePath = "data/"+filename
        if os.path.isfile(filePath):
            print "hit cache"
            f = open(filePath, 'r')
            data = f.read()
            f.close()
        else:
            print "miss cache"
            r  = requests.get(url)
            data = r.text
            #cache the file
            f = open(filePath, 'w')
            f.write(data)
            f.flush()
            f.close()

        bs = BeautifulSoup(data)
        table = bs.findAll('table', {'class': 'aws_data'})[1]
        dlRows = table.findAll('tr')
        result = []
        for dlRow in dlRows:
            u = dlRow.findAll('td')
            if len(u) > 1:
                tdUrl = u[0]
                dlCount = u[1].text
                link = getLinkFromTd(tdUrl)
                count = int(dlCount)
                filename = link[(link.rfind("/")+1):]
                if (needle in filename):
                    result.append((link, count))
        return result

def processAll(needle):
    result = {}
    currentYear = dt.date.today().year
    currentMonth = dt.date.today().month
    start = False
    for year in range(2013, 2018, 1):
        for month in range(1, 13, 1):
            strMonth = '%0*d' % (2, month)
            strYear = str(year)
            url = "https://awstats.osuosl.org/reports/ftp.osuosl.org-musescore/" + strYear + "/" + strMonth + "/awstats.ftp.osuosl.org-musescore.urldetail.html"
            x = strYear + "/" + strMonth
            linkCounts = processUrl(url, x, needle)
            for linkCount in linkCounts:
                y = 0
                if linkCount and (len(linkCount) == 2):
                    y = linkCount[1]
                # don't write value if we are still 0
                if y != 0:
                    start = True
                if not start:
                    continue
                print x + "," + str(y)
                if x in result:
                    result[x] = y + result[x]
                else:
                    result[x] = y
            #break on today
            if (year == currentYear) and (month == currentMonth):
                break
    r = []
    for key in sorted(result):
        r.append((key, result[key]))
    return r



def createGraph(needle):
    result = processAll(needle)
    f = open('template.html', 'r')
    content = f.read()
    f.close()
    total = 0
    data = """var data = new google.visualization.DataTable();
        data.addColumn('string', 'Month');
        data.addColumn('number', 'Downloads');
        data.addRows(["""
    for r in result:
        data += "['" + r[0] + "', " + str(r[1]) + "],"
        total += int(r[1])
    data += "]);"

    print "Total downloads: " + str(total)
    d = {"charData": data, "needle": needle, "total": str(total)}

    src = Template( content )
    #do the substitution
    content = src.substitute(d)

    out = open('result.html', 'w')
    out.write(content)
    out.close()


#processUrl("https://awstats.osuosl.org/reports/ftp.osuosl.org-musescore/2014/12/awstats.ftp.osuosl.org-musescore.urldetail.html")
#createGraph("MuseScore-2.0.3.dmg")

createGraph(".exe")

#createGraph("2.0beta1")
#createGraph("exe")
#createGraph("MuseScore-1.3")

