# -*- coding: utf-8 -*-

from flask import Flask

flask_app = Flask('ynabdebtsync')
# Instantiat the logger, attaching a handler so that library submodule loggers'
# records propagate upwards to the flask logger. E.g. ynabdebtsync.dropbox's
# logger records won't propagate up to flask's logger otherwise. See
# http://stackoverflow.com/a/7294147.
flask_app.logger
