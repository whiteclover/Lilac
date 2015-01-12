#!/usr/bin/env python
 

from solo.template import render_template


class HomeController(object):

    def index(self):
        return render_template('index.html')

   
    def _404_page(self, *args, **kw):
        return render_template('404.html')