# Big picture

* [Create Heroku app][4]
* Use official node [buildpack][1] to [execute grunt task][2].
* Configure Heroku to use additional [buildpack][3], the official Python one,
  for Flask API and Angular SPA.

[1]: https://github.com/heroku/heroku-buildpack-nodejs
[2]: https://devcenter.heroku.com/articles/node-with-grunt
[3]: http://www.angularonrails.com/deploy-angular-rails-single-page-application-heroku/
[4]: https://devcenter.heroku.com/articles/getting-started-with-python#set-up
