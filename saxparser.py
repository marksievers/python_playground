from xml.dom.minidom import parseString
import httplib

xml = """
    <root>
      <parent>
        <child1>X</child1>
        <child2>Y</child2>
      </parent>
    </root>
     """

dom = parseString(xml)
children = [c.localName for p in dom.getElementsByTagName("parent") for c in p.childNodes if c.nodeType == c.ELEMENT_NODE]
print children
for c in children:
  print c

conn = httplib.HTTPConnection("www.metallica.com")
conn.request("GET", "/tour_date_list.asp?show=past&rpp=2000&page=1&sortdir=1&sortby=p.date")
r1 = conn.getresponse()
print r1.status, r1.reason
data1 = r1.read()
conn.close()

print data1
