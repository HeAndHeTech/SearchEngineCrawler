import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import pymongo

colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW


def connect_to_db():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["coin-search"]
    global db_object
    db_object = mydb["websiteContent"]
    #print(mydb,mycol)


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_child_text(soup,url):
    td = ""
    p = ""
    if "geeksforgeeks" in url:
        # Find all the td elements on the page
        td = soup.find_all('article')

    if "w3schools" in url:
        # Find all the td elements on the page
        td = soup.find_all(('div', {'id': 'main'}))

    if "tutorialspoint" in url:
        # Find all the td elements on the page
        td = soup.find_all(('div', {'class': 'mui-col-md-6 tutorial-content'}))

    for i in td:
        for para in i.find_all('p'):
            p = p + para.text + ","
    #if "\xa0 " in p:
        #p = p.replace(u'\xa0', u'')
    p = unicodedata.normalize("NFKD", p)
    return p

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")
        urls.add(href)
        # Append-adds at last
        file1 = open("C://Users//DELL//PycharmProjects//searchwebcrawler//url.txt", "a")  # append mode
        file1.write(href + "\n")
        file1.close()
        internal_urls.add(href)

    mydict = {}
    title = ""
    p = ""
    headings = []
    links = soup.find_all("title")
    for link in links:
        #print(link.text.strip())
        title = title + link.text.strip()
    p = get_child_text(soup,url)

    #links = soup.find_all("p")
    #for link in links:
        #print(link.text.strip())
        #p = p + link.text.strip() + ","
    heading = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for link in heading:
        print(link.text.strip())
        headings.append(link.text.strip())

    headings = list(set(headings))
    if "" in headings:
        headings.remove('')

    mydict['url'] = url
    mydict['title'] = title
    mydict['content'] = p
    mydict['headings'] = headings
    print(mydict)
    print(db_object)
    x = db_object.insert_one(mydict)

    return urls


def crawl(url, max_urls):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            print('total_urls_visited', total_urls_visited)
            break
        crawl(link, max_urls=max_urls)


if __name__ == "__main__":
    # Using readlines()
    connect_to_db()
    file1 = open('C://Users//DELL//PycharmProjects//searchwebcrawler//url-to-crawls.txt', 'r')
    Lines = file1.readlines()
    # Strips the newline character
    for line in Lines:
        # number of urls visited so far will be stored here
        total_urls_visited = 0
        # initialize the set of links (unique links)
        internal_urls = set()
        external_urls = set()
        url = line.strip('\n')
        crawl(url, 10)
        print("[+] Total Internal links:", len(internal_urls))
        print("[+] Total External links:", len(external_urls))
        print("[+] Total URLs:", len(external_urls) + len(internal_urls))
