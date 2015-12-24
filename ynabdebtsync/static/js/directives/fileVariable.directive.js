(function() {
    'use strict';

    angular
        .module('app')
        .directive('fileVariable', fileVariable);

    // Modified from http://stackoverflow.com/a/19647381
    function fileVariable() {
        // When the file input value changes, set the scope variable specified in the
        // attribute value to the file contents.
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                var onChangeHandler = scope.$eval(attrs.fileOnChange);
                element.bind('change', function(event) {
                    scope[attrs.fileVariable] = event.target.files[0];
                });
            }
        };
    }
})();
