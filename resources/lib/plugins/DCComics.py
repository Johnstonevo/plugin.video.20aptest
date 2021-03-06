"""
    DC Comics
    Copyright (C) 2018,
    Version 1.0.1
    Team OTB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    -------------------------------------------------------------

    Usage Examples:


    Returns the DC Comics List

    <dir>
    <title>DC Comics</title>
    <dccomics>all</dccomics>
    </dir>
   
    --------------------------------------------------------------

"""



import requests,re,os,xbmc,xbmcaddon
import base64,pickle,koding,time,sqlite3
from koding import route
from ..plugin import Plugin
from resources.lib.util.context import get_context_items
from resources.lib.util.xml import JenItem, JenList, display_list, display_data, clean_url
from resources.lib.external.airtable.airtable import Airtable
from unidecode import unidecode

CACHE_TIME = 86400  # change to wanted cache time in seconds

addon_id = xbmcaddon.Addon().getAddonInfo('id')
addon_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
AddonName = xbmc.getInfoLabel('Container.PluginName')
home_folder = xbmc.translatePath('special://home/')
user_data_folder = os.path.join(home_folder, 'userdata')
addon_data_folder = os.path.join(user_data_folder, 'addon_data')
database_path = os.path.join(addon_data_folder, addon_id)
database_loc = os.path.join(database_path, 'database.db')


class DC_comics(Plugin):
    name = "dccomics"

    def process_item(self, item_xml):
        if "<dccomics>" in item_xml:
            item = JenItem(item_xml)
            if "all" in item.get("dccomics", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_dccomics_list",
                    'url': item.get("dccomics", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item              
            elif "open|" in item.get("dccomics", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_dccomics_items",
                    'url': item.get("dccomics", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item 
            elif "shows|" in item.get("dccomics", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_dccomics_shows",
                    'url': item.get("dccomics", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item
            elif "tv_shows|" in item.get("dccomics", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_dccomics_tv_shows",
                    'url': item.get("dccomics", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item
            elif "season|" in item.get("dccomics", ""):
                result_item = {
                    'label': item["title"],
                    'icon': item.get("thumbnail", addon_icon),
                    'fanart': item.get("fanart", addon_fanart),
                    'mode': "open_dccomics_season",
                    'url': item.get("dccomics", ""),
                    'folder': True,
                    'imdb': "0",
                    'season': "0",
                    'episode': "0",
                    'info': {},
                    'year': "0",
                    'context': get_context_items(item),
                    "summary": item.get("summary", None)
                }
                result_item["properties"] = {
                    'fanart_image': result_item["fanart"]
                }
                result_item['fanart_small'] = result_item["fanart"]
                return result_item


@route(mode='open_dccomics_list')
def open_list():
    pins = "PLugindccomicslist"
    Items = fetch_from_db2(pins)
    if Items:
        display_data(Items)  
    else:    
        xml = ""
        at = Airtable('appUUMKBACjsL4fmx', 'DC Comics', api_key='keyem86gyhcLFSLqh')
        match = at.get_all(maxRecords=1200, view='Grid view') 
        for field in match: 
            try:
                res = field['fields']   
                name = res['name']
                name = remove_non_ascii(name)
                link1 = res['link1']
                thumbnail = res['thumbnail']
                fanart = res['fanart']
                summary = res ['summary']
                summary = remove_non_ascii(summary) 
                print link1                                                           
                xml += "<item>"\
                       "<title>%s</title>"\
                       "<meta>"\
                       "<content>movie</content>"\
                       "<imdb></imdb>"\
                       "<title></title>"\
                       "<year></year>"\
                       "<thumbnail>%s</thumbnail>"\
                       "<fanart>%s</fanart>"\
                       "<summary>%s</summary>"\
                       "</meta>"\
                       "<dccomics>open|%s</dccomics>"\
                       "</item>" % (name,thumbnail,fanart,summary,link1)
            except:
                pass                                                                     
        jenlist = JenList(xml)
        display_list(jenlist.get_list(), jenlist.get_content_type(), pins)

@route(mode='open_dccomics_items',args=["url"])
def open_items(url):    
        xml = ""
        title = url.split("|")[-2]
        key = url.split("|")[-1]
        at = Airtable(key, title, api_key='keyem86gyhcLFSLqh')
        match = at.get_all(maxRecords=1200, view='Grid view')
        if title == "DC Movies":
            pins = "PLugindccomicsmovies"
            Items = fetch_from_db2(pins)
            if Items:
                display_data(Items)  
            else:            
                for field in match:
                    try:
                        res = field['fields']   
                        thumbnail = res['thumbnail']
                        fanart = res['fanart']
                        summary = res['summary']
                        summary = remove_non_ascii(summary)                   
                        name = res['name']
                        name = remove_non_ascii(name)
                        link1 = res['link1']
                        link2 = res['link2']
                        link3 = res['link3']
                        link4 = res['link4']                                                 
                        xml += "<item>"\
                               "<title>%s</title>"\
                               "<meta>"\
                               "<content>movie</content>"\
                               "<imdb></imdb>"\
                               "<title></title>"\
                               "<year></year>"\
                               "<thumbnail>%s</thumbnail>"\
                               "<fanart>%s</fanart>"\
                               "<summary>%s</summary>"\
                               "</meta>"\
                               "<link>"\
                               "<sublink>%s</sublink>"\
                               "<sublink>%s</sublink>"\
                               "<sublink>%s</sublink>"\
                               "<sublink>%s</sublink>"\
                               "</link>"\
                               "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3,link4) 
                    except:
                        pass                                                                     
                jenlist = JenList(xml)
                display_list(jenlist.get_list(), jenlist.get_content_type(), pins)
        elif title == "DC Shows":
            pins = "PLugindccomicsshows"
            Items = fetch_from_db2(pins)
            if Items:
                display_data(Items)  
            else:            
                for field in match:
                    try:
                        res = field['fields']   
                        thumbnail = res['thumbnail']
                        fanart = res['fanart']
                        summary = res['summary']
                        summary = remove_non_ascii(summary)                   
                        name = res['name']
                        name = remove_non_ascii(name)
                        link1 = res['link1']                                                 
                        xml += "<item>"\
                               "<title>%s</title>"\
                               "<meta>"\
                               "<content>movie</content>"\
                               "<imdb></imdb>"\
                               "<title></title>"\
                               "<year></year>"\
                               "<thumbnail>%s</thumbnail>"\
                               "<fanart>%s</fanart>"\
                               "<summary>%s</summary>"\
                               "</meta>"\
                               "<link>"\
                               "<dccomics>shows|%s</dccomics>"\
                               "</link>"\
                               "</item>" % (name,thumbnail,fanart,summary,link1)
                    except:
                        pass                                                                     
                jenlist = JenList(xml)
                display_list(jenlist.get_list(), jenlist.get_content_type(), pins)
        elif title == "DC Animated Series":
            pins = "PLugindccomicsseries"
            Items = fetch_from_db2(pins)
            if Items:
                display_data(Items)  
            else:            
                for field in match:
                    try:
                        res = field['fields']   
                        thumbnail = res['thumbnail']
                        fanart = res['fanart']
                        summary = res['summary']
                        summary = remove_non_ascii(summary)                   
                        name = res['name']
                        name = remove_non_ascii(name)
                        link1 = res['link1']                                                 
                        xml += "<item>"\
                               "<title>%s</title>"\
                               "<meta>"\
                               "<content>movie</content>"\
                               "<imdb></imdb>"\
                               "<title></title>"\
                               "<year></year>"\
                               "<thumbnail>%s</thumbnail>"\
                               "<fanart>%s</fanart>"\
                               "<summary>%s</summary>"\
                               "</meta>"\
                               "<link>"\
                               "<dccomics>shows|%s</dccomics>"\
                               "</link>"\
                               "</item>" % (name,thumbnail,fanart,summary,link1)
                    except:
                        pass                                                                     
                jenlist = JenList(xml)
                display_list(jenlist.get_list(), jenlist.get_content_type(), pins)


@route(mode='open_dccomics_shows',args=["url"])
def open_items(url):
    pins = "PLugindccomics"+url
    Items = fetch_from_db2(pins)
    if Items:
        display_data(Items)  
    else:    
        xml = ""
        title = url.split("|")[-2]
        key = url.split("|")[-1]
        result = title+"_season"
        at = Airtable(key, title, api_key='keyem86gyhcLFSLqh')
        match = at.search('category', result,view='Grid view')
        for field in match:
            try:
                res = field['fields']   
                thumbnail = res['thumbnail']
                fanart = res['fanart']
                summary = res['summary']
                summary = remove_non_ascii(summary)                   
                name = res['name']
                name = remove_non_ascii(name)
                link1 = res['link1']
                url2 = title+"|"+key+"|"+name                                                 
                xml += "<item>"\
                       "<title>%s</title>"\
                       "<meta>"\
                       "<content>movie</content>"\
                       "<imdb></imdb>"\
                       "<title></title>"\
                       "<year></year>"\
                       "<thumbnail>%s</thumbnail>"\
                       "<fanart>%s</fanart>"\
                       "<summary>%s</summary>"\
                       "</meta>"\
                       "<link>"\
                       "<dccomics>season|%s</dccomics>"\
                       "</link>"\
                       "</item>" % (name,thumbnail,fanart,summary,url2)
            except:
                pass                                                                     
        jenlist = JenList(xml)
        display_list(jenlist.get_list(), jenlist.get_content_type(), pins)    

@route(mode='open_dccomics_season',args=["url"])
def open_items(url):
    pins = "PLugindccomics"+url
    Items = fetch_from_db2(pins)
    if Items:
        display_data(Items)  
    else:    
        xml = ""
        title = url.split("|")[-3]
        key = url.split("|")[-2]
        sea_name = url.split("|")[-1]
        result = title+"_"+sea_name
        at = Airtable(key, title, api_key='keyem86gyhcLFSLqh')
        match = at.search('category', result,view='Grid view')
        for field in match:
            try:
                res = field['fields']
                thumbnail = res['thumbnail']
                fanart = res['fanart']
                summary = res['summary']
                summary = remove_non_ascii(summary)                   
                name = res['name']
                name = remove_non_ascii(name)
                link1 = res['link1']
                link2 = res['link2']
                link3 = res['link3']
                xml += "<item>"\
                       "<title>%s</title>"\
                       "<meta>"\
                       "<content>movie</content>"\
                       "<imdb></imdb>"\
                       "<title></title>"\
                       "<year></year>"\
                       "<thumbnail>%s</thumbnail>"\
                       "<fanart>%s</fanart>"\
                       "<summary>%s</summary>"\
                       "</meta>"\
                       "<link>"\
                       "<sublink>%s</sublink>"\
                       "<sublink>%s</sublink>"\
                       "<sublink>%s</sublink>"\
                       "</link>"\
                       "</item>" % (name,thumbnail,fanart,summary,link1,link2,link3)                                                               
            except:
                pass                  
        jenlist = JenList(xml)
        display_list(jenlist.get_list(), jenlist.get_content_type(), pins)    

def fetch_from_db2(url):
    koding.reset_db()
    url2 = clean_url(url)
    match = koding.Get_All_From_Table(url2)
    if match:
        match = match[0]
        if not match["value"]:
            return None   
        match_item = match["value"]
        try:
                result = pickle.loads(base64.b64decode(match_item))
        except:
                return None
        created_time = match["created"]
        if float(created_time) + CACHE_TIME <= time.time():
            koding.Remove_Table(url2)
            db = sqlite3.connect('%s' % (database_loc))        
            cursor = db.cursor()
            db.execute("vacuum")
            db.commit()
            db.close()
            return result
        else:
            pass                     
        return result
    else:
        return []

def remove_non_ascii(text):
    return unidecode(text)
