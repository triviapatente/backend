# -*- coding: utf-8 -*-

import urllib2, re, requests, shutil
from bs4 import BeautifulSoup

### Contains all the general crawl utils ###

# Given an url returns the html document
def getHtml(url):
    return urllib2.urlopen(url).read()

# Get container
def getContainer(url, containerTag, containerClass):
    return getParser(url).find(containerTag, class_ = containerClass)

# Clean sentence
def clean(str):
    return re.sub('[\n\t\r]', '', str)

# Get all anchors in a given div
def getAllAnchors(container):
    return container.findAll('a')

# Get all spans in a given div
def getAllSpans(container):
    return container.findAll('span')

# Extract links from anchors
def getLinks(anchors):
    links = []
    for a in anchors:
        link = a.get('href')
        if link:
            links.append(link)
    return links

# Extract texts from spans
def getTexts(spans):
    texts = []
    for t in spans:
        text = t.text
        if text:
            texts.append(clean(text))
    return texts

def getParser(url):
    return BeautifulSoup(getHtml(url), 'html.parser')
