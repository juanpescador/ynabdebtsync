# -*- coding: utf8 -*-
import os
from nose.tools import assert_raises, assert_equal
from ynabdebtsync import ynabbudget

budget_file_path = os.path.join(os.path.dirname(__file__), "budget.json")

with open (budget_file_path) as budget_file:
    budget_json = budget_file.read().replace('\n', '')

def test_instantiating_budget_with_json_works():
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

def test_get_category_id_from_name_inexistent_category_returns_none():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    assert_equal(ynab_budget.category_id_from_name("non existent category"), None)

def test_get_category_id_from_name_existing_category_returns_id():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    assert_equal(ynab_budget.category_id_from_name("Enric loans"), "0B268460-6D45-B9F9-C8BA-9748D21FE0DD")

def test_transactions_by_category_name_inexistent_category_raises_exception():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    with assert_raises(LookupError) as e:
        ynab_budget.transactions_by_category_name("non existent category")

    assert_equal(e.exception.message,
                 "No category with name 'non existent category' exists in the budget")

def test_transactions_by_category_name_existing_category_returns_all_transactions():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    transactions = ynab_budget.transactions_by_category_name("Motorbike repairs")

    assert_equal(len(transactions), 10)
