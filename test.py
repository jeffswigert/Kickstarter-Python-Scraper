
import urllib2
import bs4
import datetime
import string
import re
import csv

search = 'cards'
headers = ['URL','Title','Category','Goal','Funding Amount','Backers','# of Rewards','Reward Price','# Claimed']
BASE_URL = "https://www.kickstarter.com"
first_url = 'https://www.kickstarter.com/projects/search?term=' + search
subcat = 'https://www.kickstarter.com/discover/categories/34'

search_results = [first_url]
to_crawl = ['https://www.kickstarter.com/projects/1868828187/grizzly-bear-card-clips-protection-for-your-playin','https://www.kickstarter.com/projects/chriscavill/the-type-deck-typography-playing-cards-printed-by']
crawled = []

#======================
# addSearchResults
#======================
def addUrl(url,lists):
    if url not in search_results and url not in to_crawl and url not in crawled:
        lists.append(url)

def soupify(url):
    doc = urllib2.urlopen(url)
    return bs4.BeautifulSoup(doc)

def addSearchPages(url):
    '''
    Takes in a URL. 
    Generates list of pages that needs to be crawled based on last page number.
    Returns nothing
    '''
    soup = soupify(url)
    lastPage = soup.find('div',{'class':'pagination'}).find_all('a')[-2].string
    for i in range(2,int(lastPage) + 1):
        newUrl = BASE_URL + "/projects/search?page=" + str(i) + "&term=cards"
        addUrl(newUrl,search_results)

def addProjectPages(url):
    '''
    Takes in one URL from search_results from the list
    Appends project page URLs to to_crawl
    Returns nothing
    '''
    soup = soupify(url)
    for projects in soup.find_all('h2',{'class':'bbcard_name'}):
        for link in projects.find_all('a'):
            newUrl = BASE_URL + link.get('href')[0:-11]
            addUrl(newUrl, to_crawl)

def extractData(url):
    '''
    Takes in URL
    Returns title, goal, funding status, total backers, # or rewards, reward #, # of backers
    '''
    soup = soupify(url)
    title = str(soup.head.title.string[0:-14])
    category = str(soup.find('li',{'class':'category'}).find('a').contents[1][1:-1])
    goal = soup.find_all('meta')[20]['content'].split(' ')[2]
    goal = int(re.sub('[^0-9]', '', goal))
    funded = soup.find(id='pledged').find('data').contents[0]
    funded = int(re.sub('[^0-9]', '', funded))
    backers = int(soup.find(id='backers_count').find('data').contents[0])
    rewards = soup.find(id='what-you-get').find_all('li')
    reward_price = []
    reward_back = []
    for reward in rewards:
        reward_price.append(int(re.sub('[^0-9]', '', reward.h5.span.string)))
        reward_back.append(int(reward.find('span',{'class':'num-backers'}).string[1:].split(' ')[0]))
    return title, category, goal, funded, backers, len(rewards), reward_price, reward_back

def writeCSV(crawl_list,time):
    newF = open(search+'_'+str(time)+'.csv', 'wb')
    writer = csv.writer(newF, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    while len(crawl_list) > 0:
        project = crawl_list.pop()
        t, c, g, f, b, r, rp, rb = extractData(project)
        row = [t, c, g, f, b, r]
        for i in range(len(rp)):
            row.append(rp[i])
            row.append(rb[i])
        writer.writerow(row)
        crawled.append(project)
    newF.close()
    return
    
time = datetime.datetime.now()
writeCSV(to_crawl,time)


#def startCrawl():
#    errors = 0
#    startTime = datetime.datetime.now()
#
#    addSearchPages(search_results[0])
#
#    while len(search_results) > 0:
#        current = search_results.pop()
#        print(current)
#        try:
#            addProjectPages(current)
#        except Exception as e:
#            errors += 1
#            print(e)
#            continue
#        crawled.append(current)
#
#    print('Number of crawled pages: ' + str(len(crawled)))
#    print('Number of errors: ' + str(errors))
#    print('Elapsed time: ' + str(datetime.datetime.now() - startTime))