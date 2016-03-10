(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .directive('dropboxBudgetChooser', dropboxBudgetChooser);

    function dropboxBudgetChooser() {
        return {
            restrict: 'E',
            scope: {
                targetBudget: '@',
                targetBudgetPath: '='
            },
            link: link,
            controller: DropboxBudgetChooserController,
            controllerAs: 'vm',
            bindToController: true,
            templateUrl: '/static/js/dropbox/dropboxBudgetChooser.html'
        }
    }

    DropboxBudgetChooserController.$inject = ['dropboxService'];

    function DropboxBudgetChooserController(dropboxService) {
        var vm = this;

        vm.budgets = [];
        vm.gettingBudgets = false;
        vm.getBudgets = getBudgets;

        function getBudgets() {
            if (vm.budgets.length === 0) {
                vm.gettingBudgets = true;
                return dropboxService.getAllBudgets(vm.targetBudget)
                    .then(function(data) {
                        vm.budgets = data;
                        vm.gettingBudgets = false;
                    }, function(error) {
                        vm.gettingBudgets = false;
                    });
            }
        }
    }

    function link(scope, element, attrs) {
        // Initialise Semantic dropdown. It is not the element, but a child.
        angular.element(element[0].querySelector('.dropdown')).dropdown('show');
    }
})();
