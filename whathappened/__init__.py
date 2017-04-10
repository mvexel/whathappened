#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

from whathappened.osm import OSMChangeset

def whathappened(identifier, watchfor=[], osmtypes=[]):
    """Returns edits made in an OSM changeset based on its id, a list of tags to watch for, and optionally the OSM types to watch"""

    result = {}
    # Add hierarchy for salient OSM types
    for osmtype in osmtypes:
        result[osmtype] = []
    # Get the changeset
    c = OSMChangeset.from_server(identifier)
    # Look through all objects that were modified
    for osmobj in c.modified:
        # Skip the ones that are not of a type we're interested in
        if osmobj.osmtype not in osmtypes:
            continue
        # Consider only the ones that now have tags we're interested in
        if not set(watchfor).isdisjoint(osmobj.tags.keys()):
            # Compare the object with its previous version
            (created, deleted, modified, same) = osmobj.compare_with(osmobj.previous_version())
            # Consider the tags on the watchlist only
            if watchfor & created.keys() or watchfor &  modified.keys() or watchfor & deleted.keys():
                # Construct the content
                child = {"id": osmobj.identifier, "version": osmobj.version}
                child["created"] = dict((k, created[k]) for k in watchfor if k in created)
                child["modified"] = dict((k, modified[k]) for k in watchfor if k in modified)
                child["deleted"] = dict((k, deleted[k]) for k in watchfor if k in deleted)
                # Append to the result
                result[osmobj.osmtype].append(child)
    return result

@app.route("/whathappened/<int:identifier>/<watchfor>")
def full_changeset(identifier, watchfor):
    # Parse watchlist
    w = watchfor.split("|")
    # Set default OSM types
    o = ["node", "way"]
    # Parse optional passed OSM types
    osmtypes_param = request.args.get('osmtypes')
    if osmtypes_param is not None:
        o = osmtypes_param.split("|")
    # Call the main process
    result = whathappened(identifier, w, o)
    # JSON output
    return jsonify(result)