from xml.dom.minidom import parseString
import httplib
import httplib2
import html5lib
from bs4 import BeautifulSoup

def buildEntry(node):
    tds = node.find_all('td')
    obj = {}
    obj['date'] = tds[0].string
    obj['location'] = tds[1].a.string
    obj['venue'] = tds[2].string
    if tds[3].a:
        link = tds[3].a['href']
        obj['link'] = link
        obj['setlist'] = buildSetList(link)
    print obj
    return obj

def buildSetList(path):
    html = getHtml(path)
    html = "".join([line.strip() for line in html.split("\n")])
    soup = BeautifulSoup(html, "lxml")
    entries = soup.find("h2", text='Setlist').find_next_sibling('table').find_all('a')
    songs = [r.string for r in entries]
    return songs

def getHtml(path):
    http = httplib2.Http()
    status, response = http.request(path)
    return response


html = getHtml("http://www.metallica.com/tour_date_list.asp?show=past&rpp=2000&page=1&sortdir=1&sortby=p.date")
soup = BeautifulSoup(html, "lxml")
tables = soup.find_all('table')

print "Tables size: ", len(tables)

for table in tables:
  if 'ddtTable_tourdates' == table['id']:
    rows = table.tbody.find_all('tr')

entries = [buildEntry(r) for r in rows]

#for r in entries:
#  print r
