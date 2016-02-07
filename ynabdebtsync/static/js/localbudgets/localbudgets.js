(function() {
    'use strict';

    angular
        .module('app.localbudgets')
        .controller('LocalBudgets', LocalBudgets);

    LocalBudgets.$inject = ['budgetComparerService'];

    function LocalBudgets(budgetComparerService) {
        var vm = this;

        vm.compareBudgets = compareBudgets;
        vm.comparisonAttempted = false;
        vm.comparisonExecuting = false;
        vm.comparisonErrors = [];
        vm.otherTargetCategory = "";
        vm.sortTransactionsByDateAsc = sortTransactionsByDateAsc;
        vm.thisTargetCategory = "";

        function compareBudgets() {
            vm.comparisonExecuting = true;

            var formData = new FormData();
            formData.append('this_budget', vm.thisBudget);
            formData.append('this_target_category', vm.thisTargetCategory);
            formData.append('other_budget', vm.otherBudget);
            formData.append('other_target_category', vm.otherTargetCategory);
            formData.append('start_date', vm.startDate);

            var missingTransactions = budgetComparerService.compare(formData)
                .then(function(response) {
                    vm.thisMissingTransactions = response.data.this_missing;
                    vm.thisMissingTransactions.sort(vm.sortTransactionsByDateAsc);

                    vm.otherMissingTransactions = response.data.other_missing;
                    vm.otherMissingTransactions.sort(vm.sortTransactionsByDateAsc);

                    vm.comparisonAttempted = true;
                    vm.comparisonExecuting = false;
                }, function(response){
                    vm.comparisonExecuting = false;
                    vm.comparisonErrors.push(response);
                });

        }

        function sortTransactionsByDateAsc(a, b) {
            return new Date(a.date).getTime() - new Date(b.date).getTime();
        }
    }
})();
