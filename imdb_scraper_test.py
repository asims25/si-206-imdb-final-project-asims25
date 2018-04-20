import unittest
from movie_scraper import *
import json
import requests

class TestData(unittest.TestCase):
    def testDictionary(self):
        m1='Saving Private Ryan'
        m2='Alien'
        m3='Blade Runner'
        m4='Get Out'

        self.assertEqual(final_movie_dict[m1]['ReleaseYear'], '1998')
        self.assertEqual(final_movie_dict[m1]['Rating'], 'R')
        self.assertEqual(final_movie_dict[m2]['Director'], 'Ridley Scott')
        self.assertEqual(final_movie_dict[m2]['Star'], 'Sigourney Weaver')
        self.assertEqual(final_movie_dict[m3]['Genre'], 'Sci-Fi, Thriller')
        self.assertEqual(final_movie_dict[m3]['Runtime'], '117 min')
        self.assertEqual(final_movie_dict[m4]['OscarNominations'], '7')
        self.assertEqual(final_movie_dict[m4]['OscarsWon'], '3')
        self.assertEqual(final_movie_dict[m4]['BoxOffice'], '$176.04M')
        self.assertEqual(final_movie_dict[m4]['Metascore'], '84')
        self.assertEqual(final_movie_dict[m4]['UserReview'], '7.7')
class TestDatabase(unittest.TestCase):
    def testMovieInformationTable(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT MovieName FROM Movie_Information'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Men in Black',), result_list)
        self.assertEqual(len(result_list), 1100)

        sql = '''
            SELECT MovieName, ReleaseYear, LeadActor
            FROM Movie_Information
            WHERE Genre="Action, Adventure, Sci-Fi"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 16)
        self.assertEqual(result_list[1][2], 'Bruce Willis')

        conn.close()
    def testMovieReviewsTable(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT BoxOfficeMoney FROM Movie_Reviews
            WHERE CriticImdbScore>80 AND BoxOfficeMoney!="Not released"
            '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((148.48,), result_list)
        self.assertEqual(len(result_list), 351)

        sql = '''
            SELECT UserImdbScore, CriticImdbScore
            FROM Movie_Reviews
            JOIN Movie_Information
            ON Movie_Reviews.Id=Movie_Information.ID
            WHERE ReleaseYear='2017'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 95)
        self.assertEqual(result_list[57][1], 63.0)

        conn.close()
# class TestInteractive(unittest.TestCase):
#     def testGraphQuery1(self):
#         user_input='graph reviews 2017'
#         self.assertEqual(len(user_list), 20)
#         self.assertIn('Coco', movie_list)
#     def testGraphQuery2(self):
#         user_input='graph boxoffice 2017'
#         self.assertEqual(len(box_office), 20)
#         self.assertIn('It',movie_list)
#     def testGraphQuery3(self):
#         user_input='graph genre 2017'
#         self.assertEqual(len(action_counter), 44)
#     def testGraphQuery4(self):
#         user_input='graph oscars'
#         self.assertEqual(len(oscarswon_list), 20)
#         self.assertIn('Saving Private Ryan', movie_list)
unittest.main(verbosity=0)
