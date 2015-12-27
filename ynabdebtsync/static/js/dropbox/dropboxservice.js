(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .factory('dropboxService', dropboxService);

    dropboxService.$inject = ['$http'];

    function dropboxService($http) {
        var accessToken = "";
        var service = {
            getAccessToken: getAccessToken,
            getAuthLink: getAuthLink,
            getAllBudgets: getAllBudgets,
            isAuthenticated: isAuthenticated,
            setAccessToken: setAccessToken
        };

        return service;

        function getAccessToken() {
            return accessToken;
        }

        function getAuthLink() {
            return '<a href="https://www.dropbox.com/1/oauth2/authorize?redirect_uri=http%3A%2F%2Flocalhost%3A5000&response_type=token&client_id=uo6kvpwo8rv9bqi">Authenticate with dropbox</a>';
        }

        function getAllBudgets(whose) {
            var request = {
                method: 'POST',
                url: '/api/dropboxbudgets/' + whose,
                data: {
                    access_token: accessToken
                }
            }

            return $http(request)
                .then(function(response) {
                    return response.data;
                });
        }

        function isAuthenticated() {
            return accessToken !== "";
        }

        function setAccessToken(token) {
            accessToken = token;
        }
    }
})();
