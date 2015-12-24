(function() {
    'use strict';

    angular
        .module('app')
        .directive('buttonStatus', buttonStatus);

    function buttonStatus() {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                scope.$watch('comparisonExecuting', function(newValue, oldValue){
                    if(newValue) {
                        element.addClass('loading');
                    }
                    else {
                        element.removeClass('loading');
                    }
                });
            }
        };
    }
})();
