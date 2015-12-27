(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .controller('DropboxController', DropboxController);

    DropboxController.$inject = ['$location', 'dropboxService'];

    function DropboxController($location, dropboxService) {
        var vm = this;

        vm.getBudgets = getBudgets;
        vm.getAuthLink = getAuthLink;
        vm.isAuthenticated = isAuthenticated;
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

        function isAuthenticated() {
            return dropboxService.isAuthenticated();
        }

        function getAuthLink() {
            return dropboxService.getAuthLink();
        }
    }
})();
