# Heroku Setup

1. [Create Heroku app][4]
2. Set the official Node.js [buildpack][1] as priority 1 to [execute gulp
   build][2], to compile Semanic UI’s LESS and JS assets. This is configured in
   `package.json`, in the `postinstall` entry.

        $ heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-nodejs

3. Set the official Python [buildpack][7] to serve the Flask API and Angular
   SPA.

        $ heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-python

4. Push to Heroku.

## Notes

The Node.js buildpack was failing, with an error regarding not finding
`semantic/tasks/build/javascript.js`. The solution was to manually add the
`semantic/tasks/build` directory to the repository as it wasn’t being created
during `npm install` (which then executes `gulp install`, creating the `build`
directory).

Node modules are cached by default, [deactivated cache][6] temporarily while
debugging semantic-ui gulp build execution. While not mentioned, `heroku
config:unset NODE_MODULES_CACHE` reverts to original.

These links were invaluable while configuring the Heroku deployment/build:

    [1]: https://github.com/heroku/heroku-buildpack-nodejs
    [2]: https://devcenter.heroku.com/articles/node-with-grunt
    [3]: http://www.angularonrails.com/deploy-angular-rails-single-page-application-heroku/
    [4]: https://devcenter.heroku.com/articles/getting-started-with-python#set-up
    [5]: https://devcenter.heroku.com/articles/using-multiple-buildpacks-for-an-app
    [6]: https://devcenter.heroku.com/articles/nodejs-support#cache-behavior
    [7]: https://github.com/heroku/heroku-buildpack-python

[3] is a little outdated, the .buildpacks file has been deprecated and is now
configured via the [heroku commandline][5]:

[1]: https://github.com/heroku/heroku-buildpack-nodejs
[2]: https://devcenter.heroku.com/articles/node-with-grunt
[3]: http://www.angularonrails.com/deploy-angular-rails-single-page-application-heroku/
[4]: https://devcenter.heroku.com/articles/getting-started-with-python#set-up
[5]: https://devcenter.heroku.com/articles/using-multiple-buildpacks-for-an-app
[6]: https://devcenter.heroku.com/articles/nodejs-support#cache-behavior
[7]: https://github.com/heroku/heroku-buildpack-python
