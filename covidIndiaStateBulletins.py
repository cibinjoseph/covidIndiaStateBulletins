"""
A module to parse health department websites of Indian states and obtain up to
date bulletins on the COVID-19 pandemic
Each state has a getState() method which outputs a list of the form:
    [bulletinDate, bulletinLink, lastUpdated]
    bulletinDate -> date when bulletin was released
    bulletinLink -> link to bulletin
    lastUpdated -> date when last updated, None if not updated
"""

import urllib3
from bs4 import BeautifulSoup
import sys
import os
import datetime
import filecmp
from pathlib import Path

resourcesDir = 'resources/'
oldDate = datetime.date(2019, 1, 1)  # A very old date for initializations

def init():
    """
    Performs a few sanity checks and initializations
    """
    if sys.version_info.major < 3:
        raise SyntaxError('Use python version 3+')

    try:
        os.mkdir(resourcesDir)
    except FileExistsError:
        pass

def __downloadPDF(link, filename):
    """
    Downloads pdf from link and saves it with filename
    """
    try:
        req = urllib3.PoolManager()
        response = req.request('GET', link)
        pdfFile = open(filename, 'wb')
        pdfFile.write(response.data)
    except HTTPError:
        print('Error: PDF file not found')
        return False
    finally:
        pdfFile.close()

def __isSamePDF(serverFile, localFile):
    """
    Checks if pdf file on server is same as local file and overwrites if not.
    """
    if Path(localFile).is_file():
        # If local file exists
        __downloadPDF(serverFile, localFile + 'dummy')
        if filecmp.cmp(localFile, localFile + 'dummy', shallow=False):
            os.remove(localFile + 'dummy')
            isSame = True
        else:
            os.replace(localFile + 'dummy', localFile)
            isSame = False
    else:
        # If local file does not exist
        __downloadPDF(serverFile, localFile)
        isSame = False

    return isSame

def getKerala():
    """
    Parses Kerala DHS website to obtain latest PDF bulletin
    """
    linkPre = 'http://dhs.kerala.gov.in'
    DHSlink = linkPre + '/%e0%b4%a1%e0%b5%86%e0%b4%af%e0%b4%bf%e0%b4%b2%e0%b4%bf-%e0%b4%ac%e0%b5%81%e0%b4%b3%e0%b5%8d%e0%b4%b3%e0%b4%b1%e0%b5%8d%e0%b4%b1%e0%b4%bf%e0%b4%a8%e0%b5%8d%e2%80%8d/'

    # Parse tags
    req = urllib3.PoolManager()
    DHSpage = req.request('GET', DHSlink)
    soup = BeautifulSoup(DHSpage.data, 'html.parser')
    tags = soup.findAll('h3', attrs={'class': 'entry-title'})

    # Get latest date
    bulletinDate = oldDate
    bulletinLink = None
    lastUpdated = None
    for tag in tags:
        dateText = tag.a.text
        date = datetime.date(int(dateText[6:10]),
                             int(dateText[3:5]),
                             int(dateText[0:2]))
        if date > bulletinDate:
            bulletinDate = date
            bulletinLink = linkPre + tag.a.get('href')
            # Parse bulletin page to get pdf link
            bulletinPage = req.request('GET', bulletinLink)
            soup = BeautifulSoup(bulletinPage.data, 'html.parser')
            try:
                divTag = soup.find('div', attrs={'class':'entry-content'})
                ptags = divTag.findAll('p')
            except AttributeError:
                raise ConnectionError('Broken internet connection. Rerun.')

            for tag in ptags:
                if 'English' in tag.text:
                    bulletinlink = linkPre + tag.a.get('href')

            filename = resourcesDir + 'Kerala' + bulletinDate.strftime('%d-%m-%Y') + '.pdf'
            if __isSamePDF(bulletinLink, filename):
                lastUpdated = None
            else :
                lastUpdated = datetime.datetime.now()

    return [bulletinDate, bulletinLink, lastUpdated]

if __name__ == '__main__':
    init()
    getKerala()
