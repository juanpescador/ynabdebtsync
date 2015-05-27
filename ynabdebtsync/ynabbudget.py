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

        return self._all_transactions_by_category_id(category_id)

    def _all_transactions_by_category_id(self,
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
                    self._all_transactions_by_category_id(
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

        Due to the ascending order of this_transactions, if the comparison is:
            abs(this_transactions[n]) > abs(other_transactions[n])
        then this_transactions is the one missing transaction(s) from
        other_transactions:

            this_transactions                       other_transactions
            amount  memo                            amount  memo
            $-5     loan money for nachos           $5      borrow money for nachos
         -> $10     borrow money for sandwich    -> $-5     loan money for beer
                                                    $-10    loan money for sandwich

        As seen here, this_transactions[1] amount is $10, while it is $-5
        for other_transactions[1]. other_transactions contains an outflow
        transaction of $-5 but there isn't a matching inflow transaction of $5
        in this_transactions. This is the simplest case: there could be more
        than one inflow transaction of amount $5 missing from this_transactions.

        If the comparison is:
            abs(this_transactions[n]) < abs(other_transactions[n])
        then other_transactions is the one missing transaction(s) from
        this_transactions:

            this_transactions                       other_transactions
            amount  memo                            amount  memo
         -> $-3     loan money for water         -> $-5     loan money for beer
            $5      borrow money for beer           $-10    loan money for sandwich
            $10     borrow money for sandwich

        As seen here, this_transactions[0] amount is $-3, while
        other_transactions[0] is $-5. If we didn't compare the absolute values
        of the amounts, we would incorrectly choose the $-5 transaction as the
        missing one, but we can see it is actually in this_transactions.

        If the comparison is:
            abs(this_transactions[n]) == abs(other_transactions[n])
        then both categories are missing transactions from each other:

            this_transactions                       other_transactions
            amount  memo                            amount  memo
         -> $-3     loan money for water         -> $-3     loan money for juice
            $5      borrow money for beer           $-10    loan money for sandwich
            $10     borrow money for sandwich

        In this case, other_transactions is missing a $3 transaction, borrowing
        money for water, and this_transactions is missing a $3 transaction,
        borrowing money for juice.

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
        ).sort(key=lambda transaction: Decimal(transaction["amount"]))

        # other_transactions amounts are the inverse of this_transactions
        # amounts. Sort in reverse order so the indices of other_transactions
        # match the inverse transaction of this_transactions.
        # E.g. this_transactions = Joe's transactions = $-5, $+2, $+7
        #    other_transactions = Jane's transactions = $+5, $-2, $-7
        other_transactions = self.other_budget.transactions_by_category_name(
            self.other_category_name
        ).sort(key=lambda transaction: Decimal(transaction["amount"]), reverse=True)

        this_missing_transactions = []
        other_missing_transactions = []

        other_iter = iter(other_transactions)
        try:
            other_transaction = other_iter.next()
        except StopIteration:
            # Other transactions was empty, it's missing all of this budget's
            # transactions.
            other_missing_transactions = this_transactions

        # Don't have a handle on this_transactions iterator, so can't call .next()
        # to bump its position. This sentinel is used instead.
        iterations_to_skip = 0
        # Each category's transactions are sorted by amount. Therefore, if the
        # amounts ever differ it is because the category whose current
        # transaction's amount is greater than the other is missing transactions
        # of the smaller amount. The number of transactions missing is the
        # difference of transactions for that amount between the two
        # categories.
        for this_transaction in this_transactions:
            # Skip this iteration if we're bumping this_transactions past any
            # transactions that other_transactions was missing.
            if iterations_to_skip > 0:
                iterations_to_skip -= 1
                continue

            this_amount = Decimal(this_transaction["amount"])
            other_amount = Decimal(other_transaction["amount"])
            # When the amounts don't add up to zero, cancelling each other out,
            # it means there is a discrepancy in transactions.
            if this_amount + other_amount != 0:
                # this_transactions is missing one or more transactions of
                # amount == -other_amount.
                if this_amount > other_amount:
                    missing_transactions = self._get_missing_transactions_of_amount(other_amount)
                    this_missing_transactions.extend(missing_transactions)
                    # Bump other_transactions iterator past the missing transactions.
                    for transaction in missing_transactions:
                        other_transaction = other_iter.next()

                # other_transactions is missing one or more transactions of
                # amount == -other_amount.
                elif abs(this_amount) < abs(other_amount):
                    missing_transactions = self._get_missing_transactions_of_amount(this_amount)
                    other_missing_transactions.extend(missing_transactions)
                    # Set the sentinel to allow bumping this_transactions past
                    # the missing transactions.
                    iterations_to_skip = len(missing_transactions)

                # Transactions are missing from both this_transactions and
                # other_transactions.
                elif abs(this_amount) == abs(other_amount):
                    missing_transactions = self._get_missing_transactions_of_amount(other_amount)
                    this_missing_transactions.extend(missing_transactions)
                    # Bump other_transactions iterator past the missing transactions.
                    for transaction in missing_transactions:
                        other_transaction = other_iter.next()

                    missing_transactions = self._get_missing_transactions_of_amount(this_amount)
                    other_missing_transactions.extend(missing_transactions)
                    # Set the sentinel to allow bumping this_transactions past
                    # the missing transactions.
                    iterations_to_skip = len(missing_transactions)

        # If other_transactions hasn't reached the end, the remaining transactions
        # are missing from this_transactions.
        for other_transaction in other_transactions:
            this_missing_transactions.append(other_transaction)

        return this_missing_transactions, other_missing_transactions

    def _get_missing_transactions_of_amount(self, amount):
        """For each budget's transactions, compiles a list of those whose
        amount equals the given amount argument. One of the lists is a superset
        of the other list and this method returns the relative complement, i.e.
        of the list with more transactions, those that are missing from the
        list with less transactions."""

        this_transactions = self.this_budget.transactions_by_category_name(
            self.this_category_name
        )
        this_transactions = [txn for txn in this_transactions
                             if abs(Decimal(txn["amount"])) == abs(amount)]
        this_transactions.sort(key=lambda txn: txn["date"])

        other_transactions = self.other_budget.transactions_by_category_name(
            self.other_category_name
        )
        other_transactions = [txn for txn in other_transactions
                              if abs(Decimal(txn["amount"])) == abs(amount)]
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
            raise ValueError("There are no missing transactions. Both budget categories contain the same number of transactions ({0}) for amount {1}".format(len(this_transactions), amount))

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
            return this_transactions

        # superset_transactions is always longer than subset_transactions, and
        # is always bumped in tandem with subset_transactions, so it's
        # guaranteed that subset_transaction will be done before
        # superset_transaction ever is.
        while subset_transaction is not done:
            # Found a missing transaction, add it and check the next
            # subset_transaction.
            if superset_transaction["date"] != subset_transaction["date"]:
                missing_transactions.append(superset_transaction)
                subset_transaction = next(subset_transactions_iter, done)
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

        # If any superset_transactions are left, add them to
        # missing_transactions.
        while superset_transaction is not done:
            missing_transactions.append(superset_transaction)
            superset_transaction = next(superset_transactions_iter, done)

        target_missing_transactions_len = len(superset_transactions) - len(subset_transactions)

        if len(missing_transactions) != target_missing_transactions_len:
            raise ValueError("Cannot reliably detect missing transactions. This can happen if existing transaction dates don't match between the budgets.")

        return missing_transactions

