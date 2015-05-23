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
        return abs(self.this_budget.calculate_category_total(this_category_name)) == abs(self.other_budget.calculate_category_total(other_category_name))

    def get_missing_transactions(self, this_category_name, other_category_name):
        """Gets the transactions missing from each budget.

        To identify which transactions are missing, both transactions lists are
        sorted by transaction amount. "this" category's in ascending order,
        "other" category's in descending order. An inflow in this_transactions
        will be an outflow in other_transactions, so if both categories have
        the same transactions, this_transactions[n] will correspond to
        other_transactions[n]. One will be an inflow, i.e. positive amount and
        the other will be an outflow, i.e. negative amount.

        As soon as the amount for a given (this_transactions[n],
        other_transactions[n]) pair is not equal, it means that one of the
        categories is missing one or more transactions. Due to the ascending
        order of this_transactions, if the difference is
        this_transactions[n] > other_transactions[n], this_category is the one
        missing transaction(s) from other_category:

            this_transactions                       other_transactions
            amount  memo                            amount  memo
            $5      loan money for beer             $-5     borrow money for beer
         -> $10     loan money for sandwich      -> $5      loan money for nachos
                                                    $-10    borrow money for sandwich

        As seen here, this_transactions current amount is $10, while it is $5
        for other_transactions, because other_transactions contains a
        transaction for $5 which is missing from this_transactions. This is the
        simplest case: there could be more than one transaction of amount $5
        missing from this_transactions.

        Conversely, if the difference is
        this_transactions[n] < other_transactions[n], other_transactions is the
        one missing transaction(s) from this_category.
        """
        this_transactions = self.this_budget.transactions_by_category_name(this_category_name).sort(key=lambda transaction: Decimal(transaction["amount"]))
        # other_transactions amounts are the inverse of this_transactions
        # amounts. Sort in reverse order so the indices of other_transactions
        # match the inverse transaction of this_transactions.
        # E.g. this_transactions = Joe's transactions = $-5, $+2, $+7
        #    other_transactions = Jane's transactions = $+5, $-2, $-7
        other_transactions = self.other_budget.transactions_by_category_name(other_category_name).sort(key=lambda transaction: Decimal(transaction["amount"]), reverse=True)

        this_missing_transactions = []
        other_missing_transactions = []

        other_iter = iter(other_transactions)
        try:
            other_transaction = other_iter.next()
        except StopIteration:
            # Other transactions was empty, it's missing all of this budget's
            # transactions.
            other_missing_transactions = this_transactions


        # Each category's transactions are sorted by amount. Therefore, if the
        # amounts ever differ it is because the category whose current
        # transaction's amount is greater than the other is missing transactions
        # of the smaller amount. The number of transactions missing is the
        # difference of transactions for that amount between the two
        # categories.
        for this_transaction in this_transactions:
            this_amount = Decimal(this_transaction["amount"])
            other_amount = Decimal(other_transaction["amount"])
            # this_transactions is missing one or more transactions of
            # amount == other_amount.
            if this_amount > other_amount:
                this_missing_transactions.extend(
                    self.get_missing_transactions_of_amount(other_amount,
                                                            this_transactions,
                                                            other_transactions)
                )


        # If other_transactions hasn't reached the end, they're missing from
        # this_transactions.
        for other_transaction in other_transactions:
            this_missing_transactions.append(other_transaction)

        return {"this_missing_transactions": this_missing_transactions,
                "other_missing_transactions": other_missing_transactions}
