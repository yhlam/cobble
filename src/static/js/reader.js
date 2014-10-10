"use strict";
(function(){

var readerApp = angular.module("readerApp", ["ngSanitize", "infinite-scroll", "angularMoment", "cfp.hotkeys", "ui.bootstrap"]);

var Mode = {
  All: "All Item",
  Unread: "Unread Only",
}


readerApp.config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);


readerApp.controller("readerController", ["$scope", "$http", "$window", "hotkeys",
  function($scope, $http, $window, hotkeys) {
    $scope.modes = [Mode.All, Mode.Unread];

    $scope.mode = Mode.All;

    $scope.initialize = function() {
      $scope.entries = [];
      $scope.loading = false;
      $scope.done = false;
      $scope.offset = 0;
      $scope.selected = 0;
      $scope.open = false;
      $scope.last_updated = undefined;
    }

    $scope.initialize();

    $scope.poll = function() {
      if($scope.loading || $scope.done) {
        return;
      }
      $scope.loading = true;

      $scope.last_updated = $scope.last_updated || new Date().toISOString();

      $http.get("/api/v1/entry/", {
        params: {
          last_updated: $scope.last_updated,
          offset: $scope.offset,
          limit: 50,
          read: $scope.mode === Mode.Unread ? "False" : undefined,
        },
      }).success(function(data) {
        var i, entry;
        for(i=0; i<data.length; i++) {
          entry = data[i];
          $scope.entries.push({
            id: entry.id,
            feed: entry.feed,
            title: entry.title,
            time: new Date(entry.time),
            content: entry.content,
            link: entry.link,
            read: entry.read,
          });
        }

        $scope.offset += data.length;
        $scope.loading = false;
        if(data.length <= 0) {
          $scope.done = true;
        }

        $scope.markSelectedAsRead();
      });
    };

    $scope.refresh = function() {
      $scope.initialize();
      $scope.poll();
    }

    $scope.openOrClose = function($index) {
      if($scope.open && $scope.selected === $index) {
        $scope.open = false;
      }
      else{
        $scope.selected = $index;
        $scope.open = true;
        $scope.markSelectedAsRead();
      }
    };

    $scope.setMode = function(mode) {
      $scope.mode = mode;
      $scope.refresh();
    }

    $scope.setRead = function(entry, read) {
      if(entry.read == read) {
        return;
      }

      if(read) {
        $http.post("/api/v1/entry/" + entry.id + "/read/");
      }
      else {
        $http.post("/api/v1/entry/" + entry.id + "/unread/");
      }

      entry.read = read;
      if($scope.mode === Mode.Unread) {
        if(read) {
          $scope.offset = Math.max($scope.offset - 1, 0);
        }
        else {
          $scope.offset = Math.min($scope.offset + 1, $scope.entries.length);
        }
      }
    }

    $scope.markSelectedAsRead = function() {
        var entry = $scope.entries[$scope.selected];
        $scope.setRead(entry, true);
    }

    hotkeys.add({
      combo: "r",
      description: "Refresh",
      callback: $scope.refresh,
    });

    hotkeys.add({
      combo: "j",
      description: "Down",
      callback: function() {
        var max_index = $scope.entries.length - 1;
        $scope.selected = $scope.selected >= max_index ? max_index : $scope.selected + 1;
        $scope.markSelectedAsRead();
      },
    });

    hotkeys.add({
      combo: "k",
      description: "Up",
      callback: function() {
        $scope.selected = $scope.selected <= 0 ? 0 : $scope.selected - 1;
        $scope.markSelectedAsRead();
      },
    });

    hotkeys.add({
      combo: "o",
      description: "Toggle Open",
      callback: function() {
        $scope.open = !$scope.open;
        if($scope.open) {
          $scope.markSelectedAsRead();
        }
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

    hotkeys.add({
      combo: "m",
      description: "Mark as Read / Unread",
      callback: function() {
        var entry = $scope.entries[$scope.selected];
        $scope.setRead(entry, !entry.read);
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
