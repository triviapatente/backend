# -*- coding: utf-8 -*-

from crawler.utils import utils

# Given the ##url returns a map names - links in the first container of the choosen class(##containerClass) and tag(##containerTag)
def crawlPage(url, containerTag, containerId):
    container = utils.getContainer(url, containerTag, containerId)
    all_a = utils.getAllAnchors(container)
    return dict(zip(utils.getTexts(all_a), utils.getLinks(all_a)))

# Given the ##url returns all the rows of the first table in the page of the choosen ##class_of_table
def getQuestions(url, class_of_table):
    try:
        parser = utils.getParser(url)
        table = parser.find('table', class_ = class_of_table).find('tbody').findAll('tr')
        return table
    except:
        return []
# Given a ##question_row returns the image id, the question and the answer
def parseQuestionRow(question_row):
    image, image_url = question_row.find('td', { 'class' : 'img' }), None
    if image:
        try:
            image_url = image.find('img').get('src')
        except:
            None
    question_text = question_row.find('td', { 'class' : 'domanda' }).text
    question = utils.clean(question_text)
    answer = bool(utils.clean(question_row.find('td', { 'class' : 'risp' }).text) == 'V')
    return image_url, question, answer
