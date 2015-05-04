# -*- coding: utf8 -*-

import json

class YnabBudget:
    def __init__(self, budget_json):
        if budget_json is None:
            raise ValueError("Budget JSON is None")
        if budget_json == "":
            raise ValueError("Budget JSON is empty")
        try:
            self.data = json.loads(budget_json)
        except ValueError as e:
            raise YnabBudgetMalformedError("Budget JSON is malformed",
                                           inner_message=e,
                                           budget_json=budget_json)

class YnabBudgetMalformedError(Exception):
    """Exception raised when the YNAB budget JSON is malformed."""
    def __init__(self, message, inner_message="", budget_json=""):
        super(Exception, self).__init__(message)
        self.message = message
        self.inner_message = inner_message
        self.budget_json = budget_json
