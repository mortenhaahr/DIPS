room 			= "_room"
room1		 	= room + "1"
room2 			= room + "2"

base_topic 			= "pi_server/"
audio_base 			= base_topic + "audio/"

emotion_topic 		= base_topic + "emotion"
pir_topic 			= base_topic + "pir"
led_topic 			= base_topic + "led"
command_topic 		= audio_base + "commands"

context_topic  		= base_topic + "context/"
datetime_context 	= context_topic + "datetime"
emotion_context 	= context_topic + "emotion"
position_context 	= context_topic + "position"

room_context 		= context_topic + "room"
occupied_context 	= "/occupied"
music_playing_context 	= "/music_playing"
lamp_context 		= "/lamp"

system_context 		= context_topic + "system/"
leds_context 		= system_context + "leds"
audio_context		= system_context + "audio"



