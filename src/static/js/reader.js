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
            feed: {
              name: entry.feed.name,
              link: entry.feed.homepage,
            },
            title: entry.title,
            time: new Date(entry.time),
            content: entry.content,
            link: entry.link,
            read: entry.read,
            starred: entry.starred,
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
        var entry = $scope.entries[$index];
        $scope.setExpanded(entry);
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

    $scope.setExpanded = function(entry) {
      $http.post("/api/v1/entry/" + entry.id + "/expanded/");
    }

    $scope.setOpened = function(entry) {
      $http.post("/api/v1/entry/" + entry.id + "/opened/");
    }

    $scope.setStarred = function(entry, starred) {
      if(entry.starred == starred) {
        return;
      }

      if(starred) {
        $http.post("/api/v1/entry/" + entry.id + "/star/");
      }
      else {
        $http.post("/api/v1/entry/" + entry.id + "/unstar/");
      }

      entry.starred = starred;
    }


    hotkeys.add({
      combo: "r",
      description: "Refresh",
      callback: function(event) {
        $scope.refresh();

        event.preventDefault();
      }
    });

    hotkeys.add({
      combo: "j",
      description: "Down",
      callback: function(event) {
        var max_index = $scope.entries.length - 1;
        $scope.selected = $scope.selected >= max_index ? max_index : $scope.selected + 1;
        $scope.markSelectedAsRead();

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "k",
      description: "Up",
      callback: function(event) {
        $scope.selected = $scope.selected <= 0 ? 0 : $scope.selected - 1;
        $scope.markSelectedAsRead();

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "g g",
      description: "Go to the top",
      callback: function(event) {
        $scope.selected = 0;
        $scope.markSelectedAsRead();

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "shift+g",
      description: "Go to the first unread / bottom",
      callback: function(event) {
        var entries = $scope.entries;
        var length = entries.length;
        for(var i=0; i<length; i++) {
          var entry = entries[i];
          if(!entry.read) {
            break;
          }
        }
        $scope.selected = i;
        $scope.markSelectedAsRead();

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "ctrl+u",
      description: "Jump 10 entries up",
      callback: function(event) {
        var target = Math.max($scope.selected - 10, 0);
        for(var i=$scope.selected; i>=target; i--) {
          $scope.setRead($scope.entries[i], true);
        }
        $scope.selected = target;

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "ctrl+d",
      description: "Jump 10 entries down",
      callback: function(event) {
        var target = Math.min($scope.selected + 10, $scope.entries.length - 1);
        for(var i=$scope.selected; i<=target; i++) {
          $scope.setRead($scope.entries[i], true);
        }
        $scope.selected = target;

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "o",
      description: "Toggle open",
      callback: function(event) {
        $scope.open = !$scope.open;
        if($scope.open) {
          var entry = $scope.entries[$scope.selected];
          $scope.setExpanded(entry);
          $scope.markSelectedAsRead();
        }

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "p",
      description: "Open in new Tab",
      callback: function(event) {
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

        $scope.setOpened(entry);

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "m",
      description: "Mark as read / unread",
      callback: function(event) {
        var entry = $scope.entries[$scope.selected];
        $scope.setRead(entry, !entry.read);

        event.preventDefault();
      },
    });

    hotkeys.add({
      combo: "s",
      description: "Star / Unstar",
      callback: function(event) {
        var entry = $scope.entries[$scope.selected];
        $scope.setStarred(entry, !entry.starred);

        event.preventDefault();
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
