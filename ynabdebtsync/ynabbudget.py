# -*- coding: utf8 -*-

import json
from decimal import Decimal

class YnabBudget:
    """YNAB budget reading."""
    def __init__(self, budget_json):
        """budget_json is the Budget.yfull file's contents."""
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

    def master_categories_to_subcategories(self):
        """Return a dictionary keyed by the budget's master categories. Each
        master category's value is a dictionary of the subcategory names to
        IDs.
        """
        category_hierarchy = {}

        for master_category in self.data["masterCategories"]:
            category_container = {}
            for sub_category in master_category["subCategories"]:
                category_container[sub_category["name"]] = sub_category["entityId"]
            category_hierarchy[master_category["name"]] = category_container

        return category_hierarchy

    def category_id_from_name(self, name):
        """Return the category ID for a given category name, case-insensitive.
        Throws a LookupError if there is no category with the given name.
        """
        for master_category in self.data["masterCategories"]:
            for sub_category in master_category["subCategories"]:
                if sub_category["name"].lower() == name.lower():
                    return sub_category["entityId"]

        raise LookupError("No category with name '{0}' exists in the budget"
                          .format(name))

    def transactions_by_category_name(self, name):
        """Return a list of transactions that are assigned to the given
        category name.
        """
        category_id = self.category_id_from_name(name)

        return self.__all_transactions_by_category_id(category_id)

    def __all_transactions_by_category_id(self,
                                          category_id,
                                          transactions_to_check=None):
        """Recursive method that constructs a list of transactions assigned to
        the given category ID. Subtransactions are also taken into account, by
        passing a transaction's subtransactions in recursive calls via the
        transactions_to_check argument.
        """
        transactions_to_add = []

        # Base case, start with the budget's transactions.
        if transactions_to_check is None:
            transactions_to_check = self.data["transactions"]

        for transaction in transactions_to_check:
            if transaction["categoryId"] == category_id:
                transactions_to_add.append(transaction)
            # Recursive case, check subtransactions. Extend transactions_to_add
            # with the list of subtransactions assigned to the given category,
            # if any.
            if "subTransactions" in transaction:
                transactions_to_add.extend(
                    self.__all_transactions_by_category_id(
                        category_id,
                        transaction["subTransactions"]
                    )
                )

        # Turn into a generator so the results from this method can be iterated
        # over, allowing filtering by e.g. date in log(N) vs log(2N) time
        return transactions_to_add

    def calculate_category_total(self, category_name):
        transactions = self.transactions_by_category_name(category_name)

        running_total = Decimal(0)
        for transaction in transactions:
            running_total += Decimal(transaction["amount"])

        return running_total

class YnabBudgetMalformedError(Exception):
    """Exception raised when the YNAB budget JSON is malformed."""
    def __init__(self, message, inner_message="", budget_json=""):
        super(Exception, self).__init__(message)
        self.message = message
        self.inner_message = inner_message
        self.budget_json = budget_json

class YnabBudgetComparer:
    def __init__(self, this_budget_json, other_budget_json):
        self.this_budget = YnabBudget(this_budget_json)
        self.other_budget = YnabBudget(other_budget_json)

    def categories_are_reconciled(self, this_category_name, other_category_name):
        this_transactions = self.this_budget.transactions_by_category_name(this_category_name)
        other_transactions = self.other_budget.transactions_by_category_name(other_category_name)

        return len(this_transactions) == len(other_transactions)

