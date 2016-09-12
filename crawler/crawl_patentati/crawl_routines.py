# -*- coding: utf-8 -*-

from crawler.crawl_utils import utils

# Given the url returns all the links in the page in the first container of the choosen class
def crawlPage(url, containerTag, containerClass):
    container = utils.getContainer(url, containerTag, containerClass)
    all_a, all_spans = utils.getAllAnchors(container), utils.getAllSpans(container)
    return utils.getLinks(all_a), utils.getTexts(all_spans)

# Given the url returns all the rows of the first table in the page of the choosen class
def getQuestions(url, class_of_table):
    parser = utils.getParser(url)
    table = parser.find('table', class_ = class_of_table).find('tbody').findAll('tr')
    return table

# Given a question_row returns the image id, the question and the answer
def parseQuestionRow(question_row):
    image, image_url = question_row.find('td', { 'class' : 'img' }), None
    if image:
        # url del tipo: /img_sign2011/550.jpg #
        try:
            image_url = image.find('a').find('img').get('src')[14:-4]
        except:
            None
    question = utils.clean(question_row.find('td', { 'class' : 'quest' }).text)
    answer = utils.clean(question_row.find('td', { 'class' : 'risp' }).text)
    return image_url, question, answer

def getImage(id_img, path):
    url = 'http://m.patentati.it/img_sign2011/' + str(id_img) + '.jpg'
    request = requests.get(url, stream = True)
    if request.status_code == 200:
        with open(path, 'wb') as to_img:
            shutil.copyfileobj(request.raw, to_img)
        return True
    return False
