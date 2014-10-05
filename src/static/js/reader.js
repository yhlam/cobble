"use strict";
(function(){

var readerApp = angular.module("readerApp", ["ngSanitize", "infinite-scroll", "angularMoment"]);

readerApp.controller("readerController", ["$scope", "$http",
  function($scope, $http) {
    $scope.entries = [];
    $scope.loading = false;
    $scope.done = false;
    $scope.nextUrl = "/api/v1/entry";
    $scope.poll = function() {
      if(this.loading || this.done) {
        return;
      }
      this.loading = true;

      var $this = this;
      $http.get(this.nextUrl).success(function(data) {
        var i, entry;
        var results = data.results;
        for(i=0; i<results.length; i++) {
          entry = results[i];
          $this.entries.push({
            feed: entry.feed,
            title: entry.title,
            time: new Date(entry.time),
            content: entry.content,
            link: entry.link,
            open: false,
          });
        }
        $this.nextUrl = data.next;

        $this.loading = false;
        if(data.next == null) {
          $this.done = true;
        }
      });
    };
  }]);

})();
