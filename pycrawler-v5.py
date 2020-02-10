"""
bs_objects is a nested dictionary which will used for returning bs4 object of each ulr that has been crawled. {url:[soup, time]}
to prevent any kind of run time error pick correct depth for crawling.
todo: save urls and content into DB
"""
import collections
from datetime import datetime
import time
from urllib.parse import urldefrag, urljoin, urlparse
import urllib.request
import urllib.error
import bs4
import requests
import os


class Crawler:
    def __init__(self, disallow, start_page, depth, crawled_before, bs_objects):
        # todo: get url that has been crawled before and check the age param and then go fo recrawling
        # crawled_before will be a dict with will contain url + age param {"url":"ageparam"}
        self.crawled_before = {}
        successpages = 0
        failpages = 0
        pqueue = collections.deque()  # queue for pages to getting into crawler
        pqueue.append(start_page)
        crawled = []
        domain = urlparse(start_page).netloc
        self.disallow = self.robots(domain)
        sess = requests.session()  # getting session
        while successpages < depth and pqueue:
            url = pqueue.popleft()  # go to next url for crawling
            # start reading page for crawling
            try:
                response = sess.get(url)
            except (requests.exceptions.MissingSchema,
                    requests.exceptions.InvalidSchema):
                self.log_saver("*FAILED*:" + str(url), "crawlLogs.txt")
                failpages += 1
                continue
            if not response.headers['content-type'].startswith('text/html'):  # just crawl HTML
                continue
            soup = bs4.BeautifulSoup(response.text, "html.parser")  # generate BS object
            bs_objects[str(url)] = [soup, time.time()]
            crawled.append(url)
            successpages += 1
            self.log_saver('Crawling:>' + url + ' ({0} bytes)'.format(len(response.text)), "crawlLogs.txt")
            links = self.getlinks(url, domain, soup)  # get links from a page
            for link in links:
                if not self.http_double_fix(link, crawled) and not self.http_double_fix(link, pqueue):
                    if link not in disallow:
                        link = self.tweak_links(link)
                        pqueue.append(link)
        self.log_saver('{0} pages crawled, {1} links failed.'.format(successpages, failpages), "crawlLogs.txt")

    def getlinks(self, pageurl, domain, soup):
        links = [a.attrs.get('href') for a in soup.select('a[href]')]  # getting the links from soup object
        links = [urldefrag(link)[0] for link in links]  # remove the fragment off of links
        links = [link for link in links if link]  # remove empty strings
        # if it's a relative link, change to absolute
        links = [link if bool(urlparse(link).netloc) else urljoin(pageurl, link) \
                 for link in links]
        if domain:  # removing other domain links if its a single domain crawl
            links = [link for link in links if self.samedomain(urlparse(link).netloc, domain)]
        return links

    def samedomain(self, netloc1, netloc2):  # check two domain if they was same but in other subdomain
        domain1 = netloc1.lower()
        if '.' in domain1:
            domain1 = domain1.split('.')[-2] + '.' + domain1.split('.')[-1]

        domain2 = netloc2.lower()
        if '.' in domain2:
            domain2 = domain2.split('.')[-2] + '.' + domain2.split('.')[-1]
        return domain1 == domain2

    def http_double_fix(self, url, listobj):  # combain http and https version of a single page to not going in
        # crawler for second time
        http_version = url.replace('https://', 'http://')
        https_version = url.replace('http://', 'https://')
        return (http_version in listobj) or (https_version in listobj)

    def tweak_links(self, link):
        if link.endwith("/"):
            link = link[:-1]
        ipos = link.find("#")
        if ipos > 1:
            link = link[:ipos]
        if link.endswith('.png') or link.endswith('.jpg') or link.endswith('.gif'):
            link = ""
        if link in self.crawled_before:
            if self.crawled_before[link] + 172800 <= time.time():
                return None
        return link

    def robots(self, sdomain):  # make crawler to follow the robots.txt file rules
        disallow = []
        disallowswap = []
        url = "http://" + sdomain + "/robots.txt"
        try:
            urllib.request.urlretrieve(url, "robot.txt")
        except urllib.error as e:
            self.log_saver(e, "logs.txt")
            return []
        if os.path.getsize('robots.txt') >= 15000:  # controlling the robots.txt file to be real
            os.remove('rm robots.txt')
            return []
        with open('robots.txt', 'rb') as robo:
            for line in robo:
                line = str(line)
                if 'User-agent: *' in line:
                    break
                elif 'Disallow:' in line:
                    disallow.append(line)
                elif 'Allow:' in line:
                    continue
                elif '' in line:
                    break
        os.remove('rm robots.txt')
        for lk in disallow:
            lk = lk.replace('Disallow:', '')
            if ' */' in lk:
                lk = lk.replace(' */', sdomain + '/')
            elif ' /*/' in lk:
                lk = lk.replace(' /*/', sdomain + '/')
            elif ' /*.' in lk and '$' in lk:
                lk = lk.replace('$', '')
                lk = lk.replace(' /*.', '.')
            elif ' /' in lk:
                lk = lk.replace(' /', sdomain + '/')
            if '/*\n' in lk:
                lk = lk.replace('/*\n', '')
            elif '*\n' in lk:
                lk = lk.replace('*\n', '')
            lk = lk.replace('\n', '')
            disallowswap.append(lk)
        return disallowswap

    def log_saver(self, message, file=''):
        try:
            with open(str(file), "a") as file:
                file.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {str(message)}")
        except Exception as e:
            print(e)
