ynabDebtSync.directive('buttonStatus', function(){
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
});
