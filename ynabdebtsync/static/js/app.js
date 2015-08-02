var ynabDebtSync = angular.module('ynabDebtSync', []);
ynabDebtSync.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);
