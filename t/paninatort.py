from lilac.paginator import Paginator
import unittest


class PaginatorTest(unittest.TestCase):

    def setUp(self):
        result = [_ for _ in range(1, 10)]
        self.p = Paginator(result, 100, 10, 5, '/test')

    def test_next_link(self):
        self.assertEqual(self.p.next_link('next'), '<a href="/test?page=11">next</a>')
        self.p.page = 22
        self.assertEqual(self.p.next_link('next'), '')

    def test_pre_link(self):
        self.assertEqual(self.p.pre_link('pre'), '<a href="/test?page=9">pre</a>')
        self.p.page = 1
        self.assertEqual(self.p.pre_link('pre'), '')

    def test_iter(self):
        for _ in range(1, 9):
            next(self.p)
        self.assertEqual(next(self.p), 9)
        self.assertEqual(self.p._index, 9)
        self.assertRaises(StopIteration, lambda: next(self.p))

    def test_len(self):
        self.assertEqual(9, len(self.p))

    def test_links(self):

        self.assertTrue(self.p.links().startswith(
            '<a href="/test">First</a><a href="/test?page=9">Previous</a><a href="/test?page=7">7</a>'))
        self.p.page = 0
        self.assertEqual(
            self.p.links(), '<a href="/test?page=1">1</a><a href="/test?page=2">2</a><a href="/test?page=3">3</a><a href="/test?page=4">4</a><a href="/test?page=1">Next</a> <a href="/test?page=21">Last</a>')
        self.p.page = 22
        self.assertEqual(
            self.p.links(), '<a href="/test">First</a><a href="/test?page=21">Previous</a><a href="/test?page=19">19</a><a href="/test?page=20">20</a><a href="/test?page=21">21</a>')


if __name__ == '__main__':
    unittest.main(verbosity=2)
