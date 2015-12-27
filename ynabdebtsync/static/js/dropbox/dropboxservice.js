(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .factory('dropboxService', dropboxService);

    dropboxService.$inject = ['$http', '$location'];

    function dropboxService($http, $location) {
        var accessToken = "";
        var service = {
            getAccessToken: getAccessToken,
            getAuthLink: getAuthLink,
            getAllBudgets: getAllBudgets,
            isAuthenticated: isAuthenticated,
            setAccessToken: setAccessToken,
            compare: compare
        };

        return service;

        function getAccessToken() {
            return accessToken;
        }

        function getAuthLink() {
            var redirectUri = $location.protocol() + '://' + $location.host() + ':' + $location.port();
            var uriEncodedRedirectUri = encodeURIComponent(redirectUri);
            return '<a href="https://www.dropbox.com/1/oauth2/authorize?redirect_uri=' + uriEncodedRedirectUri + '&response_type=token&client_id=uo6kvpwo8rv9bqi">Authenticate with dropbox</a>';
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

        function compare(thisBudgetPath, otherBudgetPath) {
            var request = {
                method: 'POST',
                url: '/api/dropboxbudgetcomparison',
                data: {
                    access_token: accessToken,
                    this_budget_path: thisBudgetPath,
                    other_budget_path: otherBudgetPath
                }
            }

            return $http(request)
                .then(function(response) {
                    return response;
                });
        }
    }
})();
