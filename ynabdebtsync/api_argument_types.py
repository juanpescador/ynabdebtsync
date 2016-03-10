# -*- coding: utf-8 -*-

from server import flask_app
from werkzeug.routing import BaseConverter

def non_empty_string(value, name):
    flask_app.logger.debug("non_empty_string checking value: '{value}'".format(value=value))

    if value == u"":
        raise ValueError("The parameter '{}' is required.".format(name))

    return value

class TargetBudgetConverter(BaseConverter):
    """Implements a converter to ensure a URL route contains either 'this' or
    'other'. If the value is correct, no further conversion is needed, so
    to_python and to_url are not overridden. If the provided value does not
    match the regex a 404 is returned. See
    http://werkzeug.pocoo.org/docs/0.11/routing/#custom-converters
    https://exploreflask.com/views.html
    http://stackoverflow.com/questions/5870188/does-flask-support-regular-expressions-in-its-url-routing"""
    def __init__(self, url_map):
        super(TargetBudgetConverter, self).__init__(url_map)
        self.regex = '(?:this|other)'
