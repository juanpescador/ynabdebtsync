# -*- coding: utf8 -*-

import ynabdebtsync.server
import ynabdebtsync.app
import ynabdebtsync.api
if __name__ == "__main__":
    ynabdebtsync.server.flask_app.run(debug=True)
