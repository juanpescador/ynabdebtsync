(function() {
    'use strict';

    angular
    .module('app.layout')
    .config(layoutConfig);

    layoutConfig.$inject = ['$stateProvider', '$urlRouterProvider'];

    function layoutConfig($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('home', {
                url: "/",
                templateUrl: "/static/js/layout/shell.html"
            });
    }
})();
