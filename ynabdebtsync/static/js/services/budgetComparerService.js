ynabDebtSync.factory('budgetComparerService', ['$http', function($http) {
    var compare = function (formData) {
        var request = {
            method: 'POST',
            url: '/api/categorycomparison',
            headers: {
                'Content-Type': 'multipart/form-data'
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
}]);
