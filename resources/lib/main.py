# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.catalogo import watchmojo

from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold
import urlquick
import xbmcgui

# Localized string Constants
SELECT_TOP = 30001
TOP_VIDEOS = 30002
PARTY_MODE = 589
FEATURED = 30005

BASE_URL = "https://www.metalvideo.com"
url_constructor = urljoin_partial(BASE_URL)

@Route.register
def root(plugin, content_type="video"):
    """
    :param Route plugin: The plugin parent object.
    :param str content_type: The type of content being listed e.g. video, music. This is passed in from kodi and
                             we have no use for it as of yet.
    """
    yield Listitem.youtube("UCMm0YNfHOCA-bvHmOBSx-ZA", label="WatchMojo UK")
    yield Listitem.from_dict(watchmojo, "WatchMojo")
