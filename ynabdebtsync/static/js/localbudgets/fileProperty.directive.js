(function() {
    'use strict';

    angular
        .module('app.localbudgets')
        .directive('fileProperty', fileProperty);

    fileProperty.$inject = ['$parse']

    // Modified from http://stackoverflow.com/a/19647381
    function fileProperty($parse) {
        // When the file input value changes, set the scope variable specified in the
        // attribute value to the file contents.
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                var onChangeHandler = scope.$eval(attrs.fileOnChange);

                element.bind('change', function(event) {
                    var getter = $parse(attrs.fileProperty);
                    var setter = getter.assign;
                    setter(scope, event.target.files[0]);
                });
            }
        };
    }
})();
