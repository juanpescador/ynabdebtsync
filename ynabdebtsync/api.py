# -*- coding: utf8 -*-

from flask import Flask, request
from flask_restful import Resource, Api
from ynabbudget import YnabBudgetComparer

app = Flask(__name__)
api = Api(app)

class CategoryComparison(Resource):
    def post(self):
        this_file = request.files["this_budget"]
        this_json = this_file.read().replace("\n", "")
        other_file = request.files["other_budget"]
        other_json = other_file.read().replace("\n", "")

        comparer = YnabBudgetComparer(this_json, 'eli', other_json, 'john')
        comparer.set_start_date("2015-07")
        missing_txns = comparer.get_missing_transactions()
        return {"this_missing": missing_txns[0], "other_missing": missing_txns[1]}

    def get(self):
        return {"key": "value"}

api.add_resource(CategoryComparison, "/categorycomparison")

