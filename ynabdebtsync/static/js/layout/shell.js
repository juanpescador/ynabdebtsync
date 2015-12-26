(function() {
    'use strict';

    angular
        .module('app.layout')
        .controller('Shell', Shell);

    Shell.$inject = ['$state'];

    function Shell($state) {
        var vm = this;
        vm.title = 'Shell';
        vm.navRoutes = [];

        var routes = $state.get();

        activate();

        ////////////////

        function activate() {
            getNavRoutes();
        }

        function getNavRoutes() {
            vm.navRoutes = routes.filter(function(route) {
                return route.data && route.data.nav;
            }).sort(function(a, b) {
                return a.data.nav - b.data.nav;
            });
        }
    }
})();
