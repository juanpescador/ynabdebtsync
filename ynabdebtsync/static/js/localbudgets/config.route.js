(function() {
    'use strict';

    angular
        .module('app.localbudgets')
        .config(localbudgetsConfig);

    localbudgetsConfig.$inject = ['$stateProvider', '$urlRouterProvider'];

    function localbudgetsConfig($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/localbudgets');

        $stateProvider
            .state('localbudgets', {
                url: "/localbudgets",
                templateUrl: "/static/js/localbudgets/localbudgets.html",
                data: {
                    nav: 1,
                    content: '<i class="disk outline icon"></i>Local Budgets'
                },
                controller: 'LocalBudgets',
                controllerAs: 'vm'
            });
    }
})();
