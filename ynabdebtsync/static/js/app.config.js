(function () {
    'use strict';

    angular
        .module('app')
        .config(interpolateProviderConfig)
        .config(locationProviderConfig);

    interpolateProviderConfig.$inject = ['$interpolateProvider', '$locationProvider'];

    function interpolateProviderConfig($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }

    function locationProviderConfig($locationProvider) {
        return $locationProvider.html5Mode(true);
    }

})();
