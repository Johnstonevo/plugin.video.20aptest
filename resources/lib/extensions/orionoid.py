# -*- coding: utf-8 -*-

'''
	Gaia Add-on
	Copyright (C) 201 Gaia

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
'''

import re
import threading

from orion import *

from resources.lib.extensions import tools
from resources.lib.extensions import network
from resources.lib.extensions import interface
from resources.lib.extensions import metadata
from resources.lib.extensions import tools

class Orionoid(object):

	Id = Orion.Id
	Name = Orion.Name
	Scraper = 'oriscrapers'

	ScrapingExclusive = OrionSettings.ScrapingExclusive
	ScrapingSequential = OrionSettings.ScrapingSequential
	ScrapingParallel = OrionSettings.ScrapingParallel

	TypeMovie = Orion.TypeMovie
	TypeShow = Orion.TypeShow

	StreamTorrent = Orion.StreamTorrent
	StreamUsenet = Orion.StreamUsenet
	StreamHoster = Orion.StreamHoster

	AudioStandard = Orion.AudioStandard
	AudioDubbed = Orion.AudioDubbed

	SubtitleSoft = Orion.SubtitleSoft
	SubtitleHard = Orion.SubtitleHard

	VoteUp = Orion.VoteUp
	VoteDown = Orion.VoteDown

	IgnoreExcludes = ['alluc', 'alluc.ee', 'prontv', 'pron.tv', 'llucy', 'llucy.net', 'furk', 'furk.net']

	##############################################################################
	# CONSTRUCTOR
	##############################################################################

	def __init__(self):
		self.mOrion = Orion(key = 'NOKEY')

	##############################################################################
	# LINK
	##############################################################################

	def link(self):
		return self.mOrion.link()

	##############################################################################
	# SETTINGS
	##############################################################################

	def settingsScrapingTimeout(self):
		return self.mOrion.settingsScrapingTimeout()

	def settingsScrapingMode(self):
		return self.mOrion.settingsScrapingMode()

	def settingsScrapingCount(self):
		return self.mOrion.settingsScrapingCount()

	def settingsScrapingQuality(self):
		return self.mOrion.settingsScrapingQuality()

	##############################################################################
	# ADDON
	##############################################################################

	@classmethod
	def addonLaunch(self):
		tools.Extensions.launch(id = Orionoid.Id)

	def addonSettings(self):
		tools.Extensions.settings(id = Orionoid.Id)

	def addonInstalled(self):
		return tools.Extensions.installed(id = Orionoid.Id)

	def addonEnable(self, refresh = False):
		return tools.Extensions.enable(id = Orionoid.Id, refresh = refresh)

	def addonDisable(self, refresh = False):
		return tools.Extensions.disable(id = Orionoid.Id, refresh = refresh)

	def addonWebsite(self, open = False):
		link = self.link()
		if open: tools.System.openLink(link, popupForce = True)
		return link

	##############################################################################
	# ACCOUNT
	##############################################################################

	def accountEnable(self, enable = True):
		tools.Settings.set('providers.general.special.member.oriscrapers', enable)

	def accountDisable(self, disable = True):
		tools.Settings.set('providers.general.special.member.oriscrapers', not disable)

	def accountEnabled(self):
		return self.mOrion.userEnabled() and tools.Settings.getBoolean('providers.general.special.member.oriscrapers')

	def accountValid(self):
		return self.mOrion.userValid()

	def accountAllow(self):
		return self.accountValid() or self.accountEnabled() or self.accountEnabled() == 0

	def accountFree(self):
		return self.mOrion.userFree()

	def accountPremium(self):
		return self.mOrion.userPremium()

	def accountDialog(self):
		return self.mOrion.userDialog()

	def accountUpdate(self, key = None, input = False, loader = False):
		return self.mOrion.userUpdate(key = key, input = input, loader = loader)

	def accountAnonymous(self):
		if not interface.Dialog.option(title = 35400, message = 35411, labelConfirm = 35427, labelDeny = 3542):
			if OrionUser.anonymous(interface = True):
				self.accountEnable()
		tools.Settings.set('internal.orion.anonymous', False)

	def accountAnonymousEnabled(self):
		return not self.accountValid() and tools.Settings.getBoolean('internal.orion.anonymous')

	##############################################################################
	# SERVER
	##############################################################################

	def serverStats(self):
		return self.mOrion.serverStats()

	def serverTest(self):
		return self.mOrion.serverTest()

	##############################################################################
	# STREAMS - UPDATE
	##############################################################################

	def _streamIgnore(self, stream):
		try:
			torrent = stream['source'] == OrionStream.TypeTorrent

			# Local stream
			if 'local' in stream and stream['local']: return True

			# Member and premium streams
			if 'memberonly' in stream and stream['memberonly']:
				excluded = False
				for exclude in Orionoid.IgnoreExcludes:
					if ('id' in stream and exclude in stream['id'].lower()) or ('name' in stream and exclude in stream['name'].lower()) or ('provider' in stream and exclude in stream['provider'].lower()) or ('source' in stream and exclude in stream['source'].lower()) or ('hoster' in stream and stream['hoster'] and exclude in stream['hoster'].lower()):
						excluded = True
						break
				if not excluded: return True

			# Not magnet and not http/ftp
			if not network.Networker.linkIs(stream['url']) and not network.Container(stream['url']).torrentIsMagnet(): return True

			# Not FQDN or IP address (eg: http://localhost or http://downloads)
			if not torrent and not '.' in network.Networker.linkDomain(stream['url'], subdomain = True, ip = True): return True

			if not torrent:
				# Streams with cookies and headers
				if '|' in stream['url']: return True

				# Very long links, which are most likely invalid or contain cookie/session data
				if len(stream['url']) > 1024: return True
		except:
			return True
		return False

	def _streamUpdate(self, meta, streams):
		item = self._streamUpdateMeta(meta)
		item['streams'] = []
		for stream in streams:
			if not self._streamIgnore(stream):
				data = {'stream' : {}, 'access' : {}, 'file' : {}, 'meta' : {}, 'video' : {}, 'audio' : {}, 'subtitle' : {}}
				if 'orion' in stream and stream['orion']: data['orion'] = True
				meta = metadata.Metadata.initialize(stream)

				if stream['source'] == OrionStream.TypeTorrent:
					data['stream']['type'] = OrionStream.TypeTorrent
				elif stream['source'] == OrionStream.TypeUsenet:
					data['stream']['type'] = OrionStream.TypeUsenet
				else:
					data['stream']['type'] = OrionStream.TypeHoster
					data['stream']['hoster'] = stream['source']

				data['stream']['link'] = stream['url']
				if 'origin' in stream: data['stream']['origin'] = stream['origin']
				data['stream']['source'] = stream['provider']
				if meta.seeds() > 0: data['stream']['seeds'] = meta.seeds()
				if meta.age() > 0: data['stream']['time'] = tools.Time.timestamp() - (meta.age() * 8400)

				data['access']['direct'] = meta.direct()
				if 'cache' in stream:
					if 'premiumize' in stream['cache']: data['access']['premiumize'] = stream['cache']['premiumize']
					if 'offcloud' in stream['cache']: data['access']['offcloud'] = stream['cache']['offcloud']
					if 'realdebrid' in stream['cache']: data['access']['realdebrid'] = stream['cache']['realdebrid']

				if 'hash' in stream: data['file']['hash'] = stream['hash']
				if 'file' in stream: data['file']['name'] = stream['file']
				if meta.size(format = False, estimate = True) > 0: data['file']['size'] = meta.size(format = False, estimate = True)
				data['file']['pack'] = meta.pack()

				if meta.release(full = False): data['meta']['release'] = meta.release(full = False)
				if meta.uploader(full = False): data['meta']['uploader'] = meta.uploader(full = False)
				if meta.edition(): data['meta']['edition'] = meta.edition()

				if meta.videoQuality(): data['video']['quality'] = meta.videoQuality()
				if meta.videoCodec(): data['video']['codec'] = meta.videoCodec()
				data['video']['3d'] = meta.videoExtra3d()

				if meta.videoQuality(): data['video']['quality'] = meta.videoQuality()
				if meta.videoCodec(): data['video']['codec'] = meta.videoCodec()
				data['video']['3d'] = meta.videoExtra3d()

				data['audio']['type'] = OrionStream.AudioDubbed if meta.audioDubbed() else OrionStream.AudioStandard
				data['audio']['channels'] = meta.audioChannels(True) if meta.audioChannels(number = True) else 2
				if meta.audioSystem(): data['audio']['system'] = meta.audioSystem(full = False)
				if meta.audioCodec(): data['audio']['codec'] = meta.audioCodec(full = False)
				data['audio']['languages'] = [i[0] for i in meta.audioLanguages()] if len(meta.audioLanguages()) > 0 else [tools.Language.EnglishCode]

				if meta.subtitlesIsSoft() or meta.subtitlesIsHard(): data['subtitle']['type'] = OrionStream.SubtitleHard if meta.subtitlesIsHard() else OrionStream.SubtitleSoft

				item['streams'].append(data)

		return OrionItem(data = item).update()

	def _streamUpdateMeta(self, meta):
		item = {}
		item['type'] = type = Orionoid.TypeShow if 'tvshowtitle' in meta else Orionoid.TypeMovie

		if item['type'] == Orionoid.TypeMovie:
			item['movie'] = {}

			item['movie']['id'] = {}
			try: item['movie']['id']['imdb'] = meta['imdb'].replace('tt', '')
			except: pass
			try: item['movie']['id']['tmdb'] = meta['tmdb']
			except: pass

			item['movie']['meta'] = {}
			try: item['movie']['meta']['title'] = meta['title']
			except: pass
			try: item['movie']['meta']['year'] = int(meta['year'])
			except: pass
		elif item['type'] == Orionoid.TypeShow:
			item['show'] = {}
			item['episode'] = {}

			item['show']['id'] = {}
			try: item['show']['id']['imdb'] = meta['imdb'].replace('tt', '')
			except: pass
			try: item['show']['id']['tmdb'] = meta['tvdb']
			except: pass

			item['show']['meta'] = {}
			try: item['show']['meta']['title'] = meta['tvshowtitle']
			except:
				try: item['show']['meta']['title'] = meta['title']
				except: pass
			try: item['show']['meta']['year'] = int(meta['tvshowyear'])
			except:
				try: item['show']['meta']['title'] = meta['year']
				except: pass

			item['episode']['meta'] = {}
			try: item['episode']['meta']['title'] = meta['title']
			except:
				try: item['episode']['meta']['title'] = meta['tvshowtitle']
				except: pass
			try: item['episode']['meta']['year'] = int(meta['year'])
			except:
				try: item['episode']['meta']['title'] = meta['tvshowyear']
				except: pass

			item['episode']['number'] = {}
			season = str(meta['season']).lower().replace('season', '').replace(' ', '')
			try: item['episode']['number']['season'] = int(season)
			except:
				try: item['episode']['number']['season'] = tools.Converter.roman(season)
				except: pass
			episode = str(meta['episode']).lower().replace('episode', '').replace(' ', '')
			try: item['episode']['number']['episode'] = int(episode)
			except:
				try: item['episode']['number']['episode'] = tools.Converter.roman(episode)
				except: pass

		return item

	def streamUpdate(self, meta, streams, wait = False):
		thread = threading.Thread(target = self._streamUpdate, args = (meta, streams))
		thread.start()
		if wait: thread.join()

	def streamRetrieve(self, type, imdb = None, season = None, episode = None, title = None, year = None, query = None):
		result = None
		if not query == None:
			result = self.mOrion.streams(type = type, query = query, details = True)
		elif type == Orionoid.TypeMovie:
			if not imdb == None:
				result = self.mOrion.streams(type = type, idImdb = imdb, details = True)
			elif not title == None:
				query = title
				if not year == None: query += ' ' + str(year)
				result = self.mOrion.streams(type = type, query = query, details = True)
		elif type == Orionoid.TypeShow:
			if not season == None and not episode == None:
				if not imdb == None:
					result = self.mOrion.streams(type = type, idImdb = imdb, numberSeason = season, numberEpisode = episode, details = True)
				elif not title == None:
					query = title + ' ' + str(season) + ' ' + str(episode)
					result = self.mOrion.streams(type = type, query = query, details = True)
		return result

	def streamsCount(self, streams):
		return self.mOrion.streamsCount(streams = streams, quality = self.mOrion.FilterSettings)

	def streamVote(self, idItem, idStream, vote = VoteUp, notification = False):
		self.mOrion.streamVote(idItem = idItem, idStream = idStream, vote = vote, notification = notification)

	def streamRemove(self, idItem, idStream, notification = False):
		self.mOrion.streamRemove(idItem = idItem, idStream = idStream, notification = notification)

	##############################################################################
	# FLARE
	##############################################################################

	def flare(self, link): # Don't make classmethod, otherwise the Orion API key is not set.
		return OrionApi().flare(link)
