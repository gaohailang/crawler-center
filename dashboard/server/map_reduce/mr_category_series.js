var map = function() {
    var self = this;
    this.category.forEach(function(item, idx) {
        emit(item, self.slug.split('-')[0]);
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
    out: 'mr_category_series'
});