# whathappened
What happened in this OSM changeset?

Try it:

[https://osm-what-happened.herokuapp.com/whathappened/41140349/wheelchair?osmtypes=node](https://osm-what-happened.herokuapp.com/whathappened/41140349/wheelchair?osmtypes=node) will look at nodes in changeset 41140349 for added or changed `wheelchair` tags.

```
{
  "node": [
    {
      "created": {}, 
      "deleted": {}, 
      "id": 2923284581, 
      "modified": {
        "wheelchair": {
          "new": "limited", 
          "old": "no"
        }
      }, 
      "version": 3
    }, ...
```

The url pattern is `https://osm-what-happened.herokuapp.com/whathappened/<changeset_id>/<watchlist>[?osmtypes=<osmtypes>` where

* `changeset_id` is your changeset id
* `watchlist` is a pipe-separated list of OSM tag keys to watch for
* `osmtypes` is a pipe-separated list of OSM object types to consider. 

`osmtypes` is optional and defaults to `node|way`.
