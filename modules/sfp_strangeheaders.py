# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_strangeheaders
# Purpose:      SpiderFoot plug-in for identifying non-standard HTTP headers
#               in web server responses.
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     01/12/2013
# Copyright:   (c) Steve Micallef 2013
# Licence:     GPL
# -------------------------------------------------------------------------------

import json
from sflib import SpiderFoot, SpiderFootPlugin, SpiderFootEvent

# Standard headers, taken from http://en.wikipedia.org/wiki/List_of_HTTP_header_fields
headers = ["access-control-allow-origin", "accept-ranges", "age", "allow", "cache-control",
           "connection", "content-encoding", "content-language", "content-length", "content-location",
           "content-md5", "content-disposition", "content-range", "content-type", "date", "etag",
           "expires", "last-modified", "link", "location", "p3p", "pragma", "proxy-authenticate",
           "refresh", "retry-after", "server", "set-cookie", "status", "strict-transport-security",
           "trailer", "transfer-encoding", "vary", "via", "warning", "www-authenticate",
           "x-frame-options", "x-xss-protection", "content-security-policy", "x-content-security-policy",
           "x-webkit-csp", "x-content-type-options", "x-powered-by", "x-ua-compatible"]

class sfp_strangeheaders(SpiderFootPlugin):
    """Strange Headers:Footprint,Passive:Content Analysis::Obtain non-standard HTTP headers returned by web servers."""

    # Default options
    opts = {}

    results = None

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = self.tempStorage()
        self.__dataSource__ = "Target Website"

        for opt in userOpts.keys():
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return ["WEBSERVER_HTTPHEADERS"]

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return ["WEBSERVER_STRANGEHEADER"]

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data
        eventSource = event.actualSource

        self.sf.debug("Received event, " + eventName + ", from " + srcModuleName)
        if eventSource in self.results:
            return None
        else:
            self.results[eventSource] = True

        if not self.getTarget().matches(self.sf.urlFQDN(eventSource)):
            self.sf.debug("Not collecting header information for external sites.")
            return None

        try:
            jdata = json.loads(eventData)
            if jdata == None:
                return None
        except BaseException as e:
            self.sf.error("Received HTTP headers from another module in an unexpected format.", False)
            return None

        for key in jdata:
            if key.lower() not in headers:
                val = key + ": " + jdata[key]
                evt = SpiderFootEvent("WEBSERVER_STRANGEHEADER", val,
                                      self.__name__, event)
                self.notifyListeners(evt)

# End of sfp_strangeheaders class
