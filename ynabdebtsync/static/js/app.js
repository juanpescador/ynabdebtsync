var ynabDebtSync = angular.module('ynabDebtSync', []);
ynabDebtSync.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);
ynabDebtSync.controller('budgetComparer', ['$scope',
  function($scope) {
    $scope.greeting = { text: 'Hello' };
}]);
