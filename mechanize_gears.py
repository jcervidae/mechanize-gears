#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Jonathan Cervidae <jonathan.cervidae@gmail.com>
# PGP Fingerprint: 2DC0 0A44 123E 6CC2 EB55  EAFB B780 421F BF4C 4CB4
# Last changed: $LastEdit: 2009-05-24 18:54:26 BST$
# Last committed: $Format:%cd$
# File revision: $Id$
#
# This file is part of mechanizebooster.
#
# mechanizebooster is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# mechanizebooster is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# mechanizebooster in the file COPYING. If not, see
# <http://www.gnu.org/licenses/>.
"""This module are some extenstions to the mechanize Browser object which add
some useful functionality"""

__author__ = "Jonathan Cervidae <jonathan.cervidae@gmail.com>"
__version__ = "0.0.1"
__copyright__ = "Copyright 2009 Jonathan Cervidae"
__license__ = "GPLv3"

import sys
import pydb
if 'pydb' in sys.modules:
    sys.excepthook = pydb.exception_hook

import mechanize
import copy
import lxml.html

class Browser(mechanize.Browser, object):
    """This is a subclass of mechanize.Browser to allow for loose-coupling.
    Using it directly would be pointless, you may as well just use
    mechanize."""
    def __init__(self, factory=None, history=None, request_class=None):
        super(Browser, self).__init__(self, factory=factory, history=history,
                                      request_class=request_class)
        # Give me a break...
        self.set_handle_robots(False)

class Reacting(Browser):
    """A subclass of the mechanize Browser which allows you to add reactions
    to web pages that a browser comes across"""
    def __init__(self, factory=None, history=None, request_class=None):
        self.__reacting_browser_reactions__ = {}
        self.performing_predicate_action = False
        super(Reacting, self).__init__(self, factory=factory, history=history,
                                       request_class=request_class)
    def add_reaction(self, predicate, action, rewind=True, reload=True,
                     reload_cookies=False):
        """This is the method used to add a reaction to a webpage. It
        accepts two required arguments:

        predicate: This is a bound function or lambda which is called
                   every time a web page is loaded. It is passed the
                   response from reading that web page and is expected to
                   return True or False. If it returns True, then the
                   bound function or lambda passed as action will be
                   executed, if it returns False, nothing happens.

        action: This is a bound function or lambda which is called if a
                predicate function returns true. It is not passed any
                arguments and nothing is done with it's return value of it
                returns one. The original code which caused the action to
                trigger will receive the ReactingBrowser object in a state
                very similar to it was before your action function was
                called (except any Cookies changed will be honoured). You
                can change this behaviour, see the optional keyword
                arguments below.  Predicates will not be checked and
                actions will be triggered while your action is executing.

    Optional arguments:

        rewind: Defaults to True. If True, after an action happens, the
                ReactingBrowser instances history, response and request
                are replaced with the objects that were there before your
                action was called, except for the request objects Cookie:
                header will be modified to reflect changes made by your
                action.

       reload: Defaults to True. If True, the original request which
               caused your predicate to return True is executed again
               after your action has finished. Note that your predicate
               will be tested again after reloading, so you should use a
               variable to block it from triggering again if reloading the
               page could cause that to happen or you may end up with an
               infinite loop.

       reload_cookies: Defaults to False. When set to False, the original
                       request object has it's Cookie: header replaced (or
                       deleted) with a header reflecting the state of the
                       CookieJar after your action happened. This is
                       usually what you want to happen and not doing so
                       can often cause infinite-loops where your predicate
                       triggers again if for example, a session ID in a
                       cookie has changed and you set this to True, then
                       the new session ID would be clobbered by the old
                       one.
        """
        reactions = self.__reacting_browser_reactions__
        reactions[predicate] = (action, rewind, reload, reload_cookies)

    def _mech_open(self, url, data=None, update_history=True, visit=None,
                   timeout=mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT):
        """This method tests the predicates and actions. It is not intended to
        be called directly, methods inherited from mechanize.Browser call
        it."""
        response = super(Reacting, self)._mech_open(
            self, url, data=None, update_history=True, visit=None,
            timeout=mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT
        )

        # Only react on visit to avoid action having to return response objects
        if self.performing_predicate_action:
            return response
        for predicate, quad in self.__reacting_browser_reactions__.items():
            action, rewind, reload, reload_cookies = quad
            if predicate(response):
                self.performing_predicate_action = True
                old_history = copy.copy(self._history)
                old_request = self.request
                old_response = self._response
                action()
                self.performing_predicate_action = False
                if rewind:
                    # Worked out how to do this with debugger, sorry it's so
                    # horrible
                    new_cookies = None
                    headers = self.request.unredirected_hdrs
                    if headers.has_key('Cookie'):
                        new_cookies = headers['Cookie']
                    self.request, self._response = (old_request, old_response)
                    self._history = old_history
                    # We will want our new cookies usually
                    # FIXME: Do not copy the header like this, work out a...
                    # new header as the same cookies may not be appropriate.
                    if not reload_cookies:
                        if new_cookies:
                            headers['Cookie'] = new_cookies
                        else:
                            if headers.has_key('Cookie'):
                                headers.pop('Cookie')
                if reload:
                    self.reload()
        # Allows action to change response. TODO: Not sure this is always safe
        return self.response()


class IESpoofing(Browser):
    """There is probably a way to do this with mechanize already and when
    someone informs me what that is, this class will be removed."""

    # Don't mangle my headers. Maybe I will monkey-patch it so it doesn't
    # meddle with the header order at some point too but this should be enough
    # to fool most sites.
    class DontMeddleWithThisString(str):
        """This class exists to enable browser spoofing and there is little
        reason for you to use it directly."""
        def capitalize(self):
            """Make capitalize return the same string instead of changing
            it"""
            return(copy.copy(self))
        def title(self):
            """Make title return the same string instead of changing it"""
            return(copy.copy(self))

    def __init__(self, factory=None, history=None, request_class=None):
        super(IESpoofing, self).__init__(self, factory=factory,
                                        history=history,
                                        request_class=request_class)
        headers = [
            ("Accept", "*/*"),
            ("Accept-Language", "en-us"),
            ("UA-CPU", "x86"),
            ("Accept-Encoding", "gzip"),
            ("User-Agent", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"),
            ("Connection", "Keep-Alive")
        ]
        self.addheaders = [
            tuple([self.DontMeddleWithThisString(string) for string in pair])
            for pair in headers
        ]
        # I've never had any problems with it.
        import warnings
        warnings.filterwarnings(
            "ignore", "gzip transfer encoding is experimental!", UserWarning
        )
        self.set_handle_gzip(mechanize._gzip.HTTPGzipProcessor)

class Scraping(Browser):
    """A subclass of the mechanize Browser which allows you to scrape
    efficiently with the lxml library. This is much faster than BeautifulSoup
    which often causes problems for me when used in conjunction with pydb.
    Therefore, it is the chosen library for scraping here."""
    def __init__(self, factory=None, history=None, request_class=None):
        pydb.debugger()
        super(Scraping, self).__init__(self, factory=factory,
                                        history=history,
                                        request_class=request_class)
        self._scraper = None

    def get_scraper(self):
        """You would not call this directly normally, just access the .scrape
        property"""
        if not self._scraper:
            html = self.response().get_data()
            self._scraper = self.RealScraper(html)
        return self._scraper

    # Mechanize hijacks __getattr__ so I can't do this. The API it provides
    # like that isn't even a good one, browser.form is much better :/
    #scrape = property(get_scraper)

    def __getattr__(self, name):
        if name == "scrape":
            return self.get_scraper()
        return Browser.__getattr__(self,name)

    def _mech_open(self, url, data=None, update_history=True, visit=None,
                   timeout=mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT):
        """This method tests the predicates and actions. It is not intended to
        be called directly, methods inherited from mechanize.Browser call
        it."""
        self._scraper = None
        return super(Scraping, self)._mech_open(
            self, url, data=None, update_history=True, visit=None,
            timeout=mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT
        )
    class RealScraper(object):
        """Performs the donkey work for the Scraping class, by donkey work I
        mean asking lxml to do the donkey work and adds a couple of
        convenience methods"""
        def __init__(self, html):
            # TODO: Subclass lxml.html.HtmlElement
            self.document = lxml.html.document_fromstring(html)
        def one_by_css(self, expr):
            elements = self.document.cssselect(expr)
            if len(elements) > 0:
                return elements[0]
            return None
        def by_css(self, expr):
            return self.document.cssselect(expr)
        def by_id(self, dom_id):
            return self.document.get_element_by_id(dom_id)

