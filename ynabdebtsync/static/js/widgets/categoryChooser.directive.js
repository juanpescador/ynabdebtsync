(function() {
    'use strict';

    angular
        .module('app.widgets')
        .directive('categoryChooser', categoryChooser);

    function categoryChooser() {
        return {
            restrict: 'E',
            scope: {
                chosenCategoryModel: '='
            },
            templateUrl: '/static/js/widgets/categoryChooser.html'
        };
    }
})();
