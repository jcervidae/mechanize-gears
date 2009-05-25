#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Jonathan Cervidae <jonathan.cervidae@gmail.com>
# PGP Fingerprint: 2DC0 0A44 123E 6CC2 EB55  EAFB B780 421F BF4C 4CB4
# Last changed: $LastEdit: 2009-05-25 23:13:50 BST$
# Last committed: $Format:%cd$
# File revision: $Id$
#
# This file is part of mechanize-gears.
#
# mechanize-gears is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# mechanize-gears is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# mechanize-gears in the file COPYING. If not, see
# <http://www.gnu.org/licenses/>.

from mechanize_gears import *
import pydb
import sys

if 'pydb' in sys.modules:
    sys.excepthook = pydb.exception_hook

class SpoofAndScrape(Scraping,IESpoofing):
    pass

class TestMechanizeGears(object):
    """This is a test intended to be run with the nose test system"""
    def test_can_pretend_to_be_internet_explorer(self):
        browser = SpoofAndScrape()
        browser.open("http://whatsmyuseragent.com/")
        user_agent = browser.scrape.one_by_css("body center h4").text_content()
        assert (
            user_agent == "Mozilla/4.0 "
            "(compatible; MSIE 7.0; Windows NT 5.1)"
        )
    def test_can_use_a_nice_scraping_api(self):
        browser = Scraping()
        browser.open("http://www.google.com/ncr")
        assert browser.scrape.one_by_css("img#logo").get('alt') == "Google"

if __name__ == '__main__':
    import nose
    nose.main()
