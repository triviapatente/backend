# -*- coding: utf-8 -*-
from crawler.patentati import routines
import crawler.utils.utils

from tp.game.models import Quiz, Image, Category
from crawler.shared import shared_map
baseUrl = ''

# get Categories and puts them into ##session, no commit, ##imgPath where to save images
# ##seed is the url of the seeding page, ##session is the ORM connected to the db
def getCategories(session, seed, bUrl, imgPath = '/images'):
    # check if imgPath == None
    if not imgPath:
        imgPath = ''
    # assign baseUrl
    global baseUrl
    baseUrl = bUrl
    # Categories and relative links extraction
    categories =  routines.crawlPage(seed, 'div', 'content')
    malformedQuestions = 0
    # For each pair category - link
    for name, link in categories.items():
        # Create record
        name = name.encode("utf-8")
        category = Category(name = name)
        infos = shared_map[name]
        category.id = infos["id"]
        category.hint = infos["hint"]
        category.color = infos["color"]
        print(f"Saving category: {category.hint}")
        session.add(category)
        session.commit()
        #print("Crawling the above category..")
        malformedQuestions += getGroups(session, link, int(category.id), imgPath)
        #print("Saved all the quizzes of the category")
    print(f"Overall malformed questions: {malformedQuestions}")


# get Groups from ##link of the category to continue the crawler and go to extract the quizzes
# ##session is the ORM connected to the db, ##category_id is the id of the category, ##imgPath where to save images
def getGroups(session, link, category_id, imgPath):
    malformedQuestions = 0
    groupsLinks = utils.getLinks(utils.getAllAnchors(utils.getContainer(baseUrl + link, 'div', 'content')))
    for link in groupsLinks:
        # Get question rows
        questionsRows = routines.getQuestions(baseUrl + link, 'quests')
        malformedQuestions += getQuestions(session, questionsRows, category_id, imgPath)
    print(f"Malformed questions: {malformedQuestions}")
    if malformedQuestions > 0:
        print("Warning: you have to correct them manually!")
    return malformedQuestions
# get Questions from ##questionsRows, which is the set of all the rows of the group table and put them into ##session
# ##session is the ORM connected to the db, ##category_id is the id of the category, ##imgPath where to save images
def getQuestions(session, questionsRows, category_id, imgPath):
    malformedQuestions = 0
    #Get out quizzes
    for row in questionsRows:
        image_url, question, answer = routines.parseQuestionRow(row)
        if question[:1].islower():
            malformedQuestions += 1
            print(f"Malformed question found: {question}")
        # Downloading image if not already done
        #print("Downloading next image if necessary..")
        image_id = getImage(session, image_url, imgPath)
        # Create quiz record
        question = Quiz(question = question, answer = answer, image_id = image_id, category_id = category_id)
        #print("Saving next quiz..")
        session.add(question)
    return malformedQuestions

# get Image from ##image_url, if not already present in the database, and return the id. Returns none if some errors occured.
# ##session the ORM connected to the db, ##imgPath where to save the image if necessary
def getImage(session, image_url, imgPath):
    if not image_url:
        return None
    url = baseUrl + image_url
    path = imgPath + image_url[14:]
    image = session.query(Image).filter(Image.image == path).first()
    if not image:
        if utils.getImage(url, path):
            # Create image record
            #print("Successful download, saving image..")
            image = Image(image = path)
            session.add(image)
            session.commit()
        else:
            #print("Some error occured in image download..")
            return None
    else:
        None
        #print("Image already present in the database..")
    return image.id
