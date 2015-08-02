ynabDebtSync.controller('budgetUploadCtrl', ['$scope', 'budgetComparerService', function($scope, budgetComparerService){
    $scope.compareBudgets = function() {
        var formData = new FormData();
        formData.append('this_budget', $scope.thisBudget);
        formData.append('this_target_category', $scope.thisTargetCategory);
        formData.append('other_budget', $scope.otherBudget);
        formData.append('other_target_category', $scope.otherTargetCategory);
        formData.append('start_date', $scope.startDate);

        var missingTransactions = budgetComparerService.compare(formData)
            .then(function(response) {
                $scope.thisMissingTransactions = missingTransactions.this_missing;
                $scope.otherMissingTransactions = missingTransactions.other_missing;
            });
    };
}]);
