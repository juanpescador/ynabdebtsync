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
            templateUrl: '/static/js/widgets/missingTransactionList.html'
        };
    }
})();
