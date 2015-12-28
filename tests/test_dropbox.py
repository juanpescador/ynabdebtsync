# -*- coding: utf-8 -*-

from ynabdebtsync import dropbox
from nose.tools import assert_equal

# Assumes one budget named dineros.
# Generate a token at https://www.dropbox.com/developers
token = 'token'

def test_get_budgets_returns_all_budgets():
    db = dropbox.Dropbox(token)
    budgets = db.get_own_budgets()
    budget = budgets[0]
    assert_equal(budget['name'], 'dineros')

def test_get_budget_file_returns_budget():
    db = dropbox.Dropbox(token)
    budgets = db.get_own_budgets()
    budget = budgets[0]
    budget_file = db.get_budget_file(budget['path'])
    print ('Budget {name} file has {count} characters'
                .format(name=budget['name'], count=len(budget_file)))

def test_line_profile_get_budget_file_returns_budget():
    db = dropbox.Dropbox(token)
    budgets = db.get_own_budgets()
    budget = budgets[0]

    # From https://zapier.com/engineering/profiling-python-boss/
    try:
        from line_profiler import LineProfiler

        def do_profile(follow=[]):
            def inner(func):
                def profiled_func(*args, **kwargs):
                    try:
                        profiler = LineProfiler()
                        profiler.add_function(func)
                        for f in follow:
                            profiler.add_function(f)
                        profiler.enable_by_count()
                        return func(*args, **kwargs)
                    finally:
                        profiler.print_stats()
                return profiled_func
            return inner

    except ImportError:
        def do_profile(follow=[]):
            "Helpful if you accidentally leave in production!"
            def inner(func):
                def nothing(*args, **kwargs):
                    return func(*args, **kwargs)
                return nothing
            return inner

    def get_number():
        for x in xrange(5000000):
            yield x

    @do_profile(follow=[db.get_budget_file])
    def expensive_function():
        return db.get_budget_file(budget['path'])

    result = expensive_function()
    budget_file = result


    print ('Budget {name} file has {count} characters'
                .format(name=budget['name'], count=len(budget_file)))

def test_cProfile_get_budget_file_returns_budget():
    db = dropbox.Dropbox(token)
    budgets = db.get_own_budgets()
    budget = budgets[0]

    # From https://zapier.com/engineering/profiling-python-boss/
    import cProfile

    def do_cprofile(func):
        def profiled_func(*args, **kwargs):
            profile = cProfile.Profile()
            try:
                profile.enable()
                result = func(*args, **kwargs)
                profile.disable()
                return result
            finally:
                profile.print_stats()
        return profiled_func

    @do_cprofile
    def expensive_function():
        return db.get_budget_file(budget['path'])

    # perform profiling
    result = expensive_function()
    budget_file = result

    print ('Budget {name} file has {count} characters'
                .format(name=budget['name'], count=len(budget_file)))

def test_dropbox_comparison():
    data = {
        'access_token': token,
        'other_budget_path': "budget/path",
        'this_budget_path': "budget/path"
    }

    from ynabdebtsync import api
    from flask import json

    api.flask_app.logger
    tc = api.flask_app.test_client()
    response = tc.post('/api/dropboxbudgetcomparison',
                       data=json.dumps(data),
                       content_type='application/json')
    data = json.loads(response.data)
    assert_equal(len(data["this_missing"]), 0)
    assert_equal(len(data["other_missing"]), 240)
