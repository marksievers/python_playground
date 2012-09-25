from xml.dom.minidom import parseString
import httplib

conn = httplib.HTTPConnection("www.metallica.com")
conn.request("GET", "/tour_date_list.asp?show=past&rpp=2000&page=1&sortdir=1&sortby=p.date")
response = conn.getresponse()
html = response.read()
conn.close()

#dom = parseString(html)
