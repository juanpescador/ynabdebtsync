# -*- coding: utf8 -*-
import os
from nose.tools import assert_raises, assert_equal, assert_true
from ynabdebtsync import ynabbudget
from decimal import Decimal

budget_file_path = os.path.join(os.path.dirname(__file__), "budget.json")
this_budget_file_path = os.path.join(os.path.dirname(__file__), "this_budget.json")
other_budget_file_path = os.path.join(os.path.dirname(__file__), "other_budget.json")

with open (budget_file_path) as budget_file:
    budget_json = budget_file.read().replace('\n', '')

with open(this_budget_file_path) as this_budget_file:
    this_budget_json = this_budget_file.read().replace('\n', '')

with open(other_budget_file_path) as other_budget_file:
    other_budget_json = other_budget_file.read().replace('\n', '')

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

def test_get_category_id_from_name_inexistent_category_raises_exception():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    with assert_raises(LookupError) as e:
        ynab_budget.category_id_from_name("non existent category")

    assert_equal(e.exception.message,
                 "No category with name 'non existent category' exists in the budget")

def test_get_category_id_from_name_existing_category_returns_id():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    assert_equal(ynab_budget.category_id_from_name("Test Debt Category"), "DEF375CA-58D2-D332-4C79-20862B7566F8")

def test_transactions_by_category_name_inexistent_category_raises_exception():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    with assert_raises(LookupError) as e:
        ynab_budget.transactions_by_category_name("non existent category")

    assert_equal(e.exception.message,
                 "No category with name 'non existent category' exists in the budget")

def test_transactions_by_category_name_existing_category_returns_all_transactions():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    transactions = ynab_budget.transactions_by_category_name("Test Debt Category")

    assert_equal(len(transactions), 3)

def test_transactions_by_category_name_no_transactions_returns_empty_list():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    transactions = ynab_budget.transactions_by_category_name("Car Payment")

    assert_equal(len(transactions), 0)

def test_master_categories_to_subcategories_structure_is_correct():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    category_hierarchy = ynab_budget.master_categories_to_subcategories()

    assert_true("Giving" in category_hierarchy)
    assert_true("Charitable" in category_hierarchy["Giving"])
    assert_equal(category_hierarchy["Giving"]["Charitable"], "A6")

def test_calculate_category_total_returns_correct_amount():
    ynab_budget = ynabbudget.YnabBudget(budget_json)
    assert_equal(ynab_budget.calculate_category_total("Test Debt Category"), Decimal(-5))

def test_calculate_category_total_decimal_amount_returns_correct_amount():
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)
    assert_equal(ynab_budget.calculate_category_total("Tithing"), 242.73)

# YnabComparer
def test_categories_reconcile_if_category_totals_are_equal():
    budget_comparer = ynabbudget.YnabBudgetComparer(budget_json, "Test Debt Category", budget_json, "Test Debt Category")

    assert_true(budget_comparer.categories_are_reconciled())

def test_get_missing_transactions_of_amount_returns_correct_number_of_missing_transactions():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    assert_equal(len(budget_comparer._get_missing_transactions_of_amount(5)), 1)

def test_get_missing_transactions_of_amount_returns_correct_missing_transactions():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    missing_transaction = budget_comparer._get_missing_transactions_of_amount(5)[0]
    assert_equal(missing_transaction["memo"], "Loan for beer")
    assert_equal(missing_transaction["amount"], -5)

def test_no_transactions_of_given_amount_throws_exception():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    with assert_raises(ValueError) as e:
        budget_comparer._get_missing_transactions_of_amount(3)

#def test_get_missing_transactions_returns_correct_transactions():
    #budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    #this_missing, other_missing = budget_comparer.get_missing_transactions()

    #assert_equal(len(this_missing), 1)
    #assert_equal(len(other_missing), 0)
    #assert_equal(this_missing[0]["memo"], "Loan for beer")
    #assert_equal(this_missing[0]["amount"], -5)

#def test_get_missing_transactions_this_transactions_other_transactions_equal_length_doesnt_throw_exception():
    #budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    #this_transactions = [
        #{
            #u'cleared': u'Cleared',
            #u'entityVersion': u'A-118',
            #u'entityType': u'transaction',
            #u'memo': u'Loan for nachos',
            #u'amount': 10,
            #u'date': u'2015-04-28',
            #u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            #u'accepted': True,
            #u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            #u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            #u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        #}
    #]

    #other_transactions = [
        #{
            #u'cleared': u'Cleared',
            #u'entityVersion': u'A-118',
            #u'entityType': u'transaction',
            #u'memo': u'Borrow for nachos',
            #u'amount': 8,
            #u'date': u'2015-04-28',
            #u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            #u'accepted': True,
            #u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            #u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            #u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        #}
    #]
    #this_missing, other_missing = budget_comparer.get_missing_transactions()

# Implement this negative, other positive, abs(this) > abs(other)
def test_get_missing_transactions_this_negative_gt_other_positive_returns_this_transaction():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for tea',
            u'amount': -10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        },
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for nachos',
            u'amount': -8,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    other_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for nachos',
            u'amount': 8,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    this_missing, other_missing = budget_comparer.get_missing_transactions()

    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], -10)
    assert_equal(other_missing[0]["memo"], "Loan for tea")

def test_get_missing_transactions_this_negative_lt_other_positive_returns_other_transaction():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for beer',
            u'amount': -10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    other_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for tea',
            u'amount': 12,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        },
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for beer',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    this_missing, other_missing = budget_comparer.get_missing_transactions()

    assert_equal(len(this_missing), 1)
    assert_equal(len(other_missing), 0)
    assert_equal(this_missing[0]["amount"], 12)
    assert_equal(this_missing[0]["memo"], "Borrow for tea")

def test_get_missing_transactions_this_negative_all_cases_other_negative_returns_this_transaction():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for water',
            u'amount': -7,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        },
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for beer',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    other_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for beer',
            u'amount': -10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    this_missing, other_missing = budget_comparer.get_missing_transactions()

    # this_missing gets the -3 transaction due to leftover transaction processing.
    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], -7)
    assert_equal(other_missing[0]["memo"], "Loan for water")

def test_get_missing_transactions_this_positive_all_cases_other_positive_returns_other_transaction():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for beer',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    other_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for milk',
            u'amount': 7,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        },
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for beer',
            u'amount': -10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    this_missing, other_missing = budget_comparer.get_missing_transactions()

    # abs(this_amount) > abs(other_amount)
    assert_equal(len(this_missing), 1)
    assert_equal(len(other_missing), 0)
    assert_equal(this_missing[0]["amount"], 7)
    assert_equal(this_missing[0]["memo"], "Borrow for milk")

    # abs(this_amount) < abs(other_amount)
    other_transactions[0]["amount"] = 11

    assert_equal(len(this_missing), 1)
    assert_equal(len(other_missing), 0)
    assert_equal(this_missing[0]["amount"], 11)
    assert_equal(this_missing[0]["memo"], "Borrow for milk")

    # abs(this_amount) == abs(other_amount)
    other_transactions[0]["amount"] = 10

    assert_equal(len(this_missing), 1)
    assert_equal(len(other_missing), 0)
    assert_equal(this_missing[0]["amount"], 10)
    assert_equal(this_missing[0]["memo"], "Borrow for milk")
