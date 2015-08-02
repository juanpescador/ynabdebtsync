// Modified from http://stackoverflow.com/a/19647381

// When the file input value changes, set the scope variable specified in the
// attribute value to the file contents.
ynabDebtSync.directive('fileVariable', function(){
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            var onChangeHandler = scope.$eval(attrs.fileOnChange);
            element.bind('change', function(event) {
                scope[attrs.fileVariable] = event.target.files[0];
            });
        }
    };
});
