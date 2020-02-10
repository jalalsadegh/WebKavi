import sqlite3
import urllib.error
import ssl
from iust import iust, iustSoap
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
# pip3 install requests
import requests

# connect to database
conn = sqlite3.connect(iust.dbname())
cur = conn.cursor()

# create tables if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS Pages (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT, error INTEGER, old_rank REAL, new_rank REAL)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Links (from_id INTEGER, to_id INTEGER)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

cur.execute('''SELECT id, url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1''')
row = cur.fetchone()

if row is not None:
    print('recrawling, or start a new DB.')
else:
    # get url 
    starturl = input('Input the web url:')

    # if user does not enter an input
    if len(starturl)<1: 
        starturl = 'https://www.w3schools.com/'

    # if contain slash remove last slash
    if starturl.endswith('/'): 
        starturl = starturl[:-1]

    # web = url
    web = starturl
    print(web)

    # get exact url and drop everything after slash 
    if starturl.endswith(tuple(iust.webPageExtensions())):
        pos = starturl.rfind('/')
        web = starturl[:pos]
        print(web)

    if len(web)>0:
        cur.execute('INSERT OR IGNORE INTO Webs(url)VALUES(?)',(web,))
        cur.execute('INSERT OR IGNORE INTO Pages(url, html, new_rank)VALUES(?, NULL, 1)',(starturl,))
        conn.commit()

cur.execute('SELECT url FROM Webs')
Webs = list()
for row in cur:
    Webs.append(row[0])
print(Webs)

many = 0
while True:
    if many<1:
        sval = input('How many pages:')
        if len(sval)<1: break
        many = int(sval)
    many = many-1
    cur.execute('''SELECT id, url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1''')
    row = cur.fetchone()
    try:
        from_id = row[0]
        url = row[1]
        print(from_id, url, end=' ')

    except:
        print('There are no unretrieved url in DB!')

        break

    try:
        # change request header (Prevent Web server robots/spider blocking, it like real browser)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        
        # get url document
        req = requests.get(url, headers=headers)
        
        # if error occured
        if req.status_code != 200:
            print('HttpRequest error code :', req.status_code)
            cur.execute('UPDATE Pages SET error = ? WHERE url = ?',(req.status_code,url))
            conn.commit()

        # if document content-type is not html
        if req.headers['content-type'] != 'text/html':
            print('right type:','text/html','wrong type:',req.headers['content-type'])
            cur.execute('DELETE FROM Pages WHERE url = ?', (url,))
            continue

        # get html document as byte
        html = req.content

        # get header
        # print(req.headers)

        # get html document as text
        # html = req.text
        # print(html)
        
        # iustSoap call from "iust.py"
        soupObj = iustSoap(html)
        soupObj.initial()
        print("\n" + soupObj.pageTitle)
        print(soupObj.pageDescription)
        print(soupObj.pageKeywords)
        # print(soupObj.soup.get_text())

    except KeyboardInterrupt:
        print('User interrupt!!')
    except:
        print('fail to retrieve')
        cur.execute('UPDATE Pages SET error = -1 WHERE url = ?',(url,))
        continue

    cur.execute('INSERT OR IGNORE INTO Pages(url, html, new_rank)VALUES(?, NULL, 1)',(url,))
    cur.execute('UPDATE Pages SET html = ? WHERE url = ?',(memoryview(html),url))
    conn.commit()

    tags = soupObj.soup('a')
    count = 0
    for tag in tags:
        # anchor link
        href = tag.get('href', None)

        # anchor hint
        anchorHint = tag.get('title', None)

        # anchor text
        anchorText = tag.text

        # check href link
        if href == None: continue

        # remove last slash from link
        if href.endswith('/'): href = href[:-1]

        # remove link bookmark 
        ipos = href.find('#')
        if ipos>1: href = href[:ipos]

        # ignore link that contain one of these extensions
        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ) : continue
        up = urlparse(href)

        # if link doesnt contain http://... then add url : url + pth   
        # e.g. http://www.iust.ac.ir  +  /content/58599/
        if len(up.scheme)<1:
            href = urljoin(url, href)
        
        # if href link is empty ignore statement and continue
        if len(href)<1: continue

        # for test 
        #print("{0} - {1} - {2}".format(anchorHint, href, anchorText))

        # check, just insert internal domain links 
        found = True
        for web in Webs:
            if href.startswith(web):
                found = False
                break

        if found == True:
            continue

        # insert anchor-link to table Pages
        cur.execute('INSERT OR IGNORE INTO Pages(url, html, new_rank)VALUES(?, NULL, 1)',(href,))
        conn.commit()

        # count hyperlinks
        count = count +1

        # get row id (to_id)
        cur.execute('SELECT id FROM Pages WHERE url = ? LIMIT 1',(href,))
        try:
            row = cur.fetchone()
            to_id = row[0]
        except:
            print('No links id!!')
            continue

        # insert link id
        cur.execute('INSERT OR IGNORE INTO Links(from_id, to_id)VALUES(?,?)',(from_id, to_id))
        conn.commit()
    print('links:',count)
