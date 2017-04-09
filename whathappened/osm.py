import logging
import requests
import xml.etree.ElementTree as ET

class OSMObject(object):
    """This represents an OSM object (node, way or relation)"""
    def __init__(self):
        super(OSMObject, self).__init__()
        self.history = []

    @classmethod
    def from_xml(cls, root):
        """Creates a new OSMObject from ElementTree XML"""

        osmobj = cls()
        # Set OSM type and basic metadata
        osmobj.osmtype = root.tag
        osmobj.identifier = int(root.attrib.get("id"))
        osmobj.version = int(root.attrib.get("version"))
        # Set OSM tags
        osmobj.tags = {}
        for elem in root:
            if elem.tag == "tag":
                osmobj.tags[elem.attrib.get("k")] = elem.attrib.get("v")
        return osmobj

    def __retrieve_history(self):
        """Retrieve all historic versions for the OSMObject from the OSM API"""
        
        history_url = "https://www.openstreetmap.org/api/0.6/{osmtype}/{identifier}/history".format(
                osmtype=self.osmtype,
                identifier=self.identifier)
        # Get history from OSM API
        try:
            history_xml = requests.get(history_url).text
        except Exception as e:
            e.message = "No good response from {}".format(history_url)
            raise e
        # Parse XML
        try:
            root = ET.fromstring(history_xml)
        except Exception as e:
            e.message = "No valid xml from {}".format(history_url)
            raise e
        # Initialize history list of the proper size
        self.history = [None] * int(root[len(root)-1].attrib["version"])
        # Populate history list
        for elem in root:
            h = OSMObject.from_xml(elem)
            self.history[h.version-1] = h

    def __repr__(self):
        return "<{osmtype} {identifier} v{version}>".format(
            osmtype=self.osmtype,
            identifier=self.identifier,
            version=self.version)

    def previous_version(self):
        """Helper to get the version before the current one"""
        
        if self.version == 1:
            raise Exception("There is nothing before v1")
        # Lazily retrieve history
        if len(self.history) == 0:
            self.__retrieve_history()
        # Go back in time until we find a valid previous version        
        for i in range(self.version-1, 0, -1):
            # Watch out for skipped version numbers, this can happen because of redaction
            if self.history[i-1] is not None and i >= 0:
                return self.history[i-1]
        raise Exception("There are no previous versions because of redaction")

    def compare_with(this, that):
        """Compare the OSMObject with another"""
        
        # FIXME this assumes that we're only comparing different versions of the same OSM object
        # Check for sane input
        if this.version == 1:
            raise Exception("There is nothing before v1")
        if this.version <= that.version:
            raise Exception("you can only compare to an older version")
        # Lazily retrieve history
        if len(this.history) == 0:
            this.__retrieve_history()
        # Create list of keys for both objects
        this_keys = set(this.tags.keys())
        that_keys = set(that.tags.keys())
        # Check for created and deleted tags
        intersect_keys = this_keys.intersection(that_keys)
        created = dict((k, this.tags[k]) for k in list(this_keys - that_keys))
        deleted = dict((k, that.tags[k]) for k in list(that_keys - this_keys))
        # Check for modified tag values
        modified = {}
        for key in this_keys - (this_keys - that_keys):
            if this.tags[key] != that.tags[key]:
                modified[key] = {"new": this.tags[key], "old": that.tags[key]}
        # We're not really interested in what stayed the same but what the heck
        same = list(o for o in intersect_keys if this.tags[o] == that.tags[o])
        return created, deleted, modified, same


class OSMChangeset(object):
    """An OSM Changeset"""

    def __init__(self):
        super(OSMChangeset, self).__init__()
        self.created = []
        self.modified = []
        self.deleted = []

    @classmethod
    def from_server(cls, identifier):
        """Instantiate an OSMChangeset from an API call"""

        changeset_url = "https://www.openstreetmap.org/api/0.6/changeset/{}/download".format(identifier)
        try:
            # Get OSMChange XML from API
            changeset_xml = requests.get(changeset_url).text
        except Exception as e:
            e.message = "No valid response from ", changeset_url
            raise e
        try:
            root = ET.fromstring(changeset_xml)
        except Exception as e:
            e.message = "No valid xml from", changeset_url
            raise e
        # Create object and set metadata
        changeset = cls()
        changeset.identifier = identifier

        # Populate created, modified, deleted with OSMObjects
        changeset.created = [OSMObject.from_xml(elem) for elem in root.findall("create/*")]
        changeset.modified = [OSMObject.from_xml(elem) for elem in root.findall("modify/*")]
        changeset.deleted = [OSMObject.from_xml(elem) for elem in root.findall("delete/*")]
        
        return changeset

    def __repr__(self):
        return "<changeset {}>".format(self.identifier)
