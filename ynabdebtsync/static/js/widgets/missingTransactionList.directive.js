(function() {
    'use strict';

    angular
        .module('app.widgets')
        .directive('missingTransactionList', missingTransactionList);

    function missingTransactionList() {
        return {
            restrict: 'E',
            scope: {
                missingTransactions: '='
            },
            templateUrl: '/static/js/widgets/missingTransactionList.template.html'
        };
    }
})();
