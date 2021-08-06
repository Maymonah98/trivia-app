import os
from flask import Flask, json, request, abort, jsonify
from flask.globals import current_app
from flask.helpers import total_seconds
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS , cross_origin
import random

from sqlalchemy.sql.elements import Null

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions=[question.format() for question in selection]
  current_questions= questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  CORS(app, resources={r"/api/*" : {'origins': '*'}})
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  @app.route('/categories')
  def get_categories():
    categories= Category.query.all()
    formatted_categories={}
    for category in categories:
      formatted_categories[category.id]=category.type

    if len(categories)==0:
      abort(404)

    return jsonify({
        'success':True,
        'categories': formatted_categories,
      })

  
  @app.route('/questions')
  def get_questions():
    categories= Category.query.order_by(Category.id).all()
    formatted_categories={}
    current_category=True
    for category1 in categories:
      formatted_categories[category1.id]=category1.type  

    selection=Question.query.order_by(Question.id).all()
    current_questions= paginate_questions(request,selection)

    if len(current_questions) ==0:
      abort(404)

    return jsonify({
      'success':True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories':formatted_categories,
      'current_category': current_category
    })

  
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    try:
      question=Question.query.filter(Question.id==question_id).one_or_none()

      if question is None:
        abort(404)
      
      question.delete()
      selection=Question.query.order_by(Question.id).all()
      current_questions= paginate_questions(request,selection)

      return jsonify({
        'success':True,
        'deleted': question_id,
        'questions':current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(400)
  

  @app.route('/questions',methods=['POST'])
  def create_question():
    body=request.get_json()
    new_question=body.get('question',None)
    new_ansewr=body.get('answer',None)
    new_category=body.get('category',None)
    new_difficulty=body.get('difficulty',None)
    search=body.get('searchTerm',None)

    try:
      if search:
        selection= Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        current_questions=paginate_questions(request,selection)

        return jsonify({
          'success':True,
          'questions':current_questions,
          'total_questions':len(selection.all()),
          'current_category':''
        })
      else:
        question=Question(question=new_question,answer=new_ansewr,category=new_category,difficulty=new_difficulty)
        question.insert()

        selection=Question.query.order_by(Question.id).all()
        current_questions=paginate_questions(request,selection)

        return jsonify({
          'success':True,
          'created':question.id,
          'questions':current_questions,
          'total_questions':len(selection)
        })

    except:
      abort(422)

  
  @app.route('/categories/<int:category_id>/questions')
  def  get_questions_based_on_category(category_id):
    selection=Question.query.filter(Question.category==category_id).all()
    current_questions=paginate_questions(request,selection)
    if len(current_questions)==0:
      abort(404)
      
    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(Question.query.all()),
      'current_category':category_id
    })
     
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def play_the_quiz():
    body=request.get_json()
    previous_question=body.get('previous_questions')
    quiz_category=body.get('quiz_category')
    print(quiz_category)
    if quiz_category['id']==0:
      questions=Question.query.filter(Question.id.notin_((previous_question))).all()
    else:
      questions=Question.query.filter(Question.category==quiz_category['id']).filter(Question.id.notin_((previous_question))).all()
    
    current_question = random.choice(questions).format()
    if current_question['id'] in previous_question:
      previous_question.append(current_question['id']) 
    
    print(previous_question)
    if quiz_category is None :
      abort(400)
    return jsonify({
      'success': True,
      'question':current_question,
      'previous_questions':previous_question
    })
      
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error':404,
      'message': 'Not found'
    }),404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error':400,
      'message': 'Bad request'
    }),400

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error':422,
      'message': 'Unprocessable'
    }),422

  return app

    