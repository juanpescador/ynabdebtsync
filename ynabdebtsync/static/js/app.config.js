(function () {
    'use strict';

    angular
        .module('app')
        .config(interpolateProviderConfig);

    interpolateProviderConfig.$inject = ['$interpolateProvider'];

    function interpolateProviderConfig($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }

})();
