(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .config(dropboxbudgetsConfig);

    dropboxbudgetsConfig.$inject = ['$stateProvider'];

    function dropboxbudgetsConfig($stateProvider) {
        $stateProvider
            .state('dropboxbudgets', {
                url: "/dropboxbudgets",
                templateUrl: "/static/js/dropbox/dropbox.html",
                data: {
                    nav: 2,
                    content: '<i class="dropbox icon"></i>Dropbox Budgets'
                },
                controller: 'DropboxController',
                controllerAs: 'vm'
            });
    }
})();
