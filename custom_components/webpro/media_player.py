"""
Support for interface with a Webpro MediaPlayer.

"""
import logging
import voluptuous as vol
import time
import math

from homeassistant.components.media_player import (ENTITY_ID_FORMAT, PLATFORM_SCHEMA, MediaPlayerDevice)
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_ENQUEUE, SUPPORT_PLAY_MEDIA, SUPPORT_SELECT_SOURCE, SUPPORT_STOP, SUPPORT_SHUFFLE_SET,
    MEDIA_TYPE_MUSIC, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE,
    SUPPORT_PREVIOUS_TRACK, SUPPORT_SEEK, SUPPORT_TURN_OFF, SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_VOLUME_STEP, SUPPORT_PLAY, SUPPORT_SELECT_SOUND_MODE)
from homeassistant.const import (
    STATE_IDLE, STATE_OFF, STATE_ON, STATE_PAUSED, STATE_PLAYING, CONF_FRIENDLY_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import slugify

from .const import CONST_PLAYLIST_TRANS

__version__ = '0.1.1'

_LOGGER = logging.getLogger(__name__)
CONST_DEFAULT_NAME = 'Webpro MediaPlayer'

SUPPORT_FEATURES = \
    SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_STEP | \
    SUPPORT_PAUSE | SUPPORT_STOP | SUPPORT_PLAY | \
    SUPPORT_SEEK | SUPPORT_PLAY_MEDIA | SUPPORT_SELECT_SOURCE | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_SHUFFLE_SET | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOUND_MODE

# ------ Set constant
# Apllicate local paramerters
CONST_VOL_STEP = 0.1

# Input Data
CONF_PLAYLIST = 'playlist'
CONF_SEARCHNAME = 'name'

# Component services
SERVICE_PLAYLIST_PLAY = 'playlist_play'
SERVICE_PLAYLIST_NEXT = 'playlist_nexttrack'
SERVICE_PLAYLIST_PREVIOUS = 'playlist_prevtrack'
SERVICE_PLAYLIST_LISTKEY = 'playlist_listkey'
SERVICE_SEARCHNAME = 'search_name'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FRIENDLY_NAME, default=CONST_DEFAULT_NAME): cv.string
})

# --------------------------------------------------------------------------------------------------------------------------------------------------

def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info("Call Webpro MediaPlayer - setup_platform ")

    friendly_name = config.get(CONF_FRIENDLY_NAME)

    wpmedia = WebproMediaPlayerDevice(friendly_name)
    add_devices([wpmedia])

    def call_service_playlist_play(call):
        wpmedia.service_playlist_play(call)

    def call_service_playlist_next_track(call):
        wpmedia.service_playlist_next_track()

    def call_service_playlist_previous_track(call):
        wpmedia.service_playlist_previous_track()

    def call_service_playlist_listkey(call):
        wpmedia.service_playlist_listkey()

    def call_service_seachname(call):
        wpmedia.service_searchname(call)

    hass.services.register(wpmedia._domain, SERVICE_PLAYLIST_PLAY, call_service_playlist_play)
    hass.services.register(wpmedia._domain, SERVICE_PLAYLIST_NEXT, call_service_playlist_next_track)
    hass.services.register(wpmedia._domain, SERVICE_PLAYLIST_PREVIOUS, call_service_playlist_previous_track)
    hass.services.register(wpmedia._domain, SERVICE_PLAYLIST_LISTKEY, call_service_playlist_listkey)
    hass.services.register(wpmedia._domain, SERVICE_SEARCHNAME, call_service_seachname)

    return True

# --------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------

class WebproMediaPlayerDevice(MediaPlayerDevice):

    def __Speaker_getState(self, speaker):
        try:
            speakerStateObj = self.hass.states.get(speaker)
            return speakerStateObj.state
        except:
            return False

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    def __Speaker_getAll(self):
        arr_media_id = ['None']
        thismedia = self._entity_id

        for ent_id in self.hass.states.entity_ids():
            if "media_player." in ent_id:
                if ent_id != thismedia and self.__Speaker_getState(ent_id)!='unavailable':
                    arr_media_id.append(ent_id)
        if len(arr_media_id) > 0:
            return arr_media_id
        else:
            return None

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_getStateAttributies(self, speaker, attri=None):
        try:
            speakerStateObj = self.hass.states.get(speaker)
            speakerStateObjAttr = speakerStateObj.attributes.copy()
            if attri:
                return speakerStateObjAttr[attri]
            else:
                return speakerStateObjAttr
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_setStateAttributies(self, speaker, new_attri):
        try:
            speakerStateObj = self.hass.states.get(speaker)
            speakerStateObjAttr = speakerStateObj.attributes.copy()
            if new_attri.items():
                for k, v in new_attri.items():
                    speakerStateObjAttr[k] = v
                self.hass.states.set(speaker, speakerStateObj.state, speakerStateObjAttr)
                return True
            else:
                return False
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_set_volume_level(self, speaker, volume):
        try:
            self.hass.services.call('media_player', 'volume_set', {'entity_id': speaker, 'volume_level': volume})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_set_volume_up(self, speaker):
        try:
            self.hass.services.call('media_player', 'volume_up', {'entity_id': speaker})
            return True
        except:
            return False
        return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_set_volume_down(self, speaker):
        try:
            self.hass.services.call('media_player', 'volume_down', {'entity_id': speaker})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_set_volume_mute(self, speaker, mute):
        try:
            self.hass.services.call('media_player', 'volume_mute', {'entity_id': speaker, 'is_volume_muted': mute})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_play_media(self, speaker, media_content_id, media_content_type='music'):
        try:
            self.hass.services.call("media_player", "play_media", {'entity_id': speaker, 'media_content_id': media_content_id, 'media_content_type': media_content_type})
            #time.sleep(3)
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_media_pause(self, speaker):
        try:
            self.hass.services.call("media_player", "media_pause", {'entity_id': speaker})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_media_play(self, speaker):
        try:
            self.hass.services.call("media_player", "media_play", {'entity_id': speaker})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_turn_on(self, speaker):
        try:
            self.hass.services.call('media_player', 'turn_on', {'entity_id': speaker})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __Speaker_turn_off(self, speaker):
        try:
            self.hass.services.call('media_player', 'turn_off', {'entity_id': speaker})
            return True
        except:
            return False
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    def __MediaController(self, action, **kwargs):
        result = False
        
        if action == 'get_allspeaker':
            result = self.__Speaker_getAll()
        else:
            if self._speaker == 'None':
                return False

            if action == 'play_media':
                result = self.__Speaker_play_media(self._speaker, self._attr['media_content_id'], self._attr['media_content_type'])
                if result:
                    self.__panel_songinfo()
            elif action == 'media_play':
                result = self.__Speaker_media_play(self._speaker)
            elif action == 'media_pause':
                result = self.__Speaker_media_pause(self._speaker)
            elif action == 'set_volume_level':
                result = self.__Speaker_set_volume_level(self._speaker, kwargs['volume'])
            elif action == 'volume_up':
                result = self.__Speaker_set_volume_up(self._speaker)
            elif action == 'volume_down':
                result = self.__Speaker_set_volume_down(self._speaker)
            elif action == 'volume_mute':
                result = self.__Speaker_set_volume_mute(self._speaker, kwargs['mute'])
            elif action == 'speaker_state':
                result = self.__Speaker_getState(self._speaker)
            elif action == 'speaker_attribution':
                try:
                    if kwargs['attri']:
                        result = self.__Speaker_getStateAttributies(self._speaker, kwargs['attri'])
                except:
                    result = self.__Speaker_getStateAttributies(self._speaker)
            elif action == 'set_speaker_attribution':
                result = self.__Speaker_setStateAttributies(self._speaker, kwargs['attri'])

        return result

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __refresh_playlist(self, action=None, calledtime=0, name=''):
        if calledtime>=10:
            self.turn_off()
            return False

        if action=='next':
            if len(self._albumlist) > 0:
                if self._songindex + 1 < len(self._albumlist):
                    self._songindex = self._songindex + 1
                else:
                    self._songindex = 0
            else:
                self._songindex = -1
        elif action=='previous':
            if len(self._albumlist) > 0:
                if self._songindex - 1 >= 0:
                    self._songindex = self._songindex - 1
                else:
                    self._songindex = len(self._albumlist)-1
            else:
                self._songindex = -1
        elif action=='search' and name!='':
            self._songindex = -1
            self._albumlist = self._zingmp3.get_searchname(name)
            try:
                if 'Custom' not in self._sound_mode_list :
                    self._sound_mode_list.append('Custom') #self._zingmp3.get_playlistkey()
                self._sound_mode = 'Custom'
                self._numofsongs = len(self._albumlist)
                self._songindex = 0
            except:
                self._numofsongs = 0
        else:
            self._songindex = -1
            self._albumlist = self._zingmp3.get_playlist(self._sound_mode)
            try:
                self._numofsongs = len(self._albumlist)
                self._songindex = 0
            except:
                self._numofsongs = 0

        if self._songindex >= 0:
            self.checking = 0
            self._songinfo = self._albumlist[self._songindex]
            self._songinfo['streamlink'] = self._zingmp3.get_stream_link(self._songinfo['id'])
            self._attr['media_playlist'] = 'Zing Mp3'
            self._attr['media_content_type'] = 'music'
            self._attr['media_content_id'] = self._songinfo['streamlink']
            self._attr['media_duration'] = self._songinfo['duration']
            self._attr['media_title'] = self._songinfo['title']
            self._attr['media_artist'] = self._songinfo['artists_names']
            self._attr['entity_picture'] = self._songinfo['thumbnail_medium']
            self._media_track = "%d / %d" % (self._songindex+1, self._numofsongs)
            
            if not self._attr['media_content_id']:
                self.__refresh_playlist('next',calledtime+1)
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __refresh_speakers(self):
        self._source_list = self.__MediaController('get_allspeaker')

        if self._source_list:
            if not self._source:
                self._source = self._source_list[0]
                self._speaker = self._source
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
        
    def __force_media_play(self):
        if self.__MediaController('play_media'):
            self._state = STATE_PLAYING

    # --------------------------------------------------------------------------------------------------------------------------------------------------    

    def __show_panel(self, sout):
        service_data = {'title': self._name, 'message': sout, 'notification_id': self._name}
        self.hass.services.call('persistent_notification', 'create', service_data)

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __panel_songinfo(self):
        sout  = '<div><table><tr>'
        sout += '<td><img src="'+self._songinfo['thumbnail']+'" width="60" /></td>'
        sout += '<td>'
        sout += 'Title: <strong>'+self._songinfo['title']+'</strong><br/>'
        sout += 'Artist: '+self._songinfo['artists_names']+'<br/>'
        sout += 'Link: <a href="'+self._songinfo['streamlink']+ '">Download</a>'
        sout += '</td>'
        sout += '</tr></table></div>'

        self.__show_panel(sout)

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __panel_keylist(self, keylist):
        sout  = ''

        for k in keylist:
            if sout != '': sout += ', '
            sout += k

        self.__show_panel(sout)

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    def __updateInfo(self):
        try:
            dev_attr  = self.__MediaController('speaker_attribution')
            self._attr['media_duration'] = dev_attr['media_duration']
            self._attr['media_position'] = dev_attr['media_position']
            self._attr['media_position_updated_at'] = dev_attr['media_duration']
            self.__MediaController('set_speaker_attribution', attri = {'app_name':self._name, 'media_title':self._attr['media_title']})
            return True
        except:
            return False
        return False

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __volume_fadeout(self, step):
        i = 0
        while i < step:
            i += 1
            self.__MediaController('volume_down')
            time.sleep(0.2)
            
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __volume_fadein(self, step):
        i = 0
        while i < step:
            i += 1
            self.__MediaController('volume_up')
            time.sleep(0.2)

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, friendly_name):
        from .zingmp3_class import ZingMP3

        self._entity_id = ENTITY_ID_FORMAT.format(slugify(friendly_name))
        self._domain = slugify(CONST_DEFAULT_NAME)
        self._zingmp3 = ZingMP3()
        self._albumlist = []
        self._songinfo = []
        self._songindex = 0
        self._numofsongs = 0
        self._name = friendly_name
        self._speaker = None
        self._state = STATE_OFF
        self._source_list = []
        self._source = None
        self._media_track = "0/0"
        self._attr = {}
        self._attr['media_playlist'] = None
        self._attr['media_content_id'] = None
        self._attr['media_title'] = None
        self._attr['media_artist'] = None
        self._attr['entity_picture'] = None
        self._attr['media_content_type'] = None
        self._attr['volume_level'] = 0.1
        self._attr['is_volume_muted'] = False
        self._attr['media_duration'] = 0.0
        self._attr['media_position'] = 0.0
        self._attr['media_position_updated_at'] = None
        self._attr['media_album_name'] = None
        self._sound_mode_list = self._zingmp3.get_playlistkey()
        self._sound_mode = self._sound_mode_list[0]
        self.checking = 0

        self.__refresh_playlist()

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def __checkdev(self):
        try:
            dev_state = self.__MediaController('speaker_state')
            if dev_state == STATE_OFF:
                self.checking = self.checking + 1
            elif dev_state == STATE_IDLE:
                self.media_next_track()
            else:
                dev_attr  = self.__MediaController('speaker_attribution')
                if self._attr['media_content_id'] != dev_attr['media_content_id']:
                    self.checking = self.checking + 1
                else:
                    self.checking = 0
                    self.__updateInfo()
        except:
            self.checking = self.checking + 1
        return self.checking
        
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def update(self):
        if self._state == STATE_PLAYING:
            if self.__checkdev()>=5:
                self.turn_off()
                return
        else:
            return
            
                
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    @property
    def name(self):
        return self._name

    @property
    def speaker(self):
        return self._speaker

    @property
    def state(self):
        return self._state

    @property
    def supported_features(self):
        return SUPPORT_FEATURES

    @property
    def media_playlist(self):
        self._attr['media_playlist']
    
    @property
    def media_content_id(self):
        return self._attr['media_content_id']

    @property
    def media_title(self):
        return self._attr['media_title']

    @property
    def media_artist(self):
        return self._attr['media_artist']

    @property
    def entity_picture(self):
        return self._attr['entity_picture']

    @property
    def media_content_type(self):
        return self._attr['media_content_type']

    @property
    def volume_level(self):
        return self._attr['volume_level']

    @property
    def is_volume_muted(self):
        return self._attr['is_volume_muted']

    @property
    def media_duration(self):
        return self._attr['media_duration']

    @property
    def media_position(self):
        return self._attr['media_position']

    @property
    def media_album_name(self):
        return self._attr['media_album_name']

    @property
    def source_list(self):
        return self._source_list

    @property
    def source(self):
        return self._source

    @property
    def media_track(self):
        return self._media_track

    @property
    def sound_mode(self):
        return self._sound_mode

    @property
    def sound_mode_list(self):
        return self._sound_mode_list

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def select_sound_mode(self, sound_mode):
        if self._sound_mode != sound_mode:
            self._sound_mode = sound_mode
            self.__refresh_playlist()
            self.__force_media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def select_source(self, source):
        if self._source != source:
            self._source = source
            self._speaker = self._source
            self.__refresh_playlist()
            self.__force_media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def set_volume_level(self, volume):
        if self.__MediaController('set_volume_level', volume = volume):
            self._attr['volume_level'] = volume

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def volume_up(self):
        curr_vol = self._attr['volume_level'] + CONST_VOL_STEP

        if curr_vol > 1.0:
            curr_vol = 1.0

        if self.__MediaController('set_volume_level', volume = curr_vol):
            self._attr['volume_level'] = curr_vol

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def volume_down(self):
        curr_vol = self._attr['volume_level'] - CONST_VOL_STEP

        if curr_vol < 0.0:
            curr_vol = 0.0
            
        if self.__MediaController('set_volume_level', volume = curr_vol):
            self._attr['volume_level'] = curr_vol

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def mute_volume(self, mute):
        if self.__MediaController('volume_mute', mute = mute):
            self._attr['is_volume_muted'] = mute

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def media_next_track(self):
        self.__refresh_playlist('next')
        self.__force_media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def media_previous_track(self):
        self.__refresh_playlist('previous')
        self.__force_media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def media_play(self):
        if self.__MediaController('media_play'):
            self._state = STATE_PLAYING

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def media_pause(self):
        if self.__MediaController('media_pause'):
            self._state = STATE_PAUSED

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def media_play_pause(self):
        if self._state == STATE_IDLE or self._state == STATE_ON:
            self.__force_media_play()
        elif self._state == STATE_PLAYING:
            self.media_pause()
        else:
            self.media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------
        
    def play_media(self, media_type, media_id, **kwargs):
        if self._speaker and self._speaker!='None':
            self.__Speaker_play_media(self._speaker, media_id, media_type)

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def turn_on(self):
        self.__refresh_speakers()
        self._state = STATE_ON

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    def turn_off(self):
        self._state = STATE_OFF

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def service_playlist_play(self, call):
        playlist = ''
        try:
            playlist = call.data.get(CONF_PLAYLIST).lower()
            playlist = CONST_PLAYLIST_TRANS[playlist]
            if self._state == STATE_OFF:
                self.turn_on()
            self.select_sound_mode(playlist)
            self.media_play()
        except:
            print('Playlist not found.')

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def service_playlist_next_track(self):
        if self._state != STATE_OFF:
            self.media_next_track()
        else:
            print('Playlist not found.')

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def service_playlist_previous_track(self):
        if self._state != STATE_OFF:
            self.media_previous_track()
        else:
            print('Playlist not found.')

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def service_playlist_listkey(self):
        listkey = self._sound_mode_list
        
        self.__panel_keylist(listkey)

    # --------------------------------------------------------------------------------------------------------------------------------------------------

    def service_searchname(self, call):
        search_name = call.data.get(CONF_SEARCHNAME).lower()

        if not search_name:
            return

        if self._state == STATE_OFF:
            self.turn_on()
        self.__refresh_playlist('search',0,search_name)
        self.__force_media_play()

    # --------------------------------------------------------------------------------------------------------------------------------------------------