# -*- coding: utf8 -*-

import ynabdebtsync.server
import ynabdebtsync.app
import ynabdebtsync.api
import logging

if __name__ == "__main__":
    ynabdebtsync.server.flask_app.run(debug=True)
else:
    # We're on Heroku, expose production mode flask_app to gunicorn. We can't
    # just pass ynabdebtsync.server:flask_app to gunicorn because
    # ynabdebtsync.app and .api need to be imported to add the different routes
    # to the server.
    heroku_server = ynabdebtsync.server.flask_app
    heroku_server.debug = False
    # Add handler to Flask logger to send records to gunicorn stderr.
    # https://github.com/benoitc/gunicorn/issues/379
    heroku_server.logger.addHandler(logging.StreamHandler())
    heroku_server.logger.setLevel(logging.INFO)
