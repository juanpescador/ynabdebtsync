# YNAB Debt Sync ##

[YNAB Debt Sync] lets you quickly reconcile your shared debt category with another
person. If you track the money you lend to someone with YNAB and they do the
same, this web application automates the process of finding which transactions
are missing from each other’s budget so the totals tally up.

[This article on my blog][BlogArticle] explains when and why this is useful,
while [this one][AlgorithmArticle] describes the algorithm (basically it’s an
algorithm to find missing transactions, i.e. errors, in double-entry
bookkeeping).

![](docs/img/demo-walkthrough.gif)

YNAB Debt Sync can compare budgets stored in Dropbox. Note that this requires a
lot of trust between participants, as the other person is able to peruse your
entire budget. Share your “YNAB” directory with someone who already uses YNAB
(and have them share theirs with you), so that you have a “YNAB” directory (your
budget) and a “YNAB (1)” directory (their budget). The server temporarily stores
both budgets in RAM, so only use the Heroku-hosted app for dummy budgets.

## Dependencies ##

* Python 2.7.9
* Node.js v0.10.26
* Semantic UI v2.0.7

## Build

Install the Python dependencies in a virtualenv:

    $ pip install -r requirements.txt

Install the Node.js dependencies:

    $ npm install

Semantic UI is installed via npm, but may fail on the first attempt, during
`gulp install`. If so, execute `npm install` again.

After successfully installing the Node.js dependencies, execute `gulp build`
from the semantic directory:

    $ cd semantic
    $ gulp build

The CSS and JavaScript files will be created under `ynabdebtsync/static/css`.

## Running the development server

From the virtualenv with all dependencies installed:

    $ python run.py

Then visit http://127.0.0.1:5000 in a browser.

## Deploying to Heroku

Read the [HerokuSetup document].

## Running the tests ##

From the project’s root, execute

    $ nosetests

[YNAB Debt Sync]: https://ynabdebtsync.herokuapp.com
[HerokuSetup document]: ./docs/HerokuSetup.md
[BlogArticle]: http://maian.org/blog/2015/08/managing-short-term-lending-with-two-way-ynab/
[AlgorithmArticle]: http://maian.org/blog/2015/08/efficiently-finding-incorrect-transactions-in-double-entry-bookkeeping/
