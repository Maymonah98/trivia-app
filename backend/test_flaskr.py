import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question={
            'question':'what is the mix that produce green color?',
            'answer':'yellow and blue',
            'difficulty':1,
            'category':1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data= json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))

    def test_404_category_does_not_exist(self):
        res=self.client().get('/categories/800')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not found')
    
    def test_get_paginated_questions(self):
        res=self.client().get('/questions')
        data= json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000',json={'difficulty':2})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not found')  


    def test_delete_question(self):
        res=self.client().delete('/questions/4')
        data=json.loads(res.data)

        question= Question.query.filter(Question.id==4).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],4)
        self.assertTrue(data['total_questions'],)
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None)

    def test_400_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Bad request')

    def test_create_question(self):
        res=self.client().post('/questions',json=self.new_question)
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
      
    def test_404_if_question_creation_not_found(self):
        res = self.client().post('/questions/',json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

       

    def test_get_question_search_with_results(self):
        res =self.client().post('/questions',json={'searchTerm':'green'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_question_search_without_results(self):
        res =self.client().post('/questions',json={'searchTerm':'applejacks'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],0)
        self.assertEqual(len(data['questions']),0)

    def test_play_quiz(self):
        new_quiz = {'previous_questions':[],'quiz_category':{'type':'Art','id':'2'}}
        res = self.client().post('/quizzes',json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_play_quiz_fail(self):
        res = self.client().post('/quizzes',json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'Bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()