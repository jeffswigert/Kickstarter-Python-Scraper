#-----------------------------------------------------------------------
#
#  KICKSTARTER.COM WEB SCRAPER
#
#-----------------------------------------------------------------------
#  
#  Written for Python 3.3
#
#-----------------------------------------------------------------------

import urllib3
import bs4
import csv
import re
import datetime
# import os

#======================
# Initialized variables
#======================

search = 'cards'

BASE_URL = 'https://www.kickstarter.com'
first_url = 'https://www.kickstarter.com/projects/search?page=1&term=' + search
subcat = 'https://www.kickstarter.com/discover/categories/34'
headers = ['URL','Title','Category','Start Date', 'End Date', 'Goal','Funding Amount','Backers','# of Rewards','Reward Price','# Claimed']

search_results = [first_url]
to_crawl = []
crawled = []

#======================
# addUrl
# Check if URL is in either list
# Add an individual URL to specified list
#======================
def addUrl(url,in_list):
    if url not in search_results and url not in to_crawl and url not in crawled:
        in_list.append(url)

#======================
# soupify
# Turns an html page into soup for further manipulation
#======================
def soupify(url):
    doc = urllib3.PoolManager().request('GET',url)
    return bs4.BeautifulSoup(doc.data)

#======================
# numify
# Remove letters and characters from string and turn into integer
#======================
def numify(in_str):
    string = in_str
    return int(string)

#======================
# addSearchPages
# Run this once first at the beginning of search
# Start with first URL and add all the other pages from the search result
#======================
def addSearchPages(url):
    '''
    Takes in a URL. 
    Generates list of pages that needs to be crawled based on last page number.
    Returns nothing
    '''
    soup = soupify(url)
    lastPage = soup.find('div',{'class':'pagination'}).find_all('a')[-2].string
    for i in range(2,int(lastPage) + 1):
        newUrl = BASE_URL + "/projects/search?page=" + str(i) + "&term=" + search
        addUrl(newUrl, search_results)

#======================
# addProjectPages
# Check if URL is in either list
# Add an individual URL
#======================
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

#======================
# extractData
# Identify key parts of each project
# Title, category, start date, end date, goal, funded or not, # of rewards, reward level, # of backers
#======================
def extractData(url):
    '''
    Takes in URL
    Returns title, category, goal, funding status, total backers, # or rewards, reward level, # of backers
    '''
    soup = soupify(url)
    title = soup.head.title.string[0:-14]
    title = str(re.sub(r'[^\x00-\x7f]', '', title))
    category = str(soup.find('li',{'class':'category'}).find('a').contents[1][1:-1])
    start = soup.find_all('time')[-2].string
    end = soup.find_all('time')[-1].string
    goal = float(soup.find(id='pledged')['data-goal'])
    funded = float(soup.find(id='pledged').find('data')['data-value'])
    backers = soup.find(id='backers_count').find('data').contents[0]
    backers = int(re.sub('[^0-9]', '', backers))
    rewards = soup.find(id='what-you-get').find_all('li')
    reward_price = []
    reward_back = []
    for reward in rewards:
        reward_price.append(int(re.sub('[^0-9]', '', reward.h5.span.string)))
        reward_back.append(int(reward.find('span',{'class':'num-backers'}).string[1:].split(' ')[0]))
    return title, category, start, end, goal, funded, backers, len(rewards), reward_price, reward_back

#======================
# writeCSV
# Create new CSV file including
# Write URL, and all info from extractData(url)
#======================
def writeCSV(crawl_list,time,errors):
    '''
    Takes in a list of URLs to crawl and the time to create unique filename
    Writes important data to CSV
    Returns nothing
    '''
    newT = re.sub('[^0-9]', '', str(time))
    newF = open(search+'_'+newT+'.csv', 'w', newline='')
    writer = csv.writer(newF, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    while len(crawl_list) > 0:
        project = crawl_list.pop()
        print(project)
        try:
            t, c, s,e, g, f, b, r, rp, rb = extractData(project)
            row = [project, t, c, s, e, g, f, b, r]
            for i in range(len(rp)):
                row.append(rp[i])
                row.append(rb[i])
            writer.writerow(row)
        except Exception as e:
            errors += 1
            row = [project, e]
            writer.writerow(row)
            print(e)
        crawled.append(project)
    newF.close()
    return

#======================
# startCrawl
# Start the crawl process
#======================
def startCrawl():
    errors = 0
    startTime = datetime.datetime.now()

    addSearchPages(search_results[0])

    while len(search_results) > 0:
        current = search_results.pop()
        print(current)
        try:
            addProjectPages(current)
        except Exception as e:
            errors += 1
            print(e)
            continue
        crawled.append(current)
    projects = len(to_crawl)

    writeCSV(to_crawl,startTime,errors)

    # try:
    #     writeCSV(to_crawl,startTime)
    # except Exception as e:
    #     errors += 1
    #     print(e)

    print('Number of crawled pages: ' + str(len(crawled)))
    print('Number of projects: ' + str(projects))
    print('Number of errors: ' + str(errors))
    print('Elapsed time: ' + str(datetime.datetime.now() - startTime))

startCrawl()

#-----------------------------------------------------------------------
#======================
# Testing
#======================
# to_crawl = ['https://www.kickstarter.com/projects/1761852825/the-aesir-deck-viking-gods-on-playing-cards',
# 'https://www.kickstarter.com/projects/1374838500/japanese-the-game-a-language-learning-card-game']

# print(extractData(to_crawl[0]))
# print(extractData(to_crawl[1]))

# extractData(to_crawl[0])
# extractData(to_crawl[1])

# time = datetime.datetime.now()
# writeCSV(to_crawl,time)