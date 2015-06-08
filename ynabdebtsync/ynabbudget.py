# -*- coding: utf8 -*-

import json
import re

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

    def transactions_by_category_name(self, name, filters=None):
        """Return a list of transactions that are assigned to the given
        category name.
        """
        category_id = self.category_id_from_name(name)

        return self._transactions_from_category_id(category_id, filters=filters)

    def _transactions_from_category_id(self,
                                        category_id,
                                        transactions_to_check=None,
                                        filters=None):
        """Constructs a list of transactions assigned to the given category ID.
        Subtransactions are also taken into account, by passing a transaction's
        subtransactions in recursive calls via the transactions_to_check
        argument.
        """
        transactions_to_add = []

        # Base case, start with the budget's transactions.
        if transactions_to_check is None:
            transactions_to_check = self.data["transactions"]

        for transaction in transactions_to_check:
            if transaction["categoryId"] == category_id:
                if filters is None:
                    transactions_to_add.append(transaction)
                elif all([filter_(transaction) for filter_ in filters]):
                    transactions_to_add.append(transaction)
            # Recursive case, check subtransactions. Extend transactions_to_add
            # with the list of subtransactions assigned to the given category,
            # if any.
            if "subTransactions" in transaction:
                # Subtransactions don't have their own date, add the parent
                # transaction's date.
                for subtransaction in transaction["subTransactions"]:
                    subtransaction["date"] = transaction["date"]
                    # If the subtransaction already has a memo leave it as is.
                    if "memo" not in subtransaction and "memo" in transaction:
                        subtransaction["memo"] = transaction["memo"]
                transactions_to_add.extend(
                    self._transactions_from_category_id(
                        category_id,
                        transaction["subTransactions"],
                        filters
                    )
                )

        # Turn into a generator so the results from this method can be iterated
        # over, allowing filtering by e.g. date in log(N) vs log(2N) time
        return transactions_to_add

    def filter_category_transactions_by_date(self, category_name, date):
        """Retrieves transactions from a category that match a given date string, in
        yyyy[-mm[-dd]] format. The month and day are optional, so it is possible to
        filter by year; year and month; or year, month and date."""
        filters = []
        date_filter = lambda txn: re.match(date, txn["date"]) is not None
        filters.append(date_filter)

        return self.transactions_by_category_name(category_name, filters)

    def calculate_category_total(self, category_name):
        transactions = self.transactions_by_category_name(category_name)

        running_total = 0
        for transaction in transactions:
            running_total += transaction["amount"]

        return running_total

class YnabBudgetMalformedError(Exception):
    """Exception raised when the YNAB budget JSON is malformed."""
    def __init__(self, message, inner_message="", budget_json=""):
        super(Exception, self).__init__(message)
        self.message = message
        self.inner_message = inner_message
        self.budget_json = budget_json

class YnabBudgetComparerValueError(ValueError):
    """Raise this when there are no missing transactions."""

class YnabBudgetComparer:
    def __init__(self, this_budget_json, this_category_name, other_budget_json, other_category_name):
        self.this_budget = YnabBudget(this_budget_json)
        self.this_category_name = this_category_name
        self.other_budget = YnabBudget(other_budget_json)
        self.other_category_name = other_category_name

    def categories_are_reconciled(self):
        return abs(self.this_budget.calculate_category_total(self.this_category_name)) == abs(self.other_budget.calculate_category_total(self.other_category_name))

    def get_missing_transactions(self):
        """Gets the transactions missing from each budget.

        To identify which transactions are missing, both transactions lists are
        sorted by transaction amount. "this" category's in ascending order,
        "other" category's in descending order. An inflow in this_transactions
        will be an outflow in other_transactions, so if both categories have
        the same transactions, this_transactions[n] will correspond to
        other_transactions[n]. One will be an inflow, i.e. positive amount and
        the other will be an outflow, i.e. negative amount.

        Matching transactions' amounts will add up to zero, as the inflow will
        cancel out the outflow. If the amounts for a given
        (this_transactions[n], other_transactions[n]) pair do not add up to
        zero, it means that one, or both, of the categories is missing one, or
        more, transactions.

        There are four main cases when the transactions don't match, based on
        the signs of this_amount and other_amount:
            A. this_amount < 0, other_amount > 0
            B. this_amount < 0, other_amount < 0
            C. this_amount > 0, other_amount > 0
            D. this_amount > 0, other_amount < 0

        Cases A and D have a further two cases each:
            1. abs(this_amount) > abs(other_amount)
            2. abs(this_amount) < abs(other_amount)

        The third case, abs(this_amount) == abs(other_amount) is impossible, as
        the opposing signs mean that, if the absolute values are equal, the actual
        values cancel each other out. E.g. this_amount = -3, other_amount = 3
            abs(-3) == abs(3)
        but
            -3 + 3 == 0
        so the transactions cancel each other out.

        Cases B and C don't distinguish between the absolute values of their
        transactions: the missing transaction is always from the same budget.
        For case B, the missing transaction is always the one from this_budget.
        For case C, the missing transaction is always the one from
        other_budget.

        An example of case A follows, which should be enough to construct the
        rest of cases.

        this_amount = -10
        other_amount = 8
        abs(this_amount) > abs(other_amount)

            this_transactions                       other_transactions
            amount  memo                            amount  memo
         -> $-10    loan money for nachos        -> $8      loan money for beer
            $8      borrow money for beer           $-10    loan money for sandwich
            $10     borrow money for sandwich

        In this case, the two transactions marked with a -> don't cancel each
        other out. To cancel each other out, other_transactions needs a
        transaction of amount $10. Because other_transactions is in descending
        order, if it existed, that transaction would be above the $8
        transaction, so we know for certain that the missing transaction out of
        the pair [$-10, $8] is the one from this_budget, i.e. the $-10
        transaction (which, when added to other_budget would become a $10 to
        cancel out the amounts).

        We don't know anything about the $8 dollar transaction from
        other_transactions yet, the algorithm only considers one pair of
        transactions at a time. In this example, the additional transactions
        have been included to give context.

        The rest of cases can be derived in a similar fashion.

        Once a divergence in amounts is identified, transactions of the
        identified amount are compared to the other category's transactions of
        the inverse amount. If the missing transaction's amount is $-5, i.e. it
        was an outflow, all outflows of $-5 from that category are compared to
        all inflows of $5 from the other category to find candidate missing
        transactions.

        While just adding the number of missing transactions would suffice to
        bring the two categories into sync, it is much more useful to the user
        if they can know what transactions were missing, e.g. when did the
        transaction take place, and what was it for? Missing transaction
        candidates are determined by matching the subset of transactions for a
        given pair of amounts (inflows in one category, outflows in the other)
        by date. If more than one missing transaction occurred on the same
        date, the first one is chosen as a candidate, for simplicity. The date
        of missing transactions is deemed important, while the memo (what it
        was for) is a nice-have.
        """
        this_transactions = self.this_budget.transactions_by_category_name(
            self.this_category_name
        )
        this_transactions.sort(key=lambda transaction: transaction["amount"])

        # other_transactions amounts are the inverse of this_transactions
        # amounts. Sort in reverse order so the indices of other_transactions
        # match the inverse transaction of this_transactions.
        # E.g. this_transactions = Joe's transactions = $-5, $+2, $+7
        #    other_transactions = Jane's transactions = $+5, $-2, $-7
        other_transactions = self.other_budget.transactions_by_category_name(
            self.other_category_name
        )
        other_transactions.sort(key=lambda transaction: transaction["amount"],
                                reverse=True)

        this_missing_transactions = []
        other_missing_transactions = []

        # Sentinel to know when iteration has finished.
        done = object()

        other_iter = iter(other_transactions)
        other_transaction = next(other_iter, done)
        if other_transaction is done:
            # Other transactions was empty, other_budget is missing all of this
            # budget's transactions, and this_budget is not missing any.
            other_missing_transactions = this_transactions
            return [], other_missing_transactions

        this_iter = iter(this_transactions)
        this_transaction = next(this_iter, done)

        # Each category's transactions are sorted by amount. Therefore, if the
        # amounts ever differ it is because the category whose current
        # transaction's amount is greater than the other is missing transactions
        # of the smaller amount. The number of transactions missing is the
        # difference of transactions for that amount between the two
        # categories.
        while this_transaction is not done and other_transaction is not done:
            this_amount = this_transaction["amount"]
            other_amount = other_transaction["amount"]
            # When the amounts aren't the inverse of each other they don't
            # cancel each other out, meaning there is a discrepancy in
            # transactions.
            if this_amount != -other_amount:
                if (this_amount < 0 and other_amount > 0):
                    if abs(this_amount) > abs(other_amount):
                        missing_transactions = self._get_this_budget_transactions_missing_from_other_budget(this_amount)
                        other_missing_transactions.extend(missing_transactions)
                        for transaction in missing_transactions:
                            this_transaction = next(this_iter, done)

                    # Don't need to check for abs(this_amount) == abs(other_amount).
                    # Due to this_amount being negative and other_amount positive, if
                    # they are equal it means they are the inverse of each other.
                    else:
                        missing_transactions = self._get_other_budget_transactions_missing_from_this_budget(other_amount)
                        this_missing_transactions.extend(missing_transactions)
                        for transaction in missing_transactions:
                            other_transaction = next(other_iter, done)

                elif (this_amount < 0 and other_amount < 0):
                    missing_transactions = self._get_this_budget_transactions_missing_from_other_budget(this_amount)
                    other_missing_transactions.extend(missing_transactions)
                    for transaction in missing_transactions:
                        this_transaction = next(this_iter, done)

                elif (this_amount > 0 and other_amount > 0):
                    missing_transactions = self._get_other_budget_transactions_missing_from_this_budget(other_amount)
                    this_missing_transactions.extend(missing_transactions)
                    for transaction in missing_transactions:
                        other_transaction = next(other_iter, done)

                elif (this_amount > 0 and other_amount < 0):
                    if abs(this_amount) > abs(other_amount):
                        missing_transactions = self._get_other_budget_transactions_missing_from_this_budget(other_amount)
                        this_missing_transactions.extend(missing_transactions)
                        for transaction in missing_transactions:
                            other_transaction = next(other_iter, done)
                    else:
                        missing_transactions = self._get_this_budget_transactions_missing_from_other_budget(this_amount)
                        other_missing_transactions.extend(missing_transactions)
                        for transaction in missing_transactions:
                            this_transaction = next(this_iter, done)


            # Amounts cancel each other out, representing a matching inflow
            # and outflow. Check the next pair.
            else:
                this_transaction = next(this_iter, done)
                other_transaction = next(other_iter, done)

        # If this_transactions hasn't reached the end, the remaining transactions
        # are missing from other_transactions.
        while this_transaction is not done:
            other_missing_transactions.append(this_transaction)
            this_transaction = next(this_iter, done)
        # If other_transactions hasn't reached the end, the remaining transactions
        # are missing from this_transactions.
        while other_transaction is not done:
            this_missing_transactions.append(other_transaction)
            other_transaction = next(other_iter, done)

        return this_missing_transactions, other_missing_transactions

    def _get_missing_transactions_of_amount(self, this_amount):
        """Gets the missing pair transactions for a given amount. A pair
        transaction is a one that cancels out the transaction for the given
        amount. E.g. if the amount is 5 (an inflow), its pair transaction in
        the other budget is of amount -5, i.e. an outflow. this_amount gives
        the cardinality of the transactions to look for, i.e. are we checking
        for outflows from this_budget compared to inflows for other_budget, or
        vice versa?

        For each budget's transactions, compiles a list of pair transactions
        for the given amount argument. One of the lists is a superset of the
        other list and this method returns the relative complement, i.e. of the
        list with more transactions, those that are missing from the list that
        has less transactions."""

        this_transactions = self.this_budget.transactions_by_category_name(
            self.this_category_name
        )
        this_transactions = [txn for txn in this_transactions
                             if txn["amount"] == this_amount]
        this_transactions.sort(key=lambda txn: txn["date"])

        other_transactions = self.other_budget.transactions_by_category_name(
            self.other_category_name
        )
        other_transactions = [txn for txn in other_transactions
                              if txn["amount"] == -this_amount]
        other_transactions.sort(key=lambda txn: txn["date"])

        missing_transactions = []

        # The superset can be either this budget's category's transactions or
        # other budget's category's transactions, we only know at runtime.
        if len(this_transactions) > len(other_transactions):
            superset_transactions = this_transactions
            subset_transactions = other_transactions
        elif len(this_transactions) < len(other_transactions):
            superset_transactions = other_transactions
            subset_transactions = this_transactions
        elif len(this_transactions) == len(other_transactions):
            raise YnabBudgetComparerValueError("There are no missing transactions. Both budget categories contain the same number of transactions ({}) for this_amount = {} and other_amount = {}".format(len(this_transactions), this_amount, -this_amount))

        missing_transactions_target_count = len(superset_transactions) - len(subset_transactions)

        # Sentinel to know when iteration has ended.
        done = object()

        superset_transactions_iter = iter(superset_transactions)
        # Superset is guaranteed to have at least one item. From the previous
        # comparisons to determine if this_transactions or other_transactions
        # is the superset, the only case where it could be empty is if both
        # this_transactions and other_transactions were empty, but then a
        # ValueError is raised and execution is stopped.
        superset_transaction = next(superset_transactions_iter)

        subset_transactions_iter = iter(subset_transactions)
        subset_transaction = next(subset_transactions_iter, done)
        if subset_transaction is done:
            # The subset is empty and is missing all of superset's transactions.
            return superset_transactions

        while (superset_transaction is not done
               and subset_transaction is not done
               and len(missing_transactions) < missing_transactions_target_count):
            # Subset is missing the current superset transaction. Add it and
            # check the next superset_transaction.
            if superset_transaction["date"] != subset_transaction["date"]:
                missing_transactions.append(superset_transaction)
                superset_transaction = next(superset_transactions_iter, done)
            # Transactions match up, check the next pair. This is a naïve
            # approach. If there are multiple transactions on the same date,
            # the order between superset and subset might not be the same.
            # Further, if one of the missing transactions is on the day where
            # there are multiple transactions, due to ordering, we might choose
            # the wrong transaction as candidate. While the amount will be
            # correct, the memo will be for another transaction and may confuse
            # the user.
            # TODO fuzzy compare memos for similar content?
            else:
                superset_transaction = next(superset_transactions_iter, done)
                subset_transaction = next(subset_transactions_iter, done)

        # Skip current superset_transaction if the last iteration was a missing
        # transaction and it was already added.
        if (superset_transaction is not done) and (
            len(missing_transactions) > 0
            and
            superset_transaction is missing_transactions[-1]
        ):
            superset_transaction = next(superset_transactions, done)

        # Only add enough superset_transactions to pad missing_transactions
        # to the right amount. Dates between super and subset mismatch, so
        # the missing transactions returned aren't the best quality, but serve
        # to reconcile the budgets.
        # TODO raise an error so the caller can decide how to resolve the issue.
        while (superset_transaction is not done
               and len(missing_transactions) < missing_transactions_target_count):
            missing_transactions.append(superset_transaction)
            superset_transaction = next(superset_transactions_iter, done)

        return missing_transactions

    def _get_this_budget_transactions_missing_from_other_budget(self, this_amount):
        return self._get_missing_transactions_of_amount(this_amount)

    def _get_other_budget_transactions_missing_from_this_budget(self, other_amount):
        this_amount = -other_amount
        return self._get_missing_transactions_of_amount(this_amount)
