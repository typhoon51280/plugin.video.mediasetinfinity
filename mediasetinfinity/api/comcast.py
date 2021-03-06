from __future__ import unicode_literals, absolute_import
import urlquick
from mediasetinfinity.support import logger, strings
from mediasetinfinity.support.routing import utils, callback, resolver
from mediasetinfinity.api.labels import logo_mediaset, logo_mediaset_play, logo_infinity, logo_infinity_plus

BASE_URL = "https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/"
url_constructor = utils.urljoin_partial(BASE_URL)

DEFAULT_PAGE_SIZE = 50

class ApiComcast():

    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        self._page_size = page_size
        self._session = urlquick.session()

    @property
    def session(self):
        return self._session

    @property
    def page_size(self):
        return self._page_size

    ### TV SERIE ###
    def seriesByGuid(self, guid):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-series-v2"), params={
                'byGuid': guid,
            }), "serie")
    ### TV SERIE ###

    ### TV SEASON ###
    def tvSeasonByGuid(self, guid):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'byGuid': guid,
            }), "tvseason")

    def tvSeasonById(self, id):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'byId': id,
            }), "tvseason")

    def tvSeasonsEndpointMethod(self, seriesId, sort="tvSeasonNumber|asc", page_number=None, page_size=None):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'bySeriesId': seriesId,
                'sort': sort,
                'range': self.range(page_number, page_size),
            }), "tvseason")

    def tvSeasonByBrandId(self, brandId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'byCustomValue': "{{brandId}}{brandId}".format(brandId=strings.join(brandId)),
            }), "tvseason")
    ### TV SEASON ###

    ### SUBBRAND ###
    def subbrandByTvSeasonId(self, tvSeasonId, sort="mediasetprogram$order"):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byTvSeasonId': tvSeasonId,
                'sort': sort,
            }), "subbrand")

    def subbrandById(self, subBrandId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byCustomValue': "{{subBrandId}}{subBrandId}".format(subBrandId=subBrandId),
            }), "subbrand")

    def subbrandByParentId(self, parentId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byTags': "parentId:{parentId}".format(parentId=parentId),
            }), "subbrand")
    ### SUBBRAND ###

    ### EPISODE ###
    def defaultEpisodePerSeasonEndpoint(self, tvSeasonId, sort=":publishInfo_lastPublished|asc,tvSeasonEpisodeNumber|asc"):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-programs-v2"), params={
                'byTvSeasonId': tvSeasonId,
                'byCustomValue': "{editorialType}{Full Episode}",
                'sort': sort,
                'range': "1-1",
            }), "program")

    def subBrandHomeMethod(self, subBrandId, sort=":publishInfo_lastPublished|desc,tvSeasonEpisodeNumber|desc", page_number=None, page_size=None):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-programs-v2"), params={
                'byCustomValue': "{{subBrandId}}{{{subBrandId}}}".format(subBrandId=subBrandId),
                'sort': sort,
                'range': self.range(page_number, page_size),
            }), "program")
    ### EPISODE ###

    ### FEED ##

    def feeds(self, feedUrl, page_number=None, page_size=None):
        return self.__handleResponse(self.session.get(feedUrl), "feed")
    ### FEED ##

    def range(self, page_number=None, page_size=None):
        if not page_number:
            page_number = 1
        if not page_size:
            page_size = self.page_size
        logger.debug("[page_number] %s", page_number)
        logger.debug("[page_size] %s", page_size)
        range_end = page_number * page_size
        range_start = range_end - page_size + 1
        return "{}-{}".format(range_start, range_end)

    def pagination(self, data):
        return {
            'page': (data['startIndex'] - 1) / data['itemsPerPage'] + 1,
            'hitsPerPage': data['itemsPerPage'],
            'hasNextPage': data['entryCount'] and data['itemsPerPage'] == data['entryCount'],
        }

    def __handleResponse(self, response, apitype=""):
        if response.status_code == 200:
            jsn = response.json()
            if 'entries' in jsn and jsn['entries']:
                return {
                    'entries': jsn['entries'],
                    'pagination': self.pagination(jsn),
                    'datatype': list(jsn['$xmlns'].keys())[0],
                    'apitype': apitype,
                }
        return False

    def listItem(self, data, **kwargs):
        if data:
            datatype = kwargs['datatype'] if 'datatype' in kwargs else None
            logger.debug("[datatype] %s", datatype)
            if datatype == "mediasetprogram":
                programtype = data['programtype'].lower() if 'programtype' in data and data['programtype'] else None
                if not programtype and 'programType' in data and data['programType']:
                    programtype = data['programType'].lower()
                if not programtype and 'programtype' in kwargs and kwargs['programtype']:
                    programtype = kwargs['programtype']
                logger.debug("[programtype] %s", programtype)
                if programtype == "episode":
                    return self.__episode(data)
                elif programtype == "series":
                    return self.__serie(data)
                elif programtype == "subbrand":
                    return self.__subbrand(data)
                elif programtype == "extra":
                    return self.__extra(data)
            elif datatype == "mediasettvseason":
                return self.__tvseason(data)
        return False

    def __serie(self, data):
        return {
            'label': data['title'],
        }

    def __subbrand(self, data):
        tvseason = self.tvSeasonById(data['tvSeasonId'])['entries'][0]
        tvseason_data = self.__tvseason(tvseason)
        subbrand_type = "episode" if 'mediasetprogram$editorialType' in data and data['mediasetprogram$editorialType'] == "Full Episode" else "subbrand"
        return {
            'label': data['description'],
            'params': {
                'subBrandId': data['mediasetprogram$subBrandId'],
                'seriesId': data['seriesId'] if 'seriesId' in data else None,
                'tvSeasonId': data['tvSeasonId'] if 'tvSeasonId' in data else None,
            },
            'callback': callback("catalogo", subbrand_type),
            'info': {
                'plot': tvseason_data['info']['plot'],
                'plotoutline': tvseason_data['info']['plotoutline'],
            },
            'art': tvseason_data['art'],
        }

    def __tvseason(self, data):
        images = data['thumbnails']
        return {
            'label': data['title'],
            'params': {
                'seriesGuid': data['seriesId'].split("/")[-1] if 'seriesId' in data else None,
                'seasonGuid': data['guid'] if 'guid' in data else None,
                'seriesId': data['seriesId'] if 'seriesId' in data else None,
                'seasonId': data['id'] if 'id' in data else None,
            },
            'callback': callback("catalogo", "tvseason"),
            'info': {
                'plot': data['mediasettvseason$longDescription'] if 'mediasettvseason$longDescription' in data else "",
                'plotoutline': data['description'] if 'description' in data else "",
            },
            'art': {
                'poster': images['image_vertical-264x396']['url'],
                'banner': images['image_header_poster-1440x630']['url'], # images['image_header_poster-1440x433']['url'],
                'fanart': images['image_horizontal_cover-704x396']['url'], # if 'brand_cover-768x340' in images else images['image_horizontal_cover-704x396']['url'],
                'thumb': images['brand_logo-210x210']['url'],
            },
        }

    def __extra(self, data):
        images = data['thumbnails']
        return {
            'label': data['title'],
            'params': {
                'guid': data['guid'] if 'guid' in data else None,
            },
            'callback': resolver("catalogo", "play"),
            'info': {
                'plot': data['longDescription'] if 'longDescription' in data else "",
                'plotoutline': data['description'] if 'description' in data else "",
            },
            'art': {
                'poster': images['image_vertical-264x396']['url'],
                'banner': images['image_header_poster-1440x630']['url'],
                'fanart': images['image_horizontal_cover-704x396']['url'],
                'thumb': "",
                'icon': images['brand_logo-210x210']['url'],
            },
        }

    def __episode(self, data):
        images = data['thumbnails']
        label = self.__label(data['title'], data['mediasetprogram$channelsRights'])
        return {
            'label': label,
            'params': {
                'guid': data['guid'] if 'guid' in data else None,
            },
            'callback': resolver("catalogo", "play"),
            'info': {
                'plot': data['longDescription'] if 'longDescription' in data else "",
                'plotoutline': data['description'] if 'description' in data else "",
                'title': label, ## required for text formatting by some skins (like estuary) ##
            },
            'art': {
                'poster': images['image_vertical-264x396']['url'],
                'banner': images['image_header_poster-1440x630']['url'],
                'fanart': images['image_horizontal_cover-704x396']['url'],
                'thumb': "",
                'icon': images['brand_logo-210x210']['url'],
            },
        }

    def __label(self, title, channelRights):
        channels =  {
            'Anonymous': None,
            'MediasetPlay': None,
            'Infinity': None,
            'Starz': None,
            'ciplayit': None,
            'historyplayit': None,
            'blazeplayit': None,
            'Moonbug': None,
            'MidnightFactory': None,
            'Juventus': None,
        }
        for chn in channelRights:
            tokens = chn.split("_")
            if len(tokens) == 1:
                value = tokens[0]
                if value == "AVOD":
                    channels['Anonymous'] = True
            elif len(tokens) > 1:
                key = tokens[0]
                value = tokens[1]
                oldval = channels[key]
                if (oldval is None) or (value == "ANY") or (oldval != "ANY" and oldval != "AVOD"):
                    channels[key] = value
        logger.debug("[channels] (%s) - (%s)", channelRights, channels)
        if channels['Anonymous']:
            title = "[{}] {}".format(logo_mediaset, title)
        elif channels['MediasetPlay'] in ["SVOD", "ANY"]:   
            title = "[{}] {}".format(logo_mediaset_play, title)
        elif channels['Infinity'] in ["SVOD", "ANY"]:
            title = "[{}] {}".format(logo_infinity_plus, title)
        logger.debug("[title] %s", title)
        return title 