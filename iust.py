import math
import socket
import sqlite3
# pip3 install requests
import requests
# pip3 install networkx
import networkx as nx
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
# from nltk import clean_html

#------------------------------------------------------------#
class iust:
    # get sqlite db name
    def dbname():
        return 'spider.sqlite'

    # get domain name
    # e.g. url: http://iust.ac.ir/content/58599/
    # ► return → iust.ac.ir
    def getDomainName(url):
        domain = urlparse(url).netloc
        return domain

    # get protocol
    # e.g. url: http://iust.ac.ir/content/58599/ 
    # ► return → http
    def getProtocol(url):
        protocol = urlparse(url).scheme
        return protocol

    # get server ip address
    # e.g. url: http://iust.ac.ir/content/58599/ 
    # ► return → 194.225.230.88
    def getHostIp(url):
        loc = urlparse(url).netloc
        return socket.gethostbyname(loc)

    # get path
    # e.g. url: http://iust.ac.ir/content/58599/ 
    # ► return → /content/58599/
    # e.g. url: http://iust.ac.ir/index.php?site=cultural_mng 
    # ► return → /index.php?site=cultural_mng
    def getURLResource(url):
        u = urlparse(url)
        result = ''
        if not urlparse(url).query:
            result = u.path
        else:
            result = u.path + '?' + u.query
        return result

    # page has bookmark true/false
    # e.g. url: http://www.iust.ac.ir/content/58599/#page-bookmark 
    # ► return → True
    def UrlHasBookmark(url):
        fragment = urldefrag(url)[1]
        return False if not fragment else True

    # get bookmark
    # e.g. url: http://www.iust.ac.ir/content/58599/#overview
    # ► return → overview
    def getUrlBookmark(url):
        fragment = urldefrag(url)[1]
        return fragment

    def getPureText():
        # remove html tags
        return 'method'

    # Get request header, e.g. 
    # print(iust.getHttpRequestHeader(requests.get("http://www.iust.ac.ir/content/58599/")))
    #  ► return → {'Date': 'Sat, 08 Feb 2020 18:07:35 GMT', 'Server': 'Apache/2.4.23 (Fedora) OpenSSL/1.0.2j-fips PHP/5.6.29', 'X-Powered-By': 'PHP/5.6.29', 'Set-Cookie': '4f2647dywID_8ef84_mysid=7; expires=Sun, 07-Feb-2021 18:07:35 GMT; Max-Age=31536000; path=/; domain=.iust.ac.ir; httponly, 4f2647dywID_8ef84_mylang=fa; expires=Sun, 07-Feb-2021 18:07:35 GMT; Max-Age=31536000; path=/; domain=.iust.ac.ir; httponly, 4f2647dywID_8ef84_data=%5B%5D; expires=Sun, 07-Feb-2021 18:07:35 GMT; Max-Age=31536000; path=/; domain=.iust.ac.ir; httponly, 4f2647dywID_8ef84_sesid=72213aabb0dd6e120f93ad22ade024f1; path=/; domain=.iust.ac.ir; httponly', 'X-UA-Compatible': 'IE=edge,chrome=1', 'X-Frame-Options': 'SAMEORIGIN', 'expires': 'Sat, 08 Feb 2020 18:27:35  GMT', 'Cache-Control': 'private,', 'Vary': 'Accept-Encoding,User-Agent', 'Content-Encoding': 'gzip', 'Content-Length': '10705', 'Keep-Alive': 'timeout=5, max=99', 'Connection': 'Keep-Alive', 'Content-Type': 'text/html; charset=UTF-8'}
    def getHttpRequestHeader(request):
        return request.headers

    # web page extensions
    def webPageExtensions():
        return [".htm", ".html", ".asp", ".aspx", ".jsp", ".php", ".html", ".ashx", ".jspx"]


    # calculate TF : Term Frequency
    # TF(i,j) = n(i,j) / Σ n(i,j)  1<=n<=k
    # The number of times a term appears in a document divded by the total number of terms in the document. Every document has its own term frequency.
    # e.g.
    # documentA = 'the man went out for a walk'  
    # documentB = 'the children sat around the fire'
    #
    # bagOfWordsA = documentA.split(' ')  --> ['the','man','went','out','for','a','walk']
    # bagOfWordsB = documentB.split(' ')  --> ['the','children','sat','around','the','fire']
    #
    # By casting the bag of words to a set, we can automatically remove any duplicate words.
    # uniqueWords = set(bagOfWordsA).union(set(bagOfWordsB))
    #
    # numOfWordsA = dict.fromkeys(uniqueWords, 0)
    # for word in bagOfWordsA: numOfWordsA[word] += 1
    #
    # numOfWordsB = dict.fromkeys(uniqueWords, 0)
    # for word in bagOfWordsB: numOfWordsB[word] += 1
    # 
    #   a   around  children  fire   for  man  out  sat  the  walk  went
    #0  1   0       0         0      1    1    1    0    1    1     1
    #1  0   1       1         1      0    0    0    1    2    0     0
    #
    # tfA = computeTF(numOfWordsA, bagOfWordsA)
    # tfB = computeTF(numOfWordsB, bagOfWordsB)
    #
    def computeTF(wordDict, bagOfWords):
        tfDict = {}
        bagOfWordsCount = len(bagOfWords)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bagOfWordsCount)
        return tfDict

    # calculate IDF : Inverse Data Frequency
    # The log of the number of documents divided by the number of documents that contain the word w. 
    # Inverse data frequency determines the weight of rare words across all documents in the corpus.
    # idf(w) = log(N/dft)
    # The IDF is computed once for all documents.
    # e.g. 
    # idfs = computeIDF([numOfWordsA, numOfWordsB])
    def computeIDF(documents):
        N = len(documents)
        idfDict = dict.fromkeys(documents[0].keys(), 0)
        for document in documents:
            for word, val in document.items():
                if val > 0:
                    idfDict[word] += 1

        for word, val in idfDict.items():
            idfDict[word] = math.log(N / float(val))
        return idfDict

    # calculate TF.IDF
    # the TF-IDF is simply the TF multiplied by IDF.
    # compute the TF-IDF scores for all the words in the corpus : e.g.
    # 
    # tfidfA = computeTFIDF(tfA, idfs)
    # tfidfB = computeTFIDF(tfB, idfs)
    # df = pd.DataFrame([tfidfA, tfidfB])
    #
    #   a          around    children    fire       for        man       out       sat        the  walk      went
    #0  0.099021   0.000000  0.000000    0.000000   0.099021   0.099021  0.099021  0.000000   0.0  0.099021  0.099021
    #1  0.000000   0.115525  0.115525    0.000000   0.000000   0.000000  0.000000  0.115525   0.0  0.000000  0.000000
    def computeTFIDF(tfBagOfWords, idfs):
        tfidf = {}
        for word, val in tfBagOfWords.items():
            tfidf[word] = val * idfs[word]
        return tfidf

    # TF-IDF alternative
    # TF-IDF alternative Solution, use the class provided by sklearn
    #
    # vectorizer = TfidfVectorizer()
    # vectors = vectorizer.fit_transform([documentA, documentB])
    # feature_names = vectorizer.get_feature_names()
    # dense = vectors.todense()
    # denselist = dense.tolist()
    # df = pd.DataFrame(denselist, columns=feature_names)


    # make grah from database table Links
    # e.g. 
    # gr = iust.getGraph()
    # print(gr.nodes())
    def getGraph():
        # create empty networx graph
        graph = nx.Graph()

        # get all links (from_id -> to_id) from database
        try:
            con = sqlite3.connect(iust.dbname())
            cur = con.cursor()
            cur.execute('''SELECT * FROM Links''')
            rows = cur.fetchall()
            
            # add to graph
            for row in rows:
                # read column "from_id" by table index
                from_id = row[0]
                # read column "to_id" by table index
                to_id = row[1]
                # add to graph
                # graph.add_nodes_from([from_id, to_id])   OR:
                graph.add_edge(from_id, to_id) 

            cur.close()
            return graph
        except error as error:
            print(error)
        finally:
            if (con):
                con.close()

    
#------------------------------------------------------------#
class iustSoap:
    def __init__(self, htmlDoc):
        self.pageTitle = '0'
        self.pageDescription = '0'
        self.pageKeywords = '0'
        self.html = htmlDoc
        self.soup = BeautifulSoup(htmlDoc, 'html.parser')
        
    def initial(self):
        # page title
        self.pageTitle = self.soup.title.string

        # get page meta description (if not fount return 0)
        description = self.soup.find('meta', attrs={'name': lambda x: x and x.lower()=='description'})
        metaDescription = '0' if not description else description['content'].encode('utf-8')
        self.pageDescription = metaDescription
    
        # get page meta keywords (if not fount return 0)
        keywords = self.soup.find('meta', attrs={'name': lambda x: x and x.lower()=='keywords'})
        metaKeywords = '0' if not keywords else keywords['content'].encode('utf-8')
        self.pageKeywords = metaKeywords

    def getHtml(self):
        return self.html

#------------------------------------------------------------#
### test

# if __name__ == "__main__":
    #----------------------------------------
    ### Graph  
    ### get graph
    # gr = iust.getGraph()

    # print(gr.nodes())
    # print('\n')
    # print(len(gr))
    # print('\n')
    # print(gr.edges())
    # print('\n')

    ### Compute the degree centrality for nodes.
    # print(nx.degree_centrality(gr))

    ### Closeness centrality of a node u is the reciprocal of the average shortest path distance to u over all n-1 reachable nodes.  
    ### closeness_centrality(G, u=None, distance=None, wf_improved=True)
    # print(nx.closeness_centrality(gr, 1, None, True))

    ### Compute the shortest-path betweenness centrality for nodes.  
    ### betweenness_centrality(G, k=None, normalized=True, weight=None, endpoints=False, seed=None)
    # print(nx.betweenness_centrality(gr, k=1, normalized=True))

    ### degree_prestige, undirected
    # n_nodes = len(gr)
    # degree_prestige = dict((v, len(gr.edges(v))/(n_nodes-1)) for v in list(gr.nodes()))
    # print(degree_prestige)

    #----------------------------------------
    # print(iust.getHttpRequestHeader(requests.get("https://www.w3schools.com/html/default.asp")))
    # print('\n')

    # domain = iust.getDomainName("http://www.iust.ac.ir/content/58599/")
    # print(domain)
    # print('\n')

    # protocol = iust.getProtocol("http://www.iust.ac.ir/content/58599/")
    # print(protocol)
    # print('\n')

    # path = iust.getURLResource("http://www.iust.ac.ir/content/58599/")
    # print(path)
    # print('\n')

    # path = iust.getURLResource("http://www.iust.ac.ir/index.php?site=cultural_mng")
    # print(path)
    # print('\n')

    # ip = iust.getHostIp("http://www.iust.ac.ir/index.php?site=cultural_mng")
    # print(ip)
    # print('\n')

    # print(iust.UrlHasBookmark("http://www.iust.ac.ir/content/58599/"))
    # print(iust.UrlHasBookmark("http://www.iust.ac.ir/content/58599/#page-bookmark"))
    # print('\n')
#------------------------------------------------------------#


######################################################################################################################
# references
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://requests.readthedocs.io/en/master/
# https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76
# https://networkx.github.io/documentation/stable/reference/algorithms/centrality.html
######################################################################################################################
