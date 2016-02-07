(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .controller('DropboxController', DropboxController);

    DropboxController.$inject = ['$location', 'dropboxService'];

    function DropboxController($location, dropboxService) {
        var vm = this;

        vm.comparisonStartDate = "";
        vm.getBudgets = getBudgets;
        vm.getAuthLink = getAuthLink;
        vm.isAuthenticated = isAuthenticated;
        vm.logOut = logOut;
        vm.otherBudgetPath = "";
        vm.otherBudgets = [];
        vm.otherTargetCategory = "";
        vm.otherMissingTransactions = [];
        vm.otherMissingPayees = {};
        vm.thisBudgetPath = "";
        vm.thisBudgets = [];
        vm.thisTargetCategory = "";
        vm.thisMissingTransactions = [];
        vm.thisMissingPayees = {};

        vm.compare = compare;
        vm.comparisonAttempted = false;
        vm.comparisonExecuting = false;
        vm.comparisonErrors = [];
        vm.sortTransactionsByDateAsc = sortTransactionsByDateAsc;

        vm.gettingOwnBudgets = false;
        vm.gettingTheirBudgets = false;

        function getBudgets(whose) {
            var destinationBudget = null;
            switch (whose) {
                case 'mine':
                    vm.gettingOwnBudgets = true;
                    break;
                case 'theirs':
                    vm.gettingTheirBudgets = true;
                    break;
                default:
                    console.log("[DropboxController]: " + whose + " is not a valid value for whose")
            }
            return dropboxService.getAllBudgets(whose)
                .then(function(data) {
                    switch (whose) {
                        case 'mine':
                            vm.gettingOwnBudgets = false;
                            vm.thisBudgets = data;
                            break;
                        case 'theirs':
                            vm.gettingTheirBudgets = false;
                            vm.otherBudgets = data;
                            break;
                        default:
                            console.log("[DropboxController]: " + whose + " is not a valid value for whose")
                    }
                    return destinationBudget;
                }, function(response) {
                    vm.gettingOwnBudgets = false;
                    vm.gettingTheirBudgets = false;
                });
        }

        function isAuthenticated() {
            return dropboxService.isAuthenticated();
        }

        function getAuthLink() {
            return dropboxService.getAuthLink();
        }

        function logOut() {
            dropboxService.setAccessToken('');
        }

        function compare() {
            vm.comparisonExecuting = true;

            dropboxService.compare(vm.thisBudgetPath, vm.otherBudgetPath)
                .then(function(response) {
                    vm.thisMissingTransactions = response.data.this_missing;
                    vm.thisMissingTransactions.sort(vm.sortTransactionsByDateAsc);

                    // This budget's missing transactions come from other
                    // budget, so the payees are also from other budget.
                    vm.thisMissingPayees = response.data.other_payees;

                    vm.otherMissingTransactions = response.data.other_missing;
                    vm.otherMissingTransactions.sort(vm.sortTransactionsByDateAsc);

                    // Other budget's missing transactions come from this
                    // budget, so the payees are also from this budget.
                    vm.otherMissingPayees = response.data.this_payees;

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
