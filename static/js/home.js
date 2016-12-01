/**
 * Created by jessicaleung on 2016-11-05.
 */
angular.module('myApp.home', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/home', {
    templateUrl: '../partials/home.html',
    controller: 'HomeCtrl'
  });
}])

.controller('HomeCtrl', [function($scope) {

}]);