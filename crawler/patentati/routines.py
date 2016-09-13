# -*- coding: utf-8 -*-

import requests, shutil
from crawler.utils import utils

# Given the url returns a map names - links in the first container of the choosen class and tag
def crawlPage(url, containerTag, containerClass):
    container = utils.getContainer(url, containerTag, containerClass)
    all_a, all_spans = utils.getAllAnchors(container), utils.getAllSpans(container)
    return dict(zip(utils.getTexts(all_spans), utils.getLinks(all_a)))

# Given the url returns all the rows of the first table in the page of the choosen class
def getQuestions(url, class_of_table):
    parser = utils.getParser(url)
    table = parser.find('table', class_ = class_of_table).find('tbody').findAll('tr')
    return table

# Given a question_row returns the image id, the question and the answer
def parseQuestionRow(question_row):
    image, image_url = question_row.find('td', { 'class' : 'img' }), None
    if image:
        try:
            image_url = image.find('a').find('img').get('src')
        except:
            None
    question = utils.clean(question_row.find('td', { 'class' : 'quest' }).text)
    answer = bool(utils.clean(question_row.find('td', { 'class' : 'risp' }).text) == 'V')
    return image_url, question, answer

# Given an image id and a path save the img in the choosen path if it doesn't already exist
def getImage(url, path):
    request = requests.get(url, stream = True)
    if request.status_code == 200:
        with open(path, 'wb') as to_img:
            shutil.copyfileobj(request.raw, to_img)
        return True
    return False
