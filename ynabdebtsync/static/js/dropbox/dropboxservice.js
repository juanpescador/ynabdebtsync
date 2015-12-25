(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .factory('dropboxService', dropboxService);

    dropboxService.$inject = ['$http'];

    function dropboxService($http) {
        var service = {
            getAllBudgets: getAllBudgets,
        };

        return service;

        function getAllBudgets(whose) {
            var request = {
                method: 'GET',
                url: '/api/dropboxbudgets/' + whose
            }

            return $http(request)
                .then(function(response) {
                    return response.data;
                });
        }
    }
})();
