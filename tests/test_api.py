import json
import unittest
import httpretty

import quizlet
from quizlet import QuizletAPI


class TestCase(unittest.TestCase):
    GET, POST, PUT, DELETE = httpretty.GET, httpretty.POST, httpretty.PUT, httpretty.DELETE

    def setUp(self):
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()

    @staticmethod
    def register_url(method, path, data=None, **kwargs):
        if data is not None:
            kwargs['body'] = json.dumps(data)
        httpretty.register_uri(method, quizlet.BASE_URL + path, **kwargs)

    @property
    def last_request(self):
        return httpretty.last_request()


class ApiTests(TestCase):
    def test_client_id_request(self):
        self.register_url(self.GET, 'wizards', {})
        QuizletAPI(client_id='gandalf').wizards.get()
        self.assertTrue(self.last_request.path.endswith('?client_id=gandalf'))

    def test_token_request(self):
        self.register_url(self.POST, 'hobbits', {})
        QuizletAPI(token='bingo').hobbits.post()
        self.assertIn('Authorization', self.last_request.headers)
        self.assertEquals(self.last_request.headers['Authorization'], 'Bearer bingo')

    def test_bad_request(self):
        msg = 'Aragorn is not an elf'
        self.register_url(self.POST, 'elfs', {'error': msg}, status=400)
        with self.assertRaises(quizlet.QuizletError) as e:
            QuizletAPI().elfs.post(data={'name': 'Aragorn'})
            self.assertIn(msg, str(e))

    def test_chain(self):
        api = QuizletAPI(client_id='1')
        sub = api._chain('foo-bar')
        self.assertIn('foo-bar', sub.url())

    def test_items(self):
        dwarves = [{'name': 'Dori'}, {'name': 'Nori'}, {'name': 'Ori'},
                   {'name': 'Bifur'}, {'name': 'Bofur'}, {'name': 'Bombur'}]

        def request_callback(request, uri, headers):
            if uri.endswith('dwarves') or uri.endswith('?page=1'):
                items = dwarves[:3]
                page_id = 1
            elif uri.endswith('?page=2'):
                items = dwarves[3:]
                page_id = 2
            else:
                items = []
                page_id = uri.split('=')[-1]
            return 200, headers, json.dumps({'page': page_id, 'dwarves': items, 'total_pages': 2})

        self.register_url(self.GET, 'dwarves', body=request_callback)

        api = QuizletAPI()
        self.assertEqual(list(api.dwarves.items()), dwarves)

    def test_user_url(self):
        self.assertIn('users/boromir', QuizletAPI(login='boromir').user_url.url())
