# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import urlparse
import json
import xbmcgui
import xbmcplugin
import xbmcaddon
import os
#######################################

#classes
class Show():
	'SHOW'
	def __init__(self, showId, mediaType, title, link, thumbnail):
		self.showId = showId
		self.mediaType = mediaType
		self.title = title
		self.link = link
		self.thumbnail = thumbnail

class Stream():
	'STREAM'
	def __init__(self, streamId, mediaType, title, date, duration, link, thumbnail):
		self.streamId = streamId
		self.mediaType = mediaType
		self.title = title
		self.date = date
		self.duration = duration
		self.link = link
		self.thumbnail = thumbnail
#######################################

#functions
def build_url(base, query):
	return base+'?'+urllib.urlencode(query)

def downloadSourceToString(url):
	rtvsloHtml = urllib2.urlopen(url)
	rtvsloData = rtvsloHtml.read()
	rtvsloHtml.close()
	return rtvsloData

def parseShowsToShowList(js):
	showList = []
	j = json.loads(js)
	j = j['response']['response']
	for show in j:
		showList.append(Show(show['id'], show['mediaType'], show['title'], show['link'], show['thumbnail']['show']))
	return showList

def parseShowToStreamList(js):
	streamList = []
	j = json.loads(js)
	j = j['response']['recordings']
	for stream in j:
		streamList.append(Stream(stream['id'], stream['mediaType'], stream['title'], stream['date'], stream['duration'], stream['link'], stream['images']['thumb']))
	return streamList

def delete_history_item(item):
	h_file = os.path.join(xbmcaddon.Addon('plugin.video.rtvslo').getAddonInfo('path'), 'history')
	if item!='brisi_vse':
		hfile = open(h_file, 'r')
		data = hfile.readlines()
		hfile.close()
		hfile = open(h_file, 'w')
		for line in data:
			if line!=item+'\n':
				if line!=item:
					hfile.write(line)
		hfile.close()
	else:
		open(h_file, 'w').close()

def parseStreamToPlaylist(js, folderType):
	j = json.loads(js)
	j = j['response']

	typeOK = True
	try:
		mediaType = j['mediaType']
		if folderType == 0 and mediaType == 'video':
			typeOK = False
		if folderType == 1 and mediaType == 'audio':
			typeOK = False
	except Exception as e:
		pass

	if typeOK:
		#newer video streams usually have this format
		try:
			playlist_type1 = j['addaptiveMedia']['hls']
			return playlist_type1
		except Exception as e:
			pass

		#audio streams and some older video streams have this format
		try:
			playlist_type2_part1 = j['mediaFiles'][0]['streamers']['http']
			if playlist_type2_part1.find('ava_archive03') > 0:
				playlist_type2_part1 = playlist_type2_part1.replace("ava_archive03", "ava_archive03/")
			elif playlist_type2_part1.find('ava_archive02') > 0:
				playlist_type2_part1 = playlist_type2_part1.replace("ava_archive02", "podcast\/ava_archive02\/")
			elif playlist_type2_part1.find('ava_archive01') > 0:
				playlist_type2_part1 = playlist_type2_part1.replace("ava_archive01", "ava_archive01\/")
			elif playlist_type2_part1.find('ava_archive00') > 0:
				playlist_type2_part1 = playlist_type2_part1.replace("ava_archive00", "ava_archive00\/")
			playlist_type2_part2 = j['mediaFiles'][0]['filename']
			return playlist_type2_part1+playlist_type2_part2
		except Exception as e:
			pass
	else:
		return ''

	#there is no hope anymore, you will be rickrolled :/
	return 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
#######################################

#main
if __name__ == "__main__":
	try:
		#get add-on base url
		base = str(sys.argv[0])

		#get add-on handle
		handle = int(sys.argv[1])

		#get add-on args
		args = urlparse.parse_qs(sys.argv[2][1:])

		#get content type
		#contentType == "audio" || "video"
		contentType = str(args.get('content_type')[0])
		contentTypeInt = -1
		if contentType == 'audio':
			contentTypeInt = 0
			xbmcplugin.setContent(handle, 'songs')
		elif contentType == 'video':
			contentTypeInt = 1
			xbmcplugin.setContent(handle, 'tvshows')

		#get mode and other parameters
		modeArg = args.get('mode', ['0'])
		mode = int(modeArg[0])
		letterArg = args.get('letter', ['A'])
		letter = letterArg[0]
		idArg = args.get('id', [''])
		id_ = idArg[0]
		pageArg = args.get('page', ['0'])
		page = int(pageArg[0])
		showTypeIdArg = args.get('showTypeId', ['0'])
		showTypeId = int(showTypeIdArg[0])
		sortArg = args.get('sort', [''])
		sort = sortArg[0]
		searchStringArg = args.get('search_string', [''])
		search_string = searchStringArg[0]

		#open history file for reading and writing
		search_history_file = os.path.join(xbmcaddon.Addon('plugin.video.rtvslo').getAddonInfo('path'), 'history')

		#step 1: Collect underpants...
		if mode == 0:
			#mode == 0: list main menu (LIVE RADIO, ODDAJE, ARHIV)
			#LIVE RADIO
			if contentType == 'audio':
				li = xbmcgui.ListItem('V živo')
				url = build_url(base, {'content_type': contentType, 'mode': 1})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			#ISKANJE
			if contentType == 'video':
				li = xbmcgui.ListItem('Iskanje')
				url = build_url(base, {'content_type': contentType, 'mode': 41})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
				#Zgodovina Iskanja
				li = xbmcgui.ListItem('Zgodovina Iskanja')
				url = build_url(base, {'content_type': contentType, 'mode': 42})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			#ARHIV ODDAJ
			li = xbmcgui.ListItem('Arhiv Oddaj')
			url = build_url(base, {'content_type': contentType, 'mode': 21})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			#ARHIV PRISPEVKOV
			li = xbmcgui.ListItem('Arhiv Prispevkov')
			url = build_url(base, {'content_type': contentType, 'mode': 31})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			#ARHIV PO ABECEDI
			li = xbmcgui.ListItem('Arhiv Po Abecedi')
			url = build_url(base, {'content_type': contentType, 'mode': 51})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		#step 2: ...?...
		elif mode == 1:
			#mode == 1: list radio stations (LIVE RADIO)
			radioList = [['ra1', 'RA1', 'Radio prvi'], ['val202', 'VAL202', 'Val 202'], ['sportval202', 'SPORTVAL202', 'Val 202 Šport'], ['ars', 'ARS', 'ARS'], ['rakp', 'RAKP', 'Radio Koper'], ['rsi', 'RSI', 'Radio Si'], ['rmb', 'RAMB', 'Radio Maribor'], ['capo', 'CAPO', 'Radio Capodistria'], ['mmr', 'MMR', 'RA MMR']]
			liveLink = 'http://mp3.rtvslo.si/'
			liveThumb = 'http://img.rtvslo.si/_up/ava/archive2/Content/channel_logos/'
			for radio in radioList:
				li = xbmcgui.ListItem(radio[2], iconImage=liveThumb+radio[1]+'_thumb.jpg')
				xbmcplugin.addDirectoryItem(handle=handle, url=liveLink+radio[0], listitem=li)

		elif mode == 21:
			#mode == 21: (ARHIV ODDAJ)

			#url parameters
			url_part1 = 'http://api.rtvslo.si/ava/getSearch?client_id='
			url_part2 = '&q=&showTypeId='
			url_part3 = '&sort='
			url_part4 = '&order=desc&pageSize=12&pageNumber='
			url_part5 = '&source=&hearingAid=0&clip=show&from=2007-01-01&to=&WPId=&zkp=0&callback=jQuery11130980077945755083_1462458118383&_=1462458118384'
			client_id = '82013fb3a531d5414f478747c1aca622'
			page_no = page
			showType = showTypeId
			sort_by = sort

			#maps for genres and sorting
			li = xbmcgui.ListItem('Zvrsti')
			url = build_url(base, {'content_type': contentType, 'mode': 211, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Sortiranje')
			url = build_url(base, {'content_type': contentType, 'mode': 212, 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

			#download response from rtvslo api
			js = downloadSourceToString(url_part1+client_id+url_part2+str(showType)+url_part3+str(sort_by)+url_part4+str(page_no)+url_part5)

			#extract json from response
			x = js.find('({')
			y = js.rfind('});')
			if x < 0 or y < 0:
				xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
			else:
				#parse json to a list of streams
				js = js[x+1:y+1]
				streamList = parseShowToStreamList(js)

				#find playlists and list streams
				for stream in streamList:
					if (contentTypeInt == 0 and stream.mediaType == 'audio') or (contentTypeInt == 1 and stream.mediaType == 'video'):
						#url parameters
						url_part1 = 'http://api.rtvslo.si/ava/getRecording/'
						url_part2 = '?client_id='
						url_part3 = '&callback=jQuery1113023734881856870338_1462389077542&_=1462389077543'
						client_id = '82013fb3a531d5414f478747c1aca622'
						recording = stream.streamId

						#download response from rtvslo api
						js = downloadSourceToString(url_part1+recording+url_part2+client_id+url_part3)

						#extract json from response
						x = js.find('({')
						y = js.rfind('});')
						if x < 0 or y < 0:
							xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
						else:
							#parse json to get a playlist
							js = js[x+1:y+1]
							playlist = parseStreamToPlaylist(js, contentTypeInt)

							#list stream
							li = xbmcgui.ListItem(stream.date+' - '+stream.title, iconImage=stream.thumbnail)
							if contentTypeInt == 0:
								li.setInfo('music', {'duration': stream.duration})
							elif contentTypeInt == 1:
								li.setInfo('video', {'duration': stream.duration})
							if playlist:
								xbmcplugin.addDirectoryItem(handle=handle, url=playlist, listitem=li)

				#show next page marker if needed
				if len(streamList) > 0:
					page_no = page_no + 1
					li = xbmcgui.ListItem('> '+str(page_no)+' >')
					url = build_url(base, {'content_type': contentType, 'mode': mode, 'page': page_no, 'sort': sort, 'showTypeId': showTypeId})
					xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 211:
			li = xbmcgui.ListItem('Informativni')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 34, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Športni')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 35, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Izobraževalni')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 33, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Kulturno Umetniški')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 30, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Razvedrilni')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 36, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Verski')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 32, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Otroški')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 31, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Mladinski')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'showTypeId': 15890838, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 212:
			li = xbmcgui.ListItem('Po Datumu')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'sort': 'date', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Po Naslovu')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'sort': 'title', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Po Popularnosti')
			url = build_url(base, {'content_type': contentType, 'mode': 21, 'sort': 'popularity', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 31:
			#mode == 31: (ARHIV PRISPEVKOV)

			#url parameters
			url_part1 = 'http://api.rtvslo.si/ava/getSearch?client_id='
			url_part2 = '&q=&showTypeId='
			url_part3 = '&sort='
			url_part4 = '&order=desc&pageSize=12&pageNumber='
			url_part5 = '&source=&hearingAid=0&clip=clip&from=2007-01-01&to=&WPId=&zkp=0&callback=jQuery111307342043845078507_1462458568679&_=1462458568680'
			client_id = '82013fb3a531d5414f478747c1aca622'
			page_no = page
			showType = showTypeId
			sort_by = sort

			#maps for genres and sorting
			li = xbmcgui.ListItem('Zvrsti')
			url = build_url(base, {'content_type': contentType, 'mode': 311, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Sortiranje')
			url = build_url(base, {'content_type': contentType, 'mode': 312, 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

			#download response from rtvslo api
			js = downloadSourceToString(url_part1+client_id+url_part2+str(showType)+url_part3+str(sort_by)+url_part4+str(page_no)+url_part5)

			#extract json from response
			x = js.find('({')
			y = js.rfind('});')
			if x < 0 or y < 0:
				xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
			else:
				#parse json to a list of streams
				js = js[x+1:y+1]
				streamList = parseShowToStreamList(js)

				#find playlists and list streams
				for stream in streamList:
					if (contentTypeInt == 0 and stream.mediaType == 'audio') or (contentTypeInt == 1 and stream.mediaType == 'video'):
						#url parameters
						url_part1 = 'http://api.rtvslo.si/ava/getRecording/'
						url_part2 = '?client_id='
						url_part3 = '&callback=jQuery1113023734881856870338_1462389077542&_=1462389077543'
						client_id = '82013fb3a531d5414f478747c1aca622'
						recording = stream.streamId

						#download response from rtvslo api
						js = downloadSourceToString(url_part1+recording+url_part2+client_id+url_part3)

						#extract json from response
						x = js.find('({')
						y = js.rfind('});')
						if x < 0 or y < 0:
							xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
						else:
							#parse json to get a playlist
							js = js[x+1:y+1]
							playlist = parseStreamToPlaylist(js, contentTypeInt)

							#list stream
							li = xbmcgui.ListItem(stream.date+' - '+stream.title, iconImage=stream.thumbnail)
							if contentTypeInt == 0:
								li.setInfo('music', {'duration': stream.duration})
							elif contentTypeInt == 1:
								li.setInfo('video', {'duration': stream.duration})
							if playlist:
								xbmcplugin.addDirectoryItem(handle=handle, url=playlist, listitem=li)

				#show next page marker if needed
				if len(streamList) > 0:
					page_no = page_no + 1
					li = xbmcgui.ListItem('> '+str(page_no)+' >')
					url = build_url(base, {'content_type': contentType, 'mode': mode, 'page': page_no, 'sort': sort, 'showTypeId': showTypeId})
					xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 311:
			li = xbmcgui.ListItem('Informativni')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 34, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Športni')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 35, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Izobraževalni')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 33, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Kulturno Umetniški')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 30, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Razvedrilni')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 36, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Verski')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 32, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Otroški')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 31, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Mladinski')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'showTypeId': 15890838, 'sort': sort})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 312:
			li = xbmcgui.ListItem('Po Datumu')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'sort': 'date', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Po Naslovu')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'sort': 'title', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			li = xbmcgui.ListItem('Po Popularnosti')
			url = build_url(base, {'content_type': contentType, 'mode': 31, 'sort': 'popularity', 'showTypeId': showTypeId})
			xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 41:
			url_part1 = 'http://api.rtvslo.si/ava/getSearch?client_id='
			url_part2 = '&q='
			url_part3 = '&sort='
			url_part4 = '&order=desc&pageSize=12&pageNumber='
			url_part5 = '&source=&hearingAid=0&clip=clip&from=2007-01-01&to=&WPId=&zkp=0&callback=jQuery111307342043845078507_1462458568679&_=1462458568680'
			url_part5_2 = '&source=&hearingAid=0&clip=show&from=2007-01-01&to=&WPId=&zkp=0&callback=jQuery111307342043845078507_1462458568679&_=1462458568680'
			client_id = '82013fb3a531d5414f478747c1aca622'
			page_no = page
			showType = showTypeId
			sort_by = sort

			if not search_string:
				keyboard = xbmc.Keyboard('', 'Iskanje', False)
				keyboard.doModal()
				if not keyboard.isConfirmed() or not keyboard.getText():
					xbmcgui.Dialog().ok('RTVSLO', 'Iskanje prekinjeno')
				search_string = keyboard.getText()
				sFile = open(search_history_file, 'r')
				data = sFile.readlines()
				sFile.close()
				sFile = open(search_history_file, 'w')
				for line in data:
					if line!='\n':
						sFile.write('%s' %line)
				sFile.write('\n%s\n' %search_string)
				sFile.close()
				#remove empty lines and duplicates
				sFile = open(search_history_file, 'r')
				data = set(sFile.readlines())
				sFile.close()
				sFile = open(search_history_file, 'w')
				for line in data:
					if line!='\n':
						sFile.write('%s' %line)
				sFile.close()
				search_string = search_string.replace(' ', '+')

			chose_dial = xbmcgui.Dialog().select('Izberi:', ['Iskanje Prispevkov', 'Iskanje Oddaj'])
			if chose_dial == 0:
				js = downloadSourceToString(url_part1+client_id+url_part2+search_string+url_part3+str(sort_by)+url_part4+str(page_no)+url_part5)
			else:
				js = downloadSourceToString(url_part1+client_id+url_part2+search_string+url_part3+str(sort_by)+url_part4+str(page_no)+url_part5_2)


			#extract json from response
			x = js.find('({')
			y = js.rfind('});')
			if x < 0 or y < 0:
				xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
			else:
				#parse json to a list of streams
				js = js[x+1:y+1]
				streamList = parseShowToStreamList(js)

				#find playlists and list streams
				for stream in streamList:
					if (contentTypeInt == 0 and stream.mediaType == 'audio') or (contentTypeInt == 1 and stream.mediaType == 'video'):
						#url parameters
						url_part1 = 'http://api.rtvslo.si/ava/getRecording/'
						url_part2 = '?client_id='
						url_part3 = '&callback=jQuery1113023734881856870338_1462389077542&_=1462389077543'
						client_id = '82013fb3a531d5414f478747c1aca622'
						recording = stream.streamId

						#download response from rtvslo api
						js = downloadSourceToString(url_part1+recording+url_part2+client_id+url_part3)

						#extract json from response
						x = js.find('({')
						y = js.rfind('});')
						if x < 0 or y < 0:
							xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
						else:
							#parse json to get a playlist
							js = js[x+1:y+1]
							playlist = parseStreamToPlaylist(js, contentTypeInt)

							#list stream
							li = xbmcgui.ListItem(stream.date+' - '+stream.title, iconImage=stream.thumbnail)
							if contentTypeInt == 0:
								li.setInfo('music', {'duration': stream.duration})
							elif contentTypeInt == 1:
								li.setInfo('video', {'duration': stream.duration})
							if playlist:
								xbmcplugin.addDirectoryItem(handle=handle, url=playlist, listitem=li)

				#show next page marker if needed
				if len(streamList) > 0:
					page_no = page_no + 1
					li = xbmcgui.ListItem('> '+str(page_no)+' >')
					url = build_url(base, {'content_type': contentType, 'mode': mode, 'page': page_no, 'sort': sort, 'showTypeId': showTypeId, 'search_string': search_string})
					xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 42:
			sFile = open(search_history_file, 'r')
			if os.path.getsize(search_history_file) == 0:
				li = xbmcgui.ListItem('Zgodovina je prazna, pojdi na iskanje')
				url = build_url(base, {'content_type': contentType, 'mode': 41, 'sort': 'date', 'showTypeId': showTypeId})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			else:
				li = xbmcgui.ListItem('Novo Iskanje')
				li.addContextMenuItems([('Izbriši zgodovino', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType, 'mode':43, 'search_string': 'brisi_vse'})))])
				url = build_url(base, {'content_type': contentType, 'mode': 41, 'sort': 'date', 'showTypeId': showTypeId})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			for line in sFile:
				search_string = line.replace(' ', '+').replace('\n','')
				li = xbmcgui.ListItem(line)
				li.addContextMenuItems([('Izbriši iskanje', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType, 'mode':43, 'search_string': search_string}))), ('Izbriši zgodovino', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType, 'mode':43, 'search_string': 'brisi_vse'})))])
				url = build_url(base, {'content_type': contentType, 'mode': 41, 'sort': 'date', 'showTypeId': showTypeId, 'search_string': search_string})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
			sFile.close()

		elif mode == 43:
			delete_history_item(search_string)
			xbmc.executebuiltin('Container.Refresh')

		elif mode == 51:
			#mode == 51: list letters menu (ODDAJE)
			oddaje = ['A','B','C','Č','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','Š','T','U','V','W','Z','Ž','0']
			for o in oddaje:
				li = xbmcgui.ListItem(o)
				url = build_url(base, {'content_type': contentType, 'mode': 52, 'letter': o})
				xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 52:
			#mode == 53: letter selected, list shows (ODDAJE)

			#url parameters
			url_part1 = 'http://api.rtvslo.si/ava/getShowsSearch?client_id='
			url_part2 = '&sort=title&order=asc&pageNumber=0&pageSize=100&hidden=0&start='
			url_part3 = '&callback=jQuery111306175395867148092_1462381908718&_=1462381908719'
			client_id = '82013fb3a531d5414f478747c1aca622'
			start = letter

			#download response from rtvslo api
			js = downloadSourceToString(url_part1+client_id+url_part2+start+url_part3)

			#extract json from response
			x = js.find('({')
			y = js.rfind('});')
			if x < 0 or y < 0:
				xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
			else:
				#parse json to a list of shows
				js = js[x+1:y+1]
				showList = parseShowsToShowList(js)

				#list shows
				for show in showList:
					if (contentType == 'audio' and show.mediaType == 'radio') or (contentType == 'video' and show.mediaType == 'tv'):
						li = xbmcgui.ListItem(show.title, iconImage=show.thumbnail)
						url = build_url(base, {'content_type': contentType, 'mode': 53, 'page': 0, 'id': show.showId})
						xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		elif mode == 53:
			#mode == 53: show selected, list streams (ODDAJE)

			#url parameters
			url_part1 = 'http://api.rtvslo.si/ava/getSearch?client_id='
			url_part2 = '&pageNumber='
			url_part3 = '&pageSize=12&clip=show&sort=date&order=desc&from=1991-01-01&showId='
			url_part4 = '&callback=jQuery11130007442688502199202_1462387460339&_=1462387460342'
			client_id = '82013fb3a531d5414f478747c1aca622'
			page_no = page
			show_id = id_

			#download response from rtvslo api
			js = downloadSourceToString(url_part1+client_id+url_part2+str(page_no)+url_part3+show_id+url_part4)

			#extract json from response
			x = js.find('({')
			y = js.rfind('});')
			if x < 0 or y < 0:
				xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
			else:
				#parse json to a list of streams
				js = js[x+1:y+1]
				streamList = parseShowToStreamList(js)

				#find playlists and list streams
				for stream in streamList:

					#url parameters
					url_part1 = 'http://api.rtvslo.si/ava/getRecording/'
					url_part2 = '?client_id='
					url_part3 = '&callback=jQuery1113023734881856870338_1462389077542&_=1462389077543'
					client_id = '82013fb3a531d5414f478747c1aca622'
					recording = stream.streamId

					#download response from rtvslo api
					js = downloadSourceToString(url_part1+recording+url_part2+client_id+url_part3)

					#extract json from response
					x = js.find('({')
					y = js.rfind('});')
					if x < 0 or y < 0:
						xbmcgui.Dialog().ok('RTVSlo.si', 'API response is invalid! :o')
					else:
						#parse json to get a playlist
						js = js[x+1:y+1]
						playlist = parseStreamToPlaylist(js, contentTypeInt)

						#list stream
						li = xbmcgui.ListItem(stream.date+' - '+stream.title, iconImage=stream.thumbnail)
						if contentTypeInt == 0:
							li.setInfo('music', {'duration': stream.duration})
						elif contentTypeInt == 1:
							li.setInfo('video', {'duration': stream.duration})
						if playlist:
							xbmcplugin.addDirectoryItem(handle=handle, url=playlist, listitem=li)

				#show next page marker if needed
				if len(streamList) > 0:
					page_no = page_no + 1
					li = xbmcgui.ListItem('> '+str(page_no)+' >')
					url = build_url(base, {'content_type': contentType, 'mode': mode, 'page': page_no, 'id': show_id})
					xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

		#step 3: ...profit!
		else:
			xbmcgui.Dialog().ok('RTVSlo.si', 'Invalid mode: '+str(mode))

		#write contents
		xbmcplugin.endOfDirectory(handle)

	except Exception as e:
		xbmcgui.Dialog().ok('RTVSlo.si', 'OMG, an error has occured?!\n'+e.message)
