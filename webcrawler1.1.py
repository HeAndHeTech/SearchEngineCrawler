import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama


colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

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
        file1.write(href+"\n")
        file1.close()
        internal_urls.add(href)
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
            print('total_urls_visited',total_urls_visited)
            break
        crawl(link, max_urls=max_urls)

if __name__ == "__main__":
    # Using readlines()
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
        crawl(url,1000)
        print("[+] Total Internal links:", len(internal_urls))
        print("[+] Total External links:", len(external_urls))
        print("[+] Total URLs:", len(external_urls) + len(internal_urls))
