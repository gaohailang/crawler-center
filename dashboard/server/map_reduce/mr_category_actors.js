var map = function() {
    var self = this;
    this.category.forEach(function(cate, idx) {
        if (typeof cate === 'string') {
            if (Array.isArray(self.actor)) {
                self.actor.forEach(function(actor) {
                    if (typeof actor !== 'string') {
                        print('dirty3 ' + JSON.stringify(self))
                        return;
                    }
                    emit(cate, actor);
                });
            }
        }
    });
};

var reduce = function(key, emits) {
    var _statsMap = {};
    emits.forEach(function(i) {
        if (typeof i !== 'string') {
            for (var xx in i) {
                _statsMap[xx] = _statsMap[xx] || 0;
                _statsMap[xx] += i[xx];
            }
        } else {
            _statsMap[i] = _statsMap[i] || 0;
            _statsMap[i] += 1;
        }
    });
    return _statsMap;
};

db.films.mapReduce(map, reduce, {
    out: 'mr_category_actors'
});