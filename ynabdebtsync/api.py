# -*- coding: utf8 -*-

import werkzeug
import time

from server import flask_app
from api_argument_types import non_empty_string
from flask import request
from flask_restful import Resource, Api, reqparse
from ynabbudget import YnabBudgetComparer
from dropbox import Dropbox

api = Api(flask_app)

class CategoryComparison(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('this_budget', required=True, type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('other_budget', required=True, type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('this_target_category', required=True, type=non_empty_string, location='form')
        parser.add_argument('other_target_category', required=True, type=non_empty_string, location='form')
        parser.add_argument('start_date', required=True, location='form')
        args = parser.parse_args()

        this_file = args["this_budget"]
        this_json = this_file.read().replace("\n", "")
        this_target_category = args["this_target_category"]
        other_file = request.files["other_budget"]
        other_json = other_file.read().replace("\n", "")
        other_target_category = args["other_target_category"]

        start_date = args["start_date"]

        comparer = YnabBudgetComparer(this_json, this_target_category, other_json, other_target_category)
        comparer.set_start_date(start_date)

        missing_txns = comparer.get_missing_transactions()
        return {"this_missing": missing_txns[0], "other_missing": missing_txns[1]}

    def get(self):
        return {"key": "value"}

class DropboxBudgets(Resource):
    def post(self, targetBudget):
        token = request.get_json()['access_token']
        db = Dropbox(token)

        if targetBudget == 'this':
            start = time.clock()
            budgets = db.get_own_budgets()
            end = time.clock()
            flask_app.logger.debug("Get own budgets time elapsed: {time}s".format(time=(end - start)))
        elif targetBudget == 'other':
            start = time.clock()
            budgets = db.get_their_budgets()
            end = time.clock()
            flask_app.logger.debug("Get their budgets time elapsed: {time}s".format(time=(end - start)))
        return budgets

class DropboxBudgetComparison(Resource):
    def post(self):
        method_start = time.clock()
        flask_app.logger.info("Comparing budgets")

        json = request.get_json()
        token = json['access_token']
        this_budget_path = json['this_budget_path']
        other_budget_path = json['other_budget_path']

        db = Dropbox(token)

        start = time.clock()
        this_json = db.get_budget_file(this_budget_path)
        end = time.clock()
        elapsed = end - start
        flask_app.logger.debug("Get this budget time elapsed: {time}s".format(time=elapsed))

        start = time.clock()
        other_json = db.get_budget_file(other_budget_path)
        end = time.clock()
        elapsed = end - start
        flask_app.logger.debug("Get other budget time elapsed: {time}s".format(time=elapsed))

        this_target_category = json['this_target_category']
        other_target_category = json['other_target_category']

        start_date = json['comparison_start_date']

        comparer = YnabBudgetComparer(this_json, this_target_category, other_json, other_target_category)
        comparer.set_start_date(start_date)

        start = time.clock()
        missing_txns = comparer.get_missing_transactions()
        end = time.clock()
        flask_app.logger.debug("Find missing transactions time elapsed: {time}s".format(time=(end - start)))

        method_finish = time.clock()
        method_elapsed = method_finish - method_start
        flask_app.logger.info("Finished comparing budgets. Time elapsed: {time}s".format(time=method_elapsed))

        this_payees = comparer.get_this_payees()
        other_payees = comparer.get_other_payees()

        return {"this_missing": missing_txns[0], "other_missing": missing_txns[1],
                "this_payees": this_payees, "other_payees": other_payees}

api.add_resource(CategoryComparison, "/api/categorycomparison")
api.add_resource(DropboxBudgets, "/api/dropboxbudgets/<target_budget:targetBudget>")
api.add_resource(DropboxBudgetComparison, "/api/dropboxbudgetcomparison")

