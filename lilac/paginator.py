#!/usr/bin/env python


class Paginator(object):

    def __init__(self, results, total, page, perpage, url, gule='?page='):
        self.results = results
        self.total = total
        self.page = page
        self.first = 'First'
        self.last = 'Last'
        self.next = 'Next'
        self.prev = 'Previous'
        self.perpage = perpage
        self.url = url
        self._index = 0
        self.gule = gule

    def next_link(self, text=None, default=''):
        text = text or self.text
        pages = (self.total / self.perpage) + 1
        if self.page < pages:
            page = self.page + 1
            return '<a href="' + self.url + self.gule + str(page) + '">' + text + '</a>'

        return default

    def pre_link(self, text=None, default=''):
        text = text or self.prev
        if self.page > 1:
            page = self.page - 1
            return '<a href="' + self.url + self.gule + str(page) + '">' + text + '</a>'

        return default

    def links(self):
        html = ''
        pages = (self.total / self.perpage) + 1
        ranged = 4
        if pages > 1:
            if self.page > 1:
                page = self.page - 1
                html += '<a href="' + self.url + '">' + self.first + '</a>' + \
                    '<a href="' + self.url + self.gule + str(page) + '">' + self.prev + '</a>'
            for i in range(self.page - ranged, self.page + ranged):
                if i < 0:
                    continue
                page = i + 1
                if page > pages:
                    break

                if page == self.page:
                    html += '<strong id="current-page">' + str(page) + '</strong>'
                else:
                    html += '<a href="' + self.url + self.gule + str(page) + '">' + str(page) + '</a>'

            if self.page < pages:
                page = self.page + 1

                html += '<a href="' + self.url + self.gule + str(page) + '">' + self.next + '</a> <a href="' + \
                    self.url + self.gule + str(pages) + '">' + self.last + '</a>'

        return html

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.results[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result

    __next__ = next  # py3 compat
