# -*- coding: utf8 -*-

import json

class YnabBudget:
    def __init__(self, budget_json):
        self.data = json.loads(budget_json)
