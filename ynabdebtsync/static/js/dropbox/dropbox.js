(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .controller('DropboxController', DropboxController);

    DropboxController.$inject = ['dropboxService'];

    function DropboxController(dropboxService) {
        var vm = this;

        vm.getBudgets = getBudgets;
        vm.otherBudgets = [];
        vm.otherCategory = "";
        vm.thisBudgets = [];
        vm.thisCategory = "";

        function getBudgets(whose) {
            return dropboxService.getAllBudgets(whose)
                .then(function(data) {
                    switch (whose) {
                        case 'mine':
                            vm.thisBudgets = data;
                            break;
                        case 'theirs':
                            vm.otherBudgets = data;
                            break;
                        default:
                            console.log("[DropboxController]: " + whose + " is not a valid value for whose")
                    }
                    return vm.thisBudgets;
                });
        }
    }
})();
