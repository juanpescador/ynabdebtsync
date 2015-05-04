# -*- coding: utf8 -*-
import os
from nose.tools import assert_raises, assert_equal
from ynabdebtsync import ynabbudget

def test_instantiating_budget_with_json_works():
    budget_file_path = os.path.join(os.path.dirname(__file__), "budget.json")

    with open (budget_file_path) as budget_file:
        budget_json = budget_file.read().replace('\n', '')
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    assert ynab_budget.data["fileMetaData"]["budgetDataVersion"] == "4.2"

def test_instantiating_budget_without_json_raises_exception():
    with assert_raises(ValueError) as e:
        ynab_budget = ynabbudget.YnabBudget(None)

    assert_equal(e.exception.message, "Budget JSON is None")

def test_instantiating_budget_with_empty_json_raises_exception():
    with assert_raises(ValueError) as e:
        ynab_budget = ynabbudget.YnabBudget("")

    assert_equal(e.exception.message, "Budget JSON is empty")

def test_instantiating_budget_with_malformed_json_raises_exception():
    with assert_raises(ynabbudget.YnabBudgetMalformedError) as e:
        ynab_budget = ynabbudget.YnabBudget("[")

    assert_equal(e.exception.message, "Budget JSON is malformed")
