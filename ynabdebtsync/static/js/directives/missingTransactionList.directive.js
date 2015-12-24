(function() {
    'use strict';

    angular
        .module('app')
        .directive('missingTransactionList', missingTransactionList);

    function missingTransactionList() {
        return {
            restrict: 'E',
            scope: {
                missingTransactions: '='
            },
            templateUrl: '/static/js/templates/missingTransactionList.template.html'
        };
    }
})();
