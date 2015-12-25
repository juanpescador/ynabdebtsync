(function() {
    'use strict';

    angular
        .module('app.localbudgets')
        .directive('fileProperty', fileProperty);

    // Modified from http://stackoverflow.com/a/19647381
    function fileProperty() {
        // When the file input value changes, set the scope variable specified in the
        // attribute value to the file contents.
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                var onChangeHandler = scope.$eval(attrs.fileOnChange);
                // If attrs.fileProperty points to a descendant object of
                // scope, as is the case with "vm.property", we need
                // to iterate through the hierarchy up to the object that holds
                // the property. This avoids creating a property on scope whose
                // name is the hierarchy, e.g.
                // scope['vm.property'] instead of scope['vm']['property'].
                var targetObject = scope;
                var objectHierarchy = attrs.fileProperty.split('.');

                // Array.prototype.pop() returns the last element. As we want
                // to traverse the hierarchy from top to bottom, reverse the
                // array so the first element popped is the one highest in the
                // hierarchy.
                objectHierarchy.reverse();
                while (objectHierarchy.length > 1) {
                    targetObject = targetObject[objectHierarchy.pop()];
                }
                var targetProperty = objectHierarchy.pop();

                element.bind('change', function(event) {
                    targetObject[targetProperty] = event.target.files[0];
                });
            }
        };
    }
})();
