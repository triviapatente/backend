# -*- coding: utf-8 -*-
from patentati import routines
from utils import utils

from app.game.models import Quiz, Image, Category

# get Categories and puts them into ##session, no commit, ##path where to save images
# ##seed is the url of the seeding page, ##session is the ORM connected to the db
def getCategories(session, seed, path):
    # Categories and relative links extraction
    categories =  routines.crawlPage(seed, 'div', 'content')
    # For each pair category - link
    for name, link in categories.items():
        # Create record
        category = Category(name = name)
        print 'Saving category: ' + name + '..'
        session.add(category)
        session.commit()
        print 'Crawling the above category..'
        getGroups(session, link, int(category.id), path)
        print 'Saved all the quizzes of the category'

# get Groups from ##link of the category to continue the crawler and go to extract the quizzes
# ##session is the ORM connected to the db, ##category_id is the id of the category, ##path where to save images
def getGroups(session, link, category_id, path):
    groupsLinks = utils.getLinks(utils.getAllAnchors(utils.getContainer('http://m.patentati.it' + link, 'div', 'content')))
    for link in groupsLinks:
        # Get question rows
        questionsRows = routines.getQuestions('http://m.patentati.it' + link, 'quests')
        getQuestions(session, questionsRows, category_id, path)

# get Questions from ##questionsRows, which is the set of all the rows of the group table and put them into ##session
# ##session is the ORM connected to the db, ##category_id is the id of the category, ##path where to save images
def getQuestions(session, questionsRows, category_id, path):
    #Get out quizzes
    for row in questionsRows:
        image_url, question, answer = routines.parseQuestionRow(row)
        # Downloading image if not already done
        #print 'Downloading next image if necessary..'
        image_id = getImage(session, image_url, path)
        # Create quiz record
        question = Quiz(question = question, answer = answer, image_id = image_id, category_id = category_id)
        #print 'Saving next quiz..'
        session.add(question)

# get Image from ##image_url, if not already present in the database, and return the id. Returns none if some errors occured.
# ##session the ORM connected to the db, ##path where to save the image if necessary
def getImage(session, image_url, path):
    if not image_url:
        return None
    url = 'http://m.patentati.it/' + image_url
    c_path = path + image_url[14:]
    image = session.query(Image).filter(Image.image == path).first()
    if not image:
        if routines.getImage(url, c_path):
            # Create image record
            print 'Successful download, saving image..'
            image = Image(image = c_path)
            session.add(image)
            session.commit()
        else:
            #print 'Some error occured in image download..'
            return None
    else:
        print 'Image already present in the database..'
    return image.id
