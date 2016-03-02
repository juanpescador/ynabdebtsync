(function() {
    'use strict';

    angular
        .module('app.widgets')
        .directive('missingTransactionList', missingTransactionList);

    function missingTransactionList() {
        return {
            restrict: 'E',
            scope: {
                missingTransactions: '=',
                payees: '='
            },
            templateUrl: '/static/js/widgets/missingTransactionList.html',
            controller: MissingTransactionController,
            controllerAs: 'vm',
            bindToController: true
        };
    }

    MissingTransactionController.$inject = [];

    function MissingTransactionController() {
        var vm = this;
        vm.downloadMissingTransactions = downloadMissingTransactions;
        vm.missingTransactionsTotal = missingTransactionsTotal;

        function downloadMissingTransactions() {
            // Adapted from http://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
            // YNAB CSV definition: http://classic.youneedabudget.com/support/article/csv-file-importing
            var csvHeaders = ["Date", "Payee", "Category", "Memo", "Outflow", "Inflow"];
            surroundItemsWithEscapedQuotes(csvHeaders);
            var csvRecords = [csvHeaders.join(",")];

            vm.missingTransactions.forEach(function (txn, index) {
                // The missing transactions come from the opposite budget, so
                // an inflow there is an outflow here.
                // YNAB expects a positive number for the outflow.
                // Only one of Inflow or Outflow can be set.
                var inflow = txn.amount < 0 ? -txn.amount : "";
                var outflow = inflow === "" ? txn.amount : "";
                var payeeName = vm.payees[txn.payeeId];
                // If it's an inflow, the payee is the budget's owner (Self).
                // Otherwise, it's the creditor (payeeName).
                var missingTransactionFields = [
                    txn.date,
                    inflow !== "" ? "Self" : payeeName,
                    "",
                    txn.memo + " (Added by YNAB Debt Sync)",
                    outflow,
                    inflow
                ];
                surroundItemsWithEscapedQuotes(missingTransactionFields);
                csvRecords.push(missingTransactionFields.join(","));

                // If the missing transaction was an inflow, we need to "spend"
                // that money to keep our YNAB balances correct.
                if (inflow !== "") {
                    // This transaction spends the money borrowed, so it is
                    // accounted for in the budget. Outflow and inflow are
                    // therefore swapped.
                    var budgetableTransaction = [
                        txn.date,
                        payeeName,
                        "",
                        txn.memo + " (Added by YNAB Debt Sync)",
                        inflow,
                        outflow
                    ];
                    surroundItemsWithEscapedQuotes(budgetableTransaction);
                    csvRecords.push(budgetableTransaction.join(","));
                }
            });

            var csvContent = "data:text/csv;charset=utf-8,";
            csvContent += csvRecords.join("\n");

            var encodedCsvUri = encodeURI(csvContent);
            window.open(encodedCsvUri);
        }

        function missingTransactionsTotal() {
            var total = 0;

            // missingTransactions is undefined until the comparison is
            // complete, but the $digest cycle calls this as from page load.
            if (typeof vm.missingTransactions !== "undefined") {
                vm.missingTransactions.forEach(function(txn, index) {
                    total += txn.amount;
                });
            }

            return total;
        };

        // Used to wrap CSV fields with quotes, so any commas contained in the
        // field's value aren't incorrectly parsed as a field separator.
        function surroundItemsWithEscapedQuotes(array) {
            array.forEach(function (item, index) {
                array[index] = "\"" + item + "\"";
            });
        }
    }
})();
