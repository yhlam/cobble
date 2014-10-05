"use strict";
(function(){

var readerApp = angular.module("readerApp", ["ngSanitize", "infinite-scroll", "angularMoment", "cfp.hotkeys"]);

readerApp.controller("readerController", ["$scope", "$http", "$window", "hotkeys",
  function($scope, $http, $window, hotkeys) {
    $scope.entries = [];
    $scope.loading = false;
    $scope.done = false;
    $scope.nextUrl = "/api/v1/entry";
    $scope.selected = 0;
    $scope.open = false;

    $scope.poll = function() {
      if($scope.loading || $scope.done) {
        return;
      }
      $scope.loading = true;

      $http.get($scope.nextUrl).success(function(data) {
        var i, entry;
        var results = data.results;
        for(i=0; i<results.length; i++) {
          entry = results[i];
          $scope.entries.push({
            feed: entry.feed,
            title: entry.title,
            time: new Date(entry.time),
            content: entry.content,
            link: entry.link,
          });
        }
        $scope.nextUrl = data.next;

        $scope.loading = false;
        if(data.next == null) {
          $scope.done = true;
        }
      });
    };

    $scope.openOrClose = function($index) {
      if($scope.open && $scope.selected === $index) {
        $scope.open = false;
      }
      else{
        $scope.selected = $index;
        $scope.open = true;
      }
    };

    hotkeys.add({
      combo: "r",
      description: "Refresh",
      callback: function() {
        $scope.done = false;
        $scope.loading = false;
        $scope.nextUrl = "/api/v1/entry";
        $scope.selected = 0;
        $scope.open = false;
        $scope.entries = [];
        $scope.poll();
      },
    });

    hotkeys.add({
      combo: "j",
      description: "Down",
      callback: function() {
        var max_index = $scope.entries.length - 1;
        $scope.selected = $scope.selected >= max_index ? max_index : $scope.selected + 1;
      },
    });

    hotkeys.add({
      combo: "k",
      description: "Up",
      callback: function() {
        $scope.selected = $scope.selected <= 0 ? 0 : $scope.selected - 1;
      },
    });

    hotkeys.add({
      combo: "o",
      description: "Toggle Open",
      callback: function() {
        $scope.open = !$scope.open;
      },
    });

    hotkeys.add({
      combo: "p",
      description: "Open in New Tab",
      callback: function() {
        var entry = $scope.entries[$scope.selected];
        var isChrome = $window.navigator.userAgent.toLowerCase().indexOf('chrome') >= 0;
        if(isChrome) {
          var a = document.createElement("a");
          a.href = entry.link;
          var evt = document.createEvent("MouseEvents")
          evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, true, false, false, false, 0, null);
          a.dispatchEvent(evt);
        }
        else {
          $window.open(entry.link)
        }
      },
    });

  }]);

readerApp.directive("readerScrollTo", ["$window", "$timeout",
    function($window, $timeout) {
      return {
        restrict: 'A',
        link: function(scope, elements, attrs) {
          scope.$watch(attrs.readerScrollTo, function(scroll) {
            if(scroll) {
              var element = elements[0];
              $timeout(function() {
                var scrollTop = $window.scrollY;
                var scrollHeight = document.documentElement.scrollHeight;
                var windowHeight = $window.innerHeight;
                var scrollBottom = scrollTop + windowHeight;
                var elementTop = element.offsetTop;
                var elementHeight = element.offsetHeight;
                var elementBottom = elementTop + elementHeight;
                if(elementBottom >= scrollBottom) {
                  if(windowHeight - 60 >= elementHeight) {
                    var scrollTo = Math.min(elementTop - windowHeight + elementHeight, scrollHeight - windowHeight);
                    $window.scrollTo(0, scrollTo);
                  }
                  else {
                    var scrollTo = Math.max(elementTop - 60, 0);
                    $window.scrollTo(0, scrollTo);
                  }
                }
                else if(elementTop < scrollTop + 60) {
                  var scrollTo = Math.max(elementTop - 60, 0);
                  $window.scrollTo(0, scrollTo);
                }
              });
            }
          });
        },
      };
    }]);

})();