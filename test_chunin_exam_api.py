import unittest
import os
import sys
from unittest.mock import patch, MagicMock

BASE_DIR = os.path.dirname(__file__)
GAMES_DIR = os.path.join(BASE_DIR, 'MyFlaskapp', 'games')
sys.path.insert(0, GAMES_DIR)

import chunin_exam as ce


class TestChuninExamAPI(unittest.TestCase):
    def test_difficulty_param(self):
        self.assertEqual(ce._difficulty_param('Easy'), 'easy')
        self.assertEqual(ce._difficulty_param('Medium'), 'medium')
        self.assertEqual(ce._difficulty_param('Hard'), 'hard')
        self.assertEqual(ce._difficulty_param(''), 'medium')

    def test_parse_question_payload_dict(self):
        payload = {"questions": [{"question": "Q1", "answer": "A1"}, {"q": "Q2", "a": "A2"}]}
        out = ce.parse_question_payload(payload)
        self.assertEqual(out, [("Q1", "A1"), ("Q2", "A2")])

    def test_parse_question_payload_list(self):
        payload = [{"text": "Q1", "ans": "A1"}, {"question": "Q2", "answer": "A2"}]
        out = ce.parse_question_payload(payload)
        self.assertEqual(out, [("Q1", "A1"), ("Q2", "A2")])

    @patch('chunin_exam.request.urlopen')
    def test_fetch_naruto_questions_success(self, m_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"questions": [{"question": "Who?", "answer": "Naruto"}]}'
        m_urlopen.return_value.__enter__.return_value = mock_resp
        cache = {}
        items = ce.fetch_naruto_questions('https://api.example.com', 'Medium', timeout=1.0, max_retries=0, cache=cache)
        self.assertEqual(items, [("Who?", "Naruto")])
        self.assertIn(('https://api.example.com', 'medium'), cache)

    @patch('chunin_exam.request.urlopen')
    def test_fetch_naruto_questions_invalid_json(self, m_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'invalid'
        m_urlopen.return_value.__enter__.return_value = mock_resp
        items = ce.fetch_naruto_questions('https://api.example.com', 'Medium', timeout=1.0, max_retries=0, cache={})
        self.assertEqual(items, [])

    @patch('chunin_exam.request.urlopen')
    def test_fetch_naruto_questions_rate_limit(self, m_urlopen):
        class E(Exception):
            pass
        from urllib.error import HTTPError
        e = HTTPError(url='u', code=429, msg='Too Many', hdrs={'Retry-After': '1'}, fp=None)
        m_urlopen.side_effect = e
        with patch('chunin_exam.time.sleep') as m_sleep:
            items = ce.fetch_naruto_questions('https://api.example.com', 'Hard', timeout=1.0, max_retries=1, cache={})
            self.assertEqual(items, [])
            m_sleep.assert_called()


if __name__ == '__main__':
    unittest.main()

