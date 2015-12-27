(function() {
    'use strict';

    angular
        .module('app.dropbox')
        .controller('DropboxController', DropboxController);

    DropboxController.$inject = ['$location', 'dropboxService'];

    function DropboxController($location, dropboxService) {
        var vm = this;

        vm.dropboxAuthLink = dropboxAuthLink;
        vm.getBudgets = getBudgets;
        vm.isAuthed = isAuthed;
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

        function isAuthed() {
            return $location.hash().search(/^access_token=(.+)$/) >= 0;
        }

        function dropboxAuthLink() {
            return '<a href="https://www.dropbox.com/1/oauth2/authorize?redirect_uri=http%3A%2F%2Flocalhost%3A5000&response_type=token&client_id=uo6kvpwo8rv9bqi">Authenticate with dropbox</a>'
        }
    }
})();
