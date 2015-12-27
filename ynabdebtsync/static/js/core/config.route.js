(function() {
    'use strict';

    angular
        .module('app.core')
        .run(config);

    config.$inject = ['$state'];

    // This is necessary for ui router's $urlRouterProvider.when rules
    // to be correctly applied on the root ('') state, to redirect the
    // user to a specific state when visiting the root page.
    // It seems if the $state dependency is not injected on application run
    // it cannot enforce the rule added via $urlRouterProvider.
    function config($state) {
    }
})();
