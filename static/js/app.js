/**
 * Created by jessicaleung on 2016-11-05.
 */
angular.module('myApp', [
    'ngRoute',
    'myApp.home',
    'myApp.signin'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider
      .otherwise({redirectTo: '/home'});
}]);