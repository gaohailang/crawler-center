window.API_HOST = 'http://127.0.0.1:5000';
window.API_PREFIX = API_HOST + '/api/v1';
var app = angular.module('fluentDashApp', ['ui.bootstrap', 'infinite-scroll', 'angularSpinkit', 'ngClipboard', 'ngRoute', 'ngPopover']);

app.config(function($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(false);

    // category, series, report(或者叫 analysis, statistics)
    // 浏览模式 - (单图放大，photobox), table, columns(waterfall | varied size grid)
    // Todo:
    $routeProvider
        .when('/', {
            templateUrl: '/views/home.html',
            controller: 'idxCtrl'
        })
        .when('/actor/:name', {
            templateUrl: '/views/actor.html',
            controller: 'actorCtrl'
        })
        .when('/category/:name', {
            templateUrl: '/views/category.html',
            controller: 'categoryCtrl'
        })
        .when('/series/:name', {
            templateUrl: '/views/series.html',
            controller: 'seriesCtrl'
            // series with column view
        })
        .when('/diy', {
            templateUrl: '/views/diy.html',
            controller: 'diyCtrl'
            // series with column view
        })
        .when('/profile/likes', {
            templateUrl: '/views/likes.html',
            controller: 'likesCtrl'
        })
        .when('/report', {
            templateUrl: '/views/report.html'
            // report with multi-chart
        })
        .otherwise({
            redirectTo: '/'
        });
});

app.run(function($rootScope) {
    $rootScope.forbidImgSrc = 'http://24.media.tumblr.com/tumblr_m2lim4Wocd1qjev1to1_1280.jpg';
    $rootScope.currentUserName = 'sivagao';
});

app.factory('ListViewAPI', function($http, $timeout) {
    /*
        1 wrapper for eve interface
        2 extend it with busy indicator, ux, used with watch
    */

    function ListView(base) {
        this.baseUrl = base;
        this.finishBase = false;
        this.items = [];
        this.newItems = [];
        this.links;
        this.busy = false;
        this.startAt;
        this.finishUX = false;
    }

    ListView.prototype.nextPage = function() {
        if (this.busy) return;
        this.busy = true;
        this.startAt = (new Date()).getTime();

        var nextHref, url = this.baseUrl;
        if (this.links && this.links.next) {
            nextHref = this.links.next.href;
            if (nextHref.indexOf('http://') > -1) {
                url = nextHref;
            } else {
                url = API_PREFIX + nextHref;
            }
        } else {
            // Todo: hasLoadAll indicator
            if (this.finishBase) return;
            this.finishBase = true;
        }

        $http.get(url).then(function(resp) {
            this.newItems = resp.data._items;
            this.links = resp.data._links;
            // 大于三秒的时候，直接去掉 busy， 小于三秒就等到三秒
            if ((new Date()).getTime() - (this.startAt + 3000)) {
                this.busy = false;
            } else {
                $timeout(function() {
                    this.busy = false;
                }, (this.startAt + 3000) - (new Date()).getTime());
            }
        }.bind(this));
    };

    return ListView;
});

app.controller('idxCtrl', function($scope, $modal, ListViewAPI) {
    $scope.popSettingModal = function() {
        $modal.open({
            templateUrl: 'views/partials/setting-modal.html',
            controller: 'settingModalCtrl',
            size: 'lg'
        })
    };
});

app.controller('actorCtrl', function($scope, $routeParams) {
    $scope.currentActor = $routeParams.name;
});

app.controller('categoryCtrl', function($scope, $routeParams) {
    $scope.currentCategory = $routeParams.name;
});

app.controller('seriesCtrl', function($scope, $routeParams) {
    $scope.currentSeries = $routeParams.name;
});

app.controller('diyCtrl', function($scope, $routeParams, $http) {
    $scope.currentQuery = $routeParams.query;
    $scope.currentDIYAPI = '/api/diy/films' + '?query=' + $routeParams.query;

    $http.get(API_HOST + '/api/diy/history').then(function(resp) {
        $scope.queryHistory = resp.data.data;
    });

    $scope.buildDiyUrl = function(i) {
        return '#diy?query=' + i;
    };
});

app.controller('likesCtrl', function($scope, $routeParams) {});

app.controller('settingModalCtrl', function($scope, $timeout) {
    var ctx;
    $timeout(function() {
        ctx = document.getElementById("chartjs-vis").getContext("2d");
    });
    $scope.form = {};
    $scope.changeVisType = function(val) {
        // if($scope.form=={}) return;
        $scope.currentVisType = val;
        $scope.form.data = JSON.stringify(configDict[val].data, null, 4);
        $scope.form.option = JSON.stringify(configDict[val].option || {}, null, 4);
    };
    $scope.changeVisType('highcharts');
    $scope.$watch('form', function(form) {
        if (!form) return;
        var currentVisType = $scope.currentVisType;
        try {
            eval('var data =' + form.data);
            if (currentVisType === 'highcharts') {
                $timeout(function() {
                    $('#highcharts-vis').highcharts(data);
                });
            }
            if (currentVisType === 'chartjs') {
                eval('var option =' + form.option);
                $timeout(function() {
                    new Chart(ctx).Bar(data, option);
                });
            }
        } catch (e) {
            console.log('Error: ' + e);
        }
    }, true);
});

// directive: filmWaterFallView, filmWaterFallVaryView
// directive: slugIconLinkTitle(抽取 series name link 化，icon 化)
// directive: filterPanel(来对 category 来快速过滤 - tagInput etc)


app.directive('seriesIconLink', function() {
    return {
        scope: {
            slug: '@'
        },
        link: function($scope, $element, $attrs) {
            var seriesIconMap = {
                MIDD: '',
                MDYD: '',
                SOE: ''
            };
            var tplStr = '<span class="label label-info"><a href="/#series/:name">:name</a></span>'

                function getSeriesIcon(name) {
                    return tplStr.replace(/:name/g, name);
                    // return seriesIconMap[name] || ;
                }

            $element.html(getSeriesIcon($scope.slug.split('-')[0]));
        }
    }
})

app.directive('filmColumnView', function() {
    return {
        templateUrl: 'views/partials/film-column-view.html',
        scope: {
            api: '@'
        },
        controller: filmListViewCtrl
    }
});

app.directive('filmTableView', function() {
    return {
        templateUrl: 'views/partials/film-table.html',
        scope: {
            api: '@'
        },
        controller: filmListViewCtrl
    }
});


function filmListViewCtrl($scope, $element, $attrs, ListViewAPI, $timeout, $routeParams, $http) {
    $scope.listView = new ListViewAPI(window.API_HOST + $scope.api);

    /*
        for column view
    */
    $scope.checkColumnNum = function() {
        if ($routeParams.column) {
            return 'film-item-column' + $routeParams.column;
        }
    };
    $scope.inferPlace = function(idx) {
        return idx % 2 ? 'laft' : 'right';
    };

    /*
        for table view
    */
    $scope.sortReverse = false;
    $scope.toggleRowSort = function(type) {
        $scope.sortType = type;
        $scope.sortReverse = !$scope.sortReverse;
    };

    $scope.infoCopied = function() {
        // tooltip it!
    };

    $scope.getDonwloadText = function(i) {
        return i.downloadurl;
    };

    $scope.likeFilm = function(film) {
        $http.post(API_HOST + '/api/film/like/' + film.slug).then(function() {
            film.isLike = true;
        }, function(resp) {
            alert('Something is wrong');
        });
    };

    // first, we just add it - then with diff time popup animation
    $scope.$watch('listView.newItems', function(val) {
        if (!val) return;
        $scope.listView.items = $scope.listView.items.concat(val);
        $timeout(function() {
            // Todo: fix hash to back home exception
            // $element.photobox('a.photo-hook');
        });
    }, true);
}

angular.bootstrap(document, ['fluentDashApp']);