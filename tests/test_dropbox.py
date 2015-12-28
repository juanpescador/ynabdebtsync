# -*- coding: utf-8 -*-

from ynabdebtsync import dropbox
from nose.tools import assert_equal

# Assumes one budget named dineros.
# Generate a token at https://www.dropbox.com/developers
token = 'token'

def test_get_budgets_returns_all_budgets():
    db = dropbox.Dropbox(token)
    budgets = db.get_all_budgets()
    budget = budgets[0]
    assert_equal(budget['name'], 'dineros')

def test_get_budget_file_returns_budget():
    db = dropbox.Dropbox(token)
    budgets = db.get_all_budgets()
    budget = budgets[0]
    budget_file = db.get_budget_file(budget['path'])
    print ('Budget {name} file has {count} characters'
                .format(name=budget['name'], count=len(budget_file)))
