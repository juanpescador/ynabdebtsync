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

def test_transactions_by_category_name_subtransactions_without_memo_inherit_parent_memo():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    subtransaction_without_memo = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for nachos',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF',
			u'subTransactions': [
				{
					u'entityId': u'8BB2E729-90D7-47B0-91B4-D291156582DB',
					u'entityType': u'subTransaction',
					u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
					u'entityVersion': u'D-328',
					u'amount': -5.75,
					u'parentTransactionId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F'
				}
			]
        }
    ]

    ynab_budget.data["transactions"] = subtransaction_without_memo

    transactions = ynab_budget.transactions_by_category_name("Test Debt Category")

    assert_equal(transactions[0]["memo"], transactions[1]["memo"])

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

def test_transactions_by_category_name_filtered_by_date_returns_transactions_of_that_date():
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)

    transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for nachos',
            u'amount': 10,
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
            u'amount': 10,
            u'date': u'2015-03-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    ynab_budget.data["transactions"] = transactions

    march_2015_transactions = ynab_budget.filter_category_transactions_by_date('test debt category', '2015-03')
    assert_equal(len(march_2015_transactions), 1)
    assert_equal(march_2015_transactions[0]["date"], "2015-03-28")

    twentyfifteen_transactions = ynab_budget.filter_category_transactions_by_date('test debt category', '2015')
    assert_equal(len(twentyfifteen_transactions), 2)
    assert_equal(twentyfifteen_transactions[0]["date"], "2015-04-28")
    assert_equal(twentyfifteen_transactions[1]["date"], "2015-03-28")

    march_28_2015_transactions = ynab_budget.filter_category_transactions_by_date('test debt category', '2015-03-28')
    assert_equal(len(march_28_2015_transactions), 1)
    assert_equal(march_28_2015_transactions[0]["date"], "2015-03-28")

    november_2013_transactions = ynab_budget.filter_category_transactions_by_date('test debt category', '2013-11')
    assert_equal(len(november_2013_transactions), 0)

def test_transactions_by_category_name_non_deleted_transaction_returns_transaction():
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)

    transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for nachos',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    ynab_budget.data["transactions"] = transactions

    transactions = ynab_budget.transactions_by_category_name('test debt category')
    assert_equal(len(transactions), 1)

def test_transactions_by_category_name_undone_deleted_transaction_returns_transaction():
    """This case shouldn't appear, testing with a real budget revealed deleting
    a transaction and then undoing the delete resulted in the isTombstone
    property being removed from the transaction. Take it into account in case
    there is an edge case where isTombstone is kept and set to false."""
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)

    transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'isTombstone': False,
            u'memo': u'Loan for nachos',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    ynab_budget.data["transactions"] = transactions

    transactions = ynab_budget.transactions_by_category_name('test debt category')
    assert_equal(len(transactions), 1)

def test_transactions_by_category_name_deleted_transaction_returns_no_transactions():
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)

    transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'isTombstone': True,
            u'memo': u'Loan for nachos',
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    ynab_budget.data["transactions"] = transactions

    transactions = ynab_budget.transactions_by_category_name('test debt category')
    assert_equal(len(transactions), 0)

def test_transactions_by_category_name_mixed_deleted_and_non_deleted_transaction_returns_non_deleted_transactions():
    ynab_budget = ynabbudget.YnabBudget(this_budget_json)

    transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'isTombstone': True,
            u'memo': u'Loan for nachos',
            u'amount': 10,
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
            u'amount': 10,
            u'date': u'2015-04-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    ynab_budget.data["transactions"] = transactions

    transactions = ynab_budget.transactions_by_category_name('test debt category')
    assert_equal(len(transactions), 1)

def test_payee_ids_to_names_returns_dictionary_of_ids_to_names():
    ynab_budget = ynabbudget.YnabBudget(budget_json)

    payees = ynab_budget.payee_ids_to_names()

    assert_equal(payees["Payee/Transfer:37ADA60C-BE54-074E-F1B2-1FC8F2BE93CF"], "Transfer : Checking")
    assert_equal(payees["D8EB026F-8762-54EB-019C-208AC519C084"], "A shop")

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

def test_get_missing_transactions_returns_correct_transactions():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_missing, other_missing = budget_comparer.get_missing_transactions()

    assert_equal(len(this_missing), 1)
    assert_equal(len(other_missing), 0)
    assert_equal(this_missing[0]["memo"], "Loan for beer")
    assert_equal(this_missing[0]["amount"], -5)

def test_get_missing_transactions_this_transactions_other_transactions_equal_length_doesnt_throw_exception():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for nachos',
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

    try:
        this_missing, other_missing = budget_comparer.get_missing_transactions()
    except Exception as e:
        # Can't do self.fail as tests are functions and not class methods.
        assert_equal(False, True, msg="Budgets with same amount of transactions unexpectedly failed:\n" + str(e))

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
            u'amount': -11,
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

    # abs(this_amount) > abs(other_amount)
    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], -11)
    assert_equal(other_missing[0]["memo"], "Loan for water")

    # abs(this_amount) < abs(other_amount)
    this_transactions[0]["amount"] = -7
    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], -7)
    assert_equal(other_missing[0]["memo"], "Loan for water")

    # abs(this_amount) == abs(other_amount)
    this_transactions[0]["amount"] = -10
    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], -10)
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

def test_get_missing_transactions_this_positive_gt_other_negative_returns_other_transaction():
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
            u'memo': u'Loan for milk',
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
    assert_equal(this_missing[0]["amount"], -7)
    assert_equal(this_missing[0]["memo"], "Loan for milk")

def test_get_missing_transactions_this_positive_lt_other_negative_returns_this_transaction():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for wine',
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

    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["amount"], 7)
    assert_equal(other_missing[0]["memo"], "Borrow for wine")

def test_get_missing_transactions_when_number_of_transactions_of_same_amount_differ_and_dates_mismatched_advances_correct_number_of_transactions():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for wine',
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
            u'memo': u'Borrow for wine',
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
            u'memo': u'Borrow for wine',
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
            u'memo': u'Borrow for wine',
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
            u'memo': u'Borrow for wine',
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
            u'memo': u'Loan for wine',
            u'amount': -7,
            u'date': u'2015-04-29',
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
            u'memo': u'Loan for wine',
            u'amount': -7,
            u'date': u'2015-04-29',
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
            u'memo': u'Loan for wine',
            u'amount': -7,
            u'date': u'2015-04-29',
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
            u'memo': u'Loan for wine',
            u'amount': -7,
            u'date': u'2015-04-29',
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
            u'date': u'2015-04-29',
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
    assert_equal(other_missing[0]["amount"], 7)
    assert_equal(other_missing[0]["memo"], "Borrow for wine")

def test_get_missing_transactions_with_start_date_returns_transactions_from_start_date_onwards():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Borrow for wine',
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
            u'memo': u'Borrow for wine',
            u'amount': 7,
            u'date': u'2015-05-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]

    other_transactions = []

    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    budget_comparer.set_start_date("2015-05")
    this_missing, other_missing = budget_comparer.get_missing_transactions()

    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["date"], "2015-05-28")
    assert_equal(other_missing[0]["amount"], 7)
    assert_equal(other_missing[0]["memo"], "Borrow for wine")

def test_get_missing_transactions_with_start_date_ignores_past_transactions():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_transactions = [
        {
            u'cleared': u'Cleared',
            u'entityVersion': u'A-118',
            u'entityType': u'transaction',
            u'memo': u'Loan for wine',
            u'amount': -1.5,
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
            u'memo': u'Loan for wine',
            u'amount': -1.5,
            u'date': u'2015-05-28',
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
            u'memo': u'Loan for crisps',
            u'amount': 1.65,
            u'date': u'2015-05-28',
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
            u'memo': u'Loan for crisps',
            u'amount': -1.65,
            u'date': u'2015-05-28',
            u'entityId': u'AD5F14BC-5BCC-E075-4B14-208676CA762F',
            u'accepted': True,
            u'payeeId': u'45C13591-718B-3025-0F3C-2086F37E7676',
            u'categoryId': u'DEF375CA-58D2-D332-4C79-20862B7566F8',
            u'accountId': u'37ADA60C- BE54-074E-F1B2-1FC8F2BE93CF'
        }
    ]


    budget_comparer.this_budget.data["transactions"] = this_transactions
    budget_comparer.other_budget.data["transactions"] = other_transactions

    budget_comparer.set_start_date("2015-05")
    this_missing, other_missing = budget_comparer.get_missing_transactions()

    assert_equal(len(this_missing), 0)
    assert_equal(len(other_missing), 1)
    assert_equal(other_missing[0]["date"], "2015-05-28")
    assert_equal(other_missing[0]["amount"], -1.5)
    assert_equal(other_missing[0]["memo"], "Loan for wine")

def test_get_this_payees_returns_this_budgets_payees():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    this_payees = budget_comparer.get_this_payees()

    assert_equal(this_payees["45C13591-F8762-54EB-019C-208AC519C084"], "This budget shop")

def test_get_other_payees_returns_other_budgets_payees():
    budget_comparer = ynabbudget.YnabBudgetComparer(this_budget_json, "Test Debt Category", other_budget_json, "Test Debt Category")

    other_payees = budget_comparer.get_other_payees()

    assert_equal(other_payees["8F925C3-F8762-54EB-019C-208AC519C084"], "Other budget shop")
