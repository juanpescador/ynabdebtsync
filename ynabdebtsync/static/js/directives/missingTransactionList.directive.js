ynabDebtSync.directive('missingTransactionList', function(){
    return {
        restrict: 'E',
        scope: {
            missingTransactions: '='
        },
        templateUrl: '/static/js/templates/missingTransactionList.template.html'
    };
});
