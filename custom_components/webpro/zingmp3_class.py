#import logging
import urllib
import datetime
import hashlib
import hmac
import gzip
import json
#import time
#import math

import urllib.parse
import urllib.request

CONST_PLAYLIST = {
    'zchart week': 'IWZ9Z08I', 'zchart k-pop': 'IWZ9Z0BO', 'zchart us-uk': 'IWZ9Z0BW', 
    'zhot v-pop':'ZU9EUF68', 'zhot k-pop': 'ZU9EUF76', 'zhot us-uk': 'ZUA67EDW', 'zhot c-pop': 'ZU9DCU07', 'zhot v-party': 'ZWZBOIWZ', 'zhot edm': 'ZZZOA8Z9', 'zhot v-dance': 'ZU6CO990', 
    'zhot bolero-best': 'ZWZCOZCF', 'zhot bolero-new': 'ZOD9CUZA', 'zhot bolero-today': 'ZODDIFW6', 'zhot bolero-couple': 'ZUOF8ZCU' 
}

class ZingMP3:

	API_KEY 	= '38e8643fb0dc04e8d65b99994d3dafff'
	SECRET_KEY	= b'10a01dcf33762d3a204cb96429918ff6'

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __init__(self):
		print('Init class')

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_request_path(self, data):

		def mapping(key, value):
			return urllib.parse.quote(key) + "=" + urllib.parse.quote(value)
		
		data = [mapping(k, v) for k, v in data.items()]
		data = "&".join(data)

		return data

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_hash256(self, string):
		return hashlib.sha256(string.encode('utf-8')).hexdigest()

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_hmac512(self, string):
		return hmac.new(self.SECRET_KEY, string.encode('utf-8'), hashlib.sha512).hexdigest()

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_json_data(self, link):

		f = urllib.request.urlopen(link)
		gzipFile = gzip.GzipFile(fileobj=f)

		return json.loads(gzipFile.read().decode('utf-8'))

	# --------------------------------------------------------------------------------------------------------------------------------------------------
	
	def __get_list_zingchart_tuan(self, type):
		url		= f"https://zingmp3.vn/api/chart/get-chart?id={type}&week=null&year=null"
		time	= str(int(datetime.datetime.now().timestamp()))
		sha256	= self.__get_hash256(f"ctime={time}id={type}")

		data = {
			'week': 'null',
			'year': 'null',
			'ctime': time,
			'sig': self.__get_hmac512(f"/chart/get-chart{sha256}"),
			'api_key': self.API_KEY
		}
		
		response = self.__get_json_data(f"{url}{self.__get_request_path(data)}")
		
		try:
			return response['data']['items']
		except:
			return False

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_list_hotlist(self, type):
		url		= f"https://zingmp3.vn/api/playlist/get-playlist-detail?id={type}&"
		time	= str(int(datetime.datetime.now().timestamp()))
		sha256	= self.__get_hash256(f"ctime={time}id={type}")

		data = {
			'ctime': time,
			'sig': self.__get_hmac512(f"/playlist/get-playlist-detail{sha256}"),
			'api_key': self.API_KEY
		}
		
		response = self.__get_json_data(f"{url}{self.__get_request_path(data)}")

		try:
			return response['data']['song']['items']
		except:
			return False

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def __get_search(self, text):

		url		= "https://zingmp3.vn/api/search?"
		time	= str(int(datetime.datetime.now().timestamp()))
		sha256	= self.__get_hash256(f"ctime={time}")

		data = {
			'ctime': time,
			'api_key': self.API_KEY,
			'q': text,
			'start': '0',
			'count': '20',
			'type': 'song',
			'sig': self.__get_hmac512(f"/search{sha256}")
		}

		response = self.__get_json_data(f"{url}{self.__get_request_path(data)}")
		try:
			return response['data']['items']
		except:
			return False

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def get_stream_link(self, id):
		url		= f"https://zingmp3.vn/api/song/get-streamings?id={id}&"
		time	= str(int(datetime.datetime.now().timestamp()))
		sha256	= self.__get_hash256(f"ctime={time}id={id}")

		data = {
			'ctime': time,
			'api_key': self.API_KEY,
			'sig': self.__get_hmac512(f"/song/get-streamings{sha256}")
		}

		streamlink = self.__get_json_data(f"{url}{self.__get_request_path(data)}")
		try:
			medialink = streamlink['data']['default']['128']
			if streamlink['data']['default']['320']:
				medialink = streamlink['data']['default']['320']
			return f"https:{medialink}"
		except:
			return False

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def get_playlist(self, music_type):
		try:
			music_type = music_type.lower()
			if music_type.startswith("zchart"):
				return self.__get_list_zingchart_tuan(CONST_PLAYLIST[music_type])
			elif music_type.startswith("zhot"):
				return self.__get_list_hotlist(CONST_PLAYLIST[music_type])
		except:
			pass

		return False

	# --------------------------------------------------------------------------------------------------------------------------------------------------
	
	def get_searchname(self, searchname):
		return self.__get_search(searchname)

	# --------------------------------------------------------------------------------------------------------------------------------------------------

	def get_playlistkey(self):
		out = []
		for key in CONST_PLAYLIST.keys():
			out.append(key)
		return out

	# --------------------------------------------------------------------------------------------------------------------------------------------------

#aa = ZingMP3()

#print(aa.get_playlist('week'))