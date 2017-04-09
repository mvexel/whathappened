#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

from whathappened.osm import OSMChangeset

def whathappened(identifier, watchfor=[], osmtypes=[]):
    result = {}
    for osmtype in osmtypes:
        result[osmtype] = []
    c = OSMChangeset.from_server(identifier)
    for osmobj in c.modified:
        if osmobj.osmtype not in osmtypes:
            continue
        if not set(watchfor).isdisjoint(osmobj.tags.keys()):
            (created, deleted, modified, same) = osmobj.compare_with(osmobj.previous_version())
            if watchfor & created.keys() or watchfor &  modified.keys() or watchfor & deleted.keys():
                child = {"id": osmobj.identifier, "version": osmobj.version}
                child["created"] = dict((k, created[k]) for k in watchfor if k in created)
                child["modified"] = dict((k, modified[k]) for k in watchfor if k in modified)
                child["deleted"] = dict((k, deleted[k]) for k in watchfor if k in deleted)
                result[osmobj.osmtype].append(child)
    return result

@app.route("/whathappened/<int:identifier>/<watchfor>")
def full_changeset(identifier, watchfor):
    w = watchfor.split("|")
    o = ["node", "way"]
    osmtypes_param = request.args.get('osmtypes')
    if osmtypes_param is not None:
        o = osmtypes_param.split("|")
    result = whathappened(identifier, w, o)
    return jsonify(result)