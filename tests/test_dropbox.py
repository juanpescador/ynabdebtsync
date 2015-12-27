# -*- coding: utf-8 -*-

from ynabdebtsync import dropbox
from nose.tools import assert_equal

# Assumes one budget named dineros.
# Generate a token at https://www.dropbox.com/developers/apps/info/uo6kvpwo8rv9bqi
token = '2s8cc2RuxUEAAAAAAAABABrV-tejV9yR7XeRNs53VGMh9l0FBh4xbpHDWFQeP8c2'

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
