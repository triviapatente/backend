# -*- coding: utf-8 -*-
# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'

from crawler.crawl_patentati import crawl_routines
from crawler.crawl_utils import utils

### Extraction ###
# Categories and relative links extraction
categories_links, cats =  crawl_routines.crawlPage(seed, 'div', 'content')

from app.game.models import Quiz, Image, Category
categories, quizzes, images = [], [], []

id_cat, id_group, maxImg = 0, 0, -1

for cat in cats:
    # Create category record
    categories.append(Category(name = cat))
    groupsLinks = utils.getLinks(utils.getAllAnchors(utils.getContainer('http://m.patentati.it' + categories_links[id_cat], 'div', 'content')))
    for link in groupsLinks:
        # Get question rows
        questionsRows = crawl_routines.getQuestions('http://m.patentati.it' + link, 'quests')
        #Get out quizzes
        for row in questionsRows:
            image, question, answer = crawl_routines.parseQuestionRow(row)
            if image and image > maxImg:
                maxImg = image
            # Create quiz record
            quizzes.append(Quiz(question = question, answer = answer, image_id = image, category_id = id_cat))
        id_group = id_group + 1

    id_cat = id_cat + 1

Get all images
for id_img in range(1, int(maxImg)):
    url = 'http://m.patentati.it/img_sign2011/' + str(id_img) + '.jpg'
    path = 'quiz/images/' + str(id_img) + '.jpg' #da vedere che path mettere
    continue #togliere questa riga quando scelto il path
    if crawl_routines.getImage(url, path):
        # Create image record
        images.append(Image(image = path))


### Saving Data ###
print str([i.json for i in categories])
print str([i.json for i in quizzes])
print str([i.json for i in images])
