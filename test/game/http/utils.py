from tp.game.models import Quiz, Training, TrainingAnswer
from tp import app, db

def dumb_training(user_id, numberOfErrors):
    limit = app.config["NUMBER_OF_QUESTIONS_FOR_TRAINING"]
    quizzes = Quiz.query.limit(limit)
    training = Training(user_id = user_id)
    db.session.add(training)
    db.session.commit()
    i = 0
    for quiz in quizzes:
        answer = quiz.answer
        if i < numberOfErrors:
            answer = not answer
        a = TrainingAnswer(training_id = training.id, answer = answer, quiz_id = quiz.id, order_index = i)
        db.session.add(a)
        i += 1
    db.session.commit()
    return training.id
