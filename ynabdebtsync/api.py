# -*- coding: utf8 -*-

import werkzeug
import time

from server import flask_app
from flask import request
from flask_restful import Resource, Api, reqparse
from ynabbudget import YnabBudgetComparer
from dropbox import Dropbox

api = Api(flask_app)

class CategoryComparison(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('this_budget', required=True, type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        this_file = request.files["this_budget"]
        this_json = this_file.read().replace("\n", "")
        this_target_category = request.form["this_target_category"]
        other_file = request.files["other_budget"]
        other_json = other_file.read().replace("\n", "")
        other_target_category = request.form["other_target_category"]

        start_date = request.form["start_date"]

        comparer = YnabBudgetComparer(this_json, this_target_category, other_json, other_target_category)
        comparer.set_start_date(start_date)

        missing_txns = comparer.get_missing_transactions()
        return {"this_missing": missing_txns[0], "other_missing": missing_txns[1]}

    def get(self):
        return {"key": "value"}

class DropboxBudgets(Resource):
    def post(self, whose):
        token = request.get_json()['access_token']
        db = Dropbox(token)

        if whose == 'mine':
            start = time.clock()
            budgets = db.get_own_budgets()
            end = time.clock()
            flask_app.logger.debug("Get own budgets time elapsed: {time}s".format(time=(end - start)))
        elif whose == 'theirs':
            start = time.clock()
            budgets = db.get_their_budgets()
            end = time.clock()
            flask_app.logger.debug("Get their budgets time elapsed: {time}s".format(time=(end - start)))
        return budgets

class DropboxBudgetComparison(Resource):
    def post(self):
        method_start = time.clock()
        flask_app.logger.debug("Comparing budgets")

        json = request.get_json()
        token = json['access_token']
        this_budget_path = json['this_budget_path']
        other_budget_path = json['other_budget_path']

        db = Dropbox(token)

        start = time.clock()
        this_json = db.get_budget_file(this_budget_path)
        end = time.clock()
        elapsed = end - start
        flask_app.logger.debug("Get this budget time elapsed: {time}s, {speed} KB/s".format(time=elapsed, speed=(len(this_json) // 1024 // elapsed)))

        start = time.clock()
        other_json = db.get_budget_file(other_budget_path)
        end = time.clock()
        elapsed = end - start
        flask_app.logger.debug("Get other budget time elapsed: {time}s, {speed} KB/s".format(time=elapsed, speed=(len(other_json) // 1024 // elapsed)))

        this_target_category = "eli"
        other_target_category = "john"

        start_date = "2015"

        comparer = YnabBudgetComparer(this_json, this_target_category, other_json, other_target_category)
        comparer.set_start_date(start_date)

        start = time.clock()
        missing_txns = comparer.get_missing_transactions()
        end = time.clock()
        flask_app.logger.debug("Find missing transactions time elapsed: {time}s".format(time=(end - start)))

        method_finish = time.clock()
        method_elapsed = method_finish - method_start
        flask_app.logger.debug("Finished comparing budgets. Time elapsed: {time}s".format(time=method_elapsed))
        return {"this_missing": missing_txns[0], "other_missing": missing_txns[1]}

api.add_resource(CategoryComparison, "/api/categorycomparison")
api.add_resource(DropboxBudgets, "/api/dropboxbudgets/<string:whose>")
api.add_resource(DropboxBudgetComparison, "/api/dropboxbudgetcomparison")

