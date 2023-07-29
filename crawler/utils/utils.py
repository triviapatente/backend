# -*- coding: utf-8 -*-

from urllib.request import urlopen
import re, requests, shutil
from bs4 import BeautifulSoup

### Contains all the general crawl utils ###

# Given an ##url returns the html document
def getHtml(url):
    return urlopen(url).read()

# Get container given the tag (##containerTag) and the class (##containerClass)
def getContainer(url, containerTag, containerClass):
    return getParser(url).find(containerTag, class_ = containerClass)

# Clean sentence (##str)
def clean(str):
    return re.sub('[\n\t\r]', '', str).strip()

# Get all anchors in a given ##container
def getAllAnchors(container):
    return container.findAll('a')

# Get all spans in a given ##container
def getAllSpans(container):
    return container.findAll('span')

# Extract links from ##anchors
def getLinks(anchors):
    links = []
    for a in anchors:
        link = a.get('href')
        if link:
            links.append(link)
    return links

# Extract texts from ##spans
def getTexts(spans):
    texts = []
    for t in spans:
        text = t.text
        if text:
            texts.append(clean(text))
    return texts

# get an html parser for the given ##url
def getParser(url):
    return BeautifulSoup(getHtml(url), "html.parser")


# Given an image ##url a path save the img in the choosen ##imgPath
def getImage(url, imgPath):
    request = requests.get(url, stream = True)
    if request.status_code == 200:
        with open(imgPath, 'wb') as to_img:
            shutil.copyfileobj(request.raw, to_img)
        return True
    return False
