ynabDebtSync.controller('budgetUploadCtrl', ['$scope', 'budgetComparerService', function($scope, budgetComparerService){
    $scope.comparisonAttempted = false;
    $scope.comparisonExecuting = false;
    $scope.comparisonErrors = [];

    $scope.compareBudgets = function() {
        $scope.comparisonExecuting = true;

        var formData = new FormData();
        formData.append('this_budget', $scope.thisBudget);
        formData.append('this_target_category', $scope.thisTargetCategory);
        formData.append('other_budget', $scope.otherBudget);
        formData.append('other_target_category', $scope.otherTargetCategory);
        formData.append('start_date', $scope.startDate);

        var missingTransactions = budgetComparerService.compare(formData)
            .then(function(response) {
                $scope.thisMissingTransactions = response.data.this_missing;
                $scope.otherMissingTransactions = response.data.other_missing;
                $scope.comparisonAttempted = true;
                $scope.comparisonExecuting = false;
            }, function(response){
                $scope.comparisonExecuting = false;
                $scope.comparisonErrors.push(response);
            });
    };
}]);
