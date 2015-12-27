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
            })
            // Dropbox does not allow fragments in the OAuth2 call's redirect URI,
            // so we will receive the access token as its own route. Adapted from
            // http://stackoverflow.com/a/28451097
            .state('access_token', {
                url: '/access_token={accessToken}&token_type={tokenType}&uid={uid}',
                template: '',
                controller: function($stateParams, $state, dropboxService) {
                    var token = $stateParams.accessToken;
                    dropboxService.setAccessToken(token);
                    $state.go('dropboxbudgets');
                },
                resolve: {
                    $state: '$state',
                    dropboxService: 'dropboxService'
                }
            });
    }
})();
