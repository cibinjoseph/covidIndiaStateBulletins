"""
A module to parse health department websites of Indian states and obtain up to
date bulletins on the COVID-19 pandemic
Each state has a getState() method which outputs a list of the form:
    [bulletinDate, bulletinLink, lastUpdated]
    bulletinDate -> date when bulletin was released
    bulletinLink -> link to bulletin
    lastUpdated -> date when last updated, None if not updated
    All dates and times are in datetime module format
"""

import urllib3
import urllib.parse
from bs4 import BeautifulSoup
import sys
import os
import datetime
import filecmp
from pathlib import Path
from re import search, sub
from warnings import simplefilter

resourcesDir = 'resources/'
oldDate = datetime.date(2019, 1, 1)  # A very old date for initializations
__verbose = False
__statusNum = 0


def init(verbose=False):
    """
    Performs a few sanity checks and initializations
    """
    global __verbose
    __verbose = verbose

    # System version check
    if sys.version_info.major < 3:
        raise SyntaxError('Use python version 3+')

    # Create resources/ directory
    try:
        os.mkdir(resourcesDir)
    except FileExistsError:
        pass


def downloadPDF(link, filename):
    """
    Downloads pdf from link and saves it with filename
    """
    try:
        req = urllib3.PoolManager()
        response = req.request('GET', link)
        pdfFile = open(filename, 'wb')
        pdfFile.write(response.data)
        pdfFile.close()
    except urllib3.exceptions.MaxRetryError:
        # Catch SSL Certificate Error
        req = urllib3.PoolManager(cert_reqs='CERT_NONE')
        simplefilter('ignore')  # Ignore SSL certificate warning
        response = req.request('GET', link)
        pdfFile = open(filename, 'wb')
        pdfFile.write(response.data)
        pdfFile.close()
    except:
        raise ConnectionError('ERROR: pdf file not found. Check connection and rerun.')


def __isSamePDF(serverFile, localFile):
    """
    Checks if pdf file on server is same as local file and overwrites if not.
    """
    if Path(localFile).is_file():
        # If local file exists, compare files and 
        # overwrite if different
        downloadPDF(serverFile, localFile + 'dummy')
        if filecmp.cmp(localFile, localFile + 'dummy', shallow=False):
            os.remove(localFile + 'dummy')
            isSame = True
        else:
            os.replace(localFile + 'dummy', localFile)
            isSame = False
    else:
        # If local file does not exist
        downloadPDF(serverFile, localFile)
        isSame = False

    return isSame

def updatePDF(stateName, bulletinDate, bulletinLink):
    """
    Checks if server bulletin is updated. Overwrites local file if so.
    Returns current date and time for lastUpdatedDate if overwriting.
    Returns None if no updates are available.
    """
    filename = resourcesDir + stateName + \
        bulletinDate.strftime('-%d-%m-%Y') + '.pdf'
    if __isSamePDF(bulletinLink, filename):
        lastUpdated = None
    else:
        lastUpdated = datetime.datetime.now()

    return lastUpdated

def printStatus(stateName, statusNum=None, lastUpdated=None):
    """
    Prints status messages if __verbose is requested
    """
    if __verbose:
        global __statusNum
        if statusNum == 0:
            __statusNum = 0
        else:
            __statusNum = __statusNum + 1

        messages = {
            0: 'Parsing website for state: ' + stateName,
            1: 'Obtaining bulletin date for state: ' + stateName,
            2: 'Checking against local pdf bulletin for state: ' + stateName,
            3: 'Completed checking updates for state: ' + stateName
        }
        totalSteps = len(messages)

        print('(' + str(__statusNum) + '/' + str(totalSteps) + ') ' +  \
              messages.get(__statusNum, 'Invalid status number'))

        if lastUpdated != None:
            print('Updated bulletin available. Downloaded to resources/')

def getKerala():
    """
    Parses Kerala DHS website to obtain latest PDF bulletin
    """
    stateName = 'Kerala'
    linkPre = 'http://dhs.kerala.gov.in'
    healthDeptlink = linkPre + '/%e0%b4%a1%e0%b5%86%e0%b4%af%e0%b4%bf' + \
    '%e0%b4%b2%e0%b4%bf-%e0%b4%ac%e0%b5%81%e0%b4%b3%e0%b5%8d%e' + \
    '0%b4%b3%e0%b4%b1%e0%b5%8d%e0%b4%b1%e0%b4%bf%e0%b4%a8%e0%b5%8d%e2%80%8d/'

    # Parse tags
    printStatus(stateName, 0)
    req = urllib3.PoolManager()
    healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    tags = soup.findAll('h3', attrs={'class': 'entry-title'})

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
        dateText = tag.a.text
        thisDate = datetime.date(int(dateText[6:10]),
                             int(dateText[3:5]),
                             int(dateText[0:2]))
        if thisDate > bulletinDate:
            # If parsed date is recent than that parsed before,
            # save the date and bulletin links
            bulletinDate = thisDate
            bulletinPageLink = linkPre + tag.a.get('href')

            # Parse latest date's bulletin page to get pdf link
            bulletinPage = req.request('GET', bulletinPageLink)
            soup = BeautifulSoup(bulletinPage.data, 'html.parser')
            try:
                divTag = soup.find('div', attrs={'class': 'entry-content'})
                ptags = divTag.findAll('p')
            except AttributeError:
                raise ConnectionError('Broken internet connection. Rerun.')

            for tag in ptags:
                if 'English' in tag.text:
                    bulletinLink = linkPre + tag.a.get('href')

    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

def getDelhi():
    """
    Parses Delhi Govt website to obtain latest PDF bulletin
    """
    stateName = 'Delhi'
    linkPre = 'http://health.delhigovt.nic.in'
    healthDeptlink = linkPre + '/wps/wcm/connect/doit_health/' + \
    'Health/Home/Covid19/Health+Bulletin'

    # Parse tags
    printStatus(stateName, 0)
    req = urllib3.PoolManager()
    healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    tdTag = soup.find('td', attrs={'class': 'standard'})
    tags = tdTag.find_all('li')

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
        # Use RegEx to get date string
        dateText = search('Dated.(.*)', tag.a.text.title()).group(0)
        dateText = dateText[6:].replace('.',' ').strip()
        try:
            # Month in words
            thisDate = datetime.datetime.strptime(dateText, '%d %B %Y')
        except ValueError:
            # Month as integer
            thisDate = datetime.datetime.strptime(dateText, '%d %m %Y')
        # Convert datetime to date class
        thisDate = thisDate.date()
        if thisDate > bulletinDate:
            # If parsed date is recent than that parsed before,
            # save the date and bulletin links
            bulletinDate = thisDate
            bulletinLink = linkPre + tag.a.get('href')

    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

def getTelangana():
    """
    Parses Telangana Govt website to obtain latest PDF bulletin
    """
    stateName = 'Telangana'
    linkPre = 'https://covid19.telangana.gov.in'
    healthDeptlink = linkPre + '/announcements/media-bulletins/'

    # Parse tags
    printStatus(stateName, 0)
    req = urllib3.PoolManager(timeout=4.0)
    healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    tdTag = soup.find('div', attrs={'class': 'ast-row'})
    tags = tdTag.find_all('h2', attrs={'class': 'entry-title'})

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
        # Use RegEx to get date string
        dateText = search('Bulletin.(.*)', tag.a.text.title()).group(0)
        dateText = dateText[11:].encode('ascii','ignore').decode('utf-8')
        dateText = dateText.replace(',', ' ').strip().split()[-3:]
        dateText = sub(r'\D', '',  dateText[0]) + ' ' + \
                dateText[1] + ' ' + dateText[2]
        try:
            # Month in words
            thisDate = datetime.datetime.strptime(dateText, '%d %B %Y')
        except ValueError:
            # Month as integer
            thisDate = datetime.datetime.strptime(dateText, '%d %m %Y')
        # Convert datetime to date class
        thisDate = thisDate.date()
        if thisDate > bulletinDate:
            # If parsed date is recent than that parsed before,
            # save the date and bulletin links
            bulletinDate = thisDate
            bulletinLink = tag.a.get('href')

    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

def getAndhraPradesh():
    """
    Parses Andhra Pradesh Govt website to obtain latest PDF bulletin
    """
    stateName = 'AndhraPradesh'
    linkPre = 'http://hmfw.ap.gov.in'
    healthDeptlink = linkPre + '/covid_19_dailybulletins.aspx'

    # Parse tags
    printStatus(stateName, 0)
    req = urllib3.PoolManager()
    healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    divTags = soup.findAll('div', attrs={'class': 'col-md-2'})

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for divTag in divTags:
        tag = divTag.find('h5')
        dateText = tag.a.text
        thisDate = datetime.datetime.strptime(dateText, '%d-%m-%Y')
        thisDate = thisDate.date()
        if thisDate > bulletinDate:
            # If parsed date is recent than that parsed before,
            # save the date and bulletin links
            bulletinDate = thisDate
            bulletinPageLink = tag.a.get('href')
            bulletinPageLink = linkPre + '/' + bulletinPageLink

    # Get bulletin link from bulletin page
    bulletinPage = req.request('GET', bulletinPageLink)
    soup = BeautifulSoup(bulletinPage.data, 'html.parser')
    aTags = soup.findAll('a', href=True)
    for tag in aTags:
        thisLink = tag.get('href')
        print('HELLOOO ' + thisLink.upper())
        if 'ENGLISH' in thisLink.upper():
            bulletinLink = linkPre + thisLink
            break
        elif 'TELUGU' in thisLink.upper():
            bulletinLink = linkPre + thisLink
            break


    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

def getTamilNadu():
    """
    Parses Tamil Nadu Govt website to obtain latest PDF bulletin
    """
    stateName = 'TamilNadu'
    linkPre = 'http://stopcoronatn.in'
    healthDeptlink = linkPre + '/dailybulletin.html'

    # Parse tags
    printStatus(stateName, 0)
    try:
        req = urllib3.PoolManager()
        healthDeptpage = req.request('GET', healthDeptlink)
    except urllib3.exceptions.MaxRetryError:
        req = urllib3.PoolManager(cert_reqs='CERT_NONE')
        simplefilter('ignore')  # Ignore SSL certificate warning
        healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    divTag = soup.find('div', attrs={'class': 'information'})
    tags = divTag.findAll('li')

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
        dateText = tag.a.text.strip().replace(',','')
        dateText = dateText[9:20] + '20'
        thisDate = datetime.datetime.strptime(dateText, '%d-%B-%Y')
        thisDate = thisDate.date()
        if thisDate > bulletinDate:
            # If parsed date is recent than that parsed before,
            # save the date and bulletin links
            bulletinDate = thisDate
            bulletinLink = linkPre + tag.a.get('href')

    print(bulletinLink)
    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

def getKarnataka():
    """
    Parses Karnataka Govt website to obtain latest PDF bulletin
    """
    stateName = 'Karnataka'
    linkPre = 'https://karunadu.karnataka.gov.in'
    healthDeptlink = linkPre + '/hfw/kannada/Pages/covid-19.aspx'

    # Parse tags
    printStatus(stateName, 0)
    try:
        req = urllib3.PoolManager()
        healthDeptpage = req.request('GET', healthDeptlink)
    except urllib3.exceptions.MaxRetryError:
        req = urllib3.PoolManager(cert_reqs='CERT_NONE')
        simplefilter('ignore')  # Ignore SSL certificate warning
        healthDeptpage = req.request('GET', healthDeptlink)
    soup = BeautifulSoup(healthDeptpage.data, 'html.parser')
    divTags = soup.findAll('div', attrs={'id': 'zone8block'})[0]
    for divTag in divTags:
        if divTag.string is None:
            if 'BULLETIN)' in divTag.text.upper():
                tags = divTag.find_all('a')

    # Get latest date
    printStatus(stateName)
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
            thisLink = tag.get('href')
            if 'ENGLISH' in thisLink.upper():
                thisDate = tag.get('href')[22:-13]
                try:
                    thisDate = datetime.datetime.strptime(thisDate, '%d-%m-%Y')
                except ValueError:
                    # Correct error in month format
                    thisDate = thisDate.replace('-30-', '-03-')
                    thisDate = datetime.datetime.strptime(thisDate, '%d-%m-%Y')

                thisDate = thisDate.date()

                if thisDate > bulletinDate:
                    # If parsed date is recent than that parsed before,
                    # save the date and bulletin links
                    bulletinDate = thisDate
                    bulletinLink = linkPre + tag.get('href')

    # Check if latest bulletin on server is same as local file
    printStatus(stateName)
    lastUpdated = updatePDF(stateName, bulletinDate, bulletinLink)

    printStatus(stateName, lastUpdated=lastUpdated)
    return [bulletinDate, bulletinLink, lastUpdated]

if __name__ == '__main__':
    init()  # Use init(verbose=True) to print out explicit status messages
    try:
        print(getKerala())
        print(getDelhi())
        print(getAndhraPradesh())
        print(getTamilNadu())
        # print(getKarnataka())
        print(getTelangana())
    except urllib3.exceptions.MaxRetryError:
        raise ConnectionError('NO INTERNET OR UNAVAILABLE')
