# homeassistant
Webpro MediaPlayer (for ZingMp3)
1. Copy "webpro" folder to "/config/custom_components/" (hassio) or "/usr/share/hassio/homeassistant/custom_components" (hassbian)
2. Add line to configuration.yaml:

media_player:
  - platform: webpro
  
3. Check valid config and restart server
4. Enjoy!
