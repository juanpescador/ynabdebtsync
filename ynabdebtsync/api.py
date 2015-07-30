# -*- coding: utf8 -*-

from . import flask_app
from flask import request
from flask_restful import Resource, Api
from ynabbudget import YnabBudgetComparer

api = Api(flask_app)

class CategoryComparison(Resource):
    def post(self):
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

api.add_resource(CategoryComparison, "/api/categorycomparison")

