import pyttsx3;
import sys;

# Fetch args from cmd
texts = sys.argv;
texts.pop(0);

# Init TTS
engine = pyttsx3.init();
engine.setProperty("rate", 130);
for voice in engine.getProperty("voices"):
    if "TTS_MS_EN-US_ZIRA" in voice.id:
        engine.setProperty('voice', voice.id);

# Insert Texts to TTS    
for text in texts:
    engine.say(text);

# Execute TTS
engine.runAndWait();
engine.stop();