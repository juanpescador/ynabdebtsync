# -*- coding: utf8 -*-

import json

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
        category_id = self.category_id_from_name(name)

        return self.__all_transactions_by_category_id(category_id)

    def __all_transactions_by_category_id(self, category_id, transactions_to_check=None):
        """Method to construct a list of transactions assigned to the given
        category ID. Subtransactions are also taken into account, by passing
        a transaction's subtransactions via the transactions_to_check argument
        in recursive calls.
        """
        transactions_to_add = []

        # Base case, check all transactions.
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

        return transactions_to_add

class YnabBudgetMalformedError(Exception):
    """Exception raised when the YNAB budget JSON is malformed."""
    def __init__(self, message, inner_message="", budget_json=""):
        super(Exception, self).__init__(message)
        self.message = message
        self.inner_message = inner_message
        self.budget_json = budget_json
