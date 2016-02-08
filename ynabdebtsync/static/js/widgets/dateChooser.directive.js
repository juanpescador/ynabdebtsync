(function() {
    'use strict';

    angular
        .module('app.widgets')
        .directive('dateChooser', dateChooser);

    function dateChooser() {
        return {
            restrict: 'E',
            scope: {
                chosenDateModel: '='
            },
            templateUrl: '/static/js/widgets/dateChooser.html'
        };
    }
})();
