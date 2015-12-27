(function() {
    'use strict';

    angular
        .module('app.core')
        .factory('budgetComparerService', budgetComparerService);

    budgetComparerService.$inject = ['$http'];

    function budgetComparerService($http) {
        var compare = function (formData) {
            var request = {
                method: 'POST',
                url: '/api/categorycomparison',
                // Angular tries to serialise the FormData, override to leave intact.
                // https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
                transformRequest: angular.identity,
                headers: {
                    // Setting the Content-Type explicitly results in the form boundary
                    // parameter not being set in the Content-Type header.
                    // Browser correctly sets the header to multipart/form-data and assigns
                    // a boundary parameter.
                    'Content-Type': undefined
                },
                data: formData
            }
            return $http(request)
                .then(function(response){
                    return response;
                });
        }

        return {
            compare: compare
        }
    }
})();
