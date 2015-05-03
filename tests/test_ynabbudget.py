# -*- coding: utf8 -*-
import os
from ynabdebtsync import ynabbudget

def test_loading_budget_works():
    budget_file_path = os.path.join(os.path.dirname(__file__), "budget.json")

    with open (budget_file_path) as budget_file:
        budget_json = budget_file.read().replace('\n', '')
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    assert ynab_budget.data["fileMetaData"]["budgetDataVersion"] == "4.2"
