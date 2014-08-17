# -*- coding: utf-8 -*-

# from flask import Flask
from flask import json, request, Response
from eve import Eve
from eve.utils import parse_request, querydef

from pymongo import Connection
import pymongo
from bson.objectid import ObjectId
MongoCon = Connection('localhost', 27017)
Collection = MongoCon.jp_av.films

import json
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Todo: 利用 Eve 中 HATEOES, PAGINATION, 等 aggregation with baike/wiki 等
app = Eve()
@app.route('/api/<regex("(category)|(actor)"):key>/<val>/films', methods=['GET'])
def get_inlist_films(key, val):
    cursor = Collection.find({key: {'$in': [val]}})
    return normal_resource_handler(cursor)

@app.route('/api/series/<val>/films', methods=['GET'])
def get_matchstr_films(val):
    cursor = Collection.find({'slug': {'$regex': '^'+val}}).sort('slug', pymongo.DESCENDING)
    return normal_resource_handler(cursor)

@app.route('/api/user/<username>/like/films', methods=['GET'])
def get_user_like_films(username):
    cursor = Collection.find({'likes': {'$in': [username]}})
    return normal_resource_handler(cursor)

@app.route('/api/film/like/<slug>', methods=['POST', 'OPTIONS'])
def like_film(slug):
    # hardcore with username:sivagao
    try:
        # todo: { "$err" : "Unsupported projection option: likes", "code" : 13097 }
        # change $push to $addToSet
        # delete likes, $unset: {'likes':1}
        Collection.update({'slug': slug}, {'$addToSet': {'likes': 'sivagao'}})
        return succResponse()
    except:
        return errorResponse('mongo')

def succResponse(data=1, status=200):
    ret = dict(data=data, msg='success action!')
    return generalJsonResponse(ret, status)

def errorResponse(kind):
    ret = dict(data={}, msg=kind+" encounter a error!")
    return generalJsonResponse(ret, 430)

def generalJsonResponse(ret, status=200):
    # or use abort(430), @app.errorhandler(430) decorator
    # flask.Response(response=ret, status=200, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)
    resp =Response(response=json.dumps(ret),\
        status=status, mimetype="application/json")
    return enableCORS(resp)

def normal_resource_handler(cursor):
    # todo: trans likes list into islike flag variable
    cutCursor, nextLink, total = paginationResource(cursor)

    _items = [i for i in cutCursor]
    _links = dict(next=nextLink)
    _meta = dict(total=total)

    resp = app.make_response(JSONEncoder().encode(dict(_items=_items, _links=_links)))
    resp.mimetype = 'application/json'
    resp = enableCORS(resp)
    return resp

def paginationResource(cursor):
    page = request.args.get('page', default=1, type=int)
    size = request.args.get('size', default=40, type=int)
    offset = page*size - size
    total = cursor.count()
    if total > offset:
        next = dict(href=request.base_url+querydef(page=page + 1))
    else:
        next = None
    return cursor.skip(offset).limit(size), next, total

def enableCORS(resp):
    methods = app.make_default_options_response().headers.get('allow', '')
    resp.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    resp.headers.add('Access-Control-Allow-Methods', methods)
    return resp
    # if request.method == 'OPTIONS':
    #     resp = app.make_default_options_response()
    # resp.headers.add('Access-Control-Allow-Headers', ', '.join(headers))
    # resp.headers.add('Access-Control-Allow-Max-Age', config.X_MAX_AGE)

if __name__ == "__main__":
    app.run(debug=True, use_debugger=True, use_reloader=True)

