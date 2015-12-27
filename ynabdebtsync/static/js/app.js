(function() {
    'use strict';

    angular.module('app', [
            'app.core',

            /*
             * Feature areas.
             */
            'app.layout',
            'app.localbudgets',
            'app.dropbox',
            'app.widgets'
        ]);
})();
