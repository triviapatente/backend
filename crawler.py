# -*- coding: utf-8 -*-

# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'

from crawler.crawl_patentati import crawl_routines
from crawler.crawl_utils import utils

### Extraction ###
# Categories and relative links extraction
categories_links, cats =  crawl_routines.crawlPage(seed, 'div', 'content')

## TODO usare serialize ##

categories, quizzes, images = [], [], []

from app.game.models import Quiz, Image, Category

id_cat, id_quest, id_group, max_img = 0, 0, 0, -1

for cat in cats:

    categories.append(Category(name = cat))

    #groups_links = utils.getLinks(utils.getAllAnchors(utils.getContainer('http://m.patentati.it' + categories_links[id_cat], 'div', 'content')))

    # i = 0
    # for group in groups:
    #     ### Nel frattempo creiamo la tabella gruppi con una notazione JSON ###
    #     table_groups += '{\n\tid:%s\n' %id_group
    #     table_groups += '\tname:%s\n' %group
    #     table_groups += '\tid_cat:%s\n}\n' %id_cat
    #
    #     ### Estrazione tabelle delle domande di ogni gruppo ###
    #     questions_rows = get_questions('http://m.patentati.it' + groups_links[i], 'quests')
    #
    #     ### Fase 4 ###
    #     ### Estrazione delle domande ###
    #     for row in questions_rows:
    #         ### Database domande con notazione JSON ###
    #         image, question, answer = parse_question_row(row)
    #         table_quests += '{\n\tid:%s\n' %id_quest
    #         table_quests += '\tquestion:%s\n' %question
    #         table_quests += '\tanswer:%s\n' %answer
    #         table_quests += '\tid_group:%s\n' %id_group
    #         table_quests += '\tid_cat:%s\n' %id_cat
    #         table_quests += '\tid_img:%s\n}\n' %image
    #         if image and int(image) > int(max_img):
    #             max_img = image
    #         id_quest = id_quest + 1
    #
    #     id_group = id_group + 1
    #     i = i + 1
    id_cat = id_cat + 1

# Get all images
# for id_img in range(1, int(max_img)):
#     url = 'http://m.patentati.it/img_sign2011/' + str(id_img) + '.jpg'
#     path = 'quiz/images/' + str(id_img) + '.jpg'
#     if crawl_routines.getImage(url, path):
#         images.append(Image(image = path))


# Printo i risultati
from flask import jsonify
print jsonify(Categories = [i.json for i in categories])
#print jsonify(Quizzes = [i.json for i in quizzes])
#print jsonify(Images = [i.json for i in images])
