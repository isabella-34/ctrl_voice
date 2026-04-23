import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("clientima006")
client1.on_message = on_message



st.title("Control por voz")
st.subheader("Da órdenes y el sistema te obedecerá")

image = Image.open('voice_ctrl.jpg')

st.image(image, width=200)




st.write("Presiona el botón y habla.")

st.markdown("""
<style>
.voice-btn {
    display: inline-block;
    padding: 12px 30px;
    font-size: 18px;
    font-weight: 500;
    color: white;
    background-color: #4CAF50;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}
.voice-btn:active {
    background-color: #2e7d32;
    opacity: 0.5; /* efecto opaco cuando se presiona */
}
</style>
<button class="voice-btn" id="voiceButton">🎤 Iniciar</button>
""", unsafe_allow_html=True)

stt_button = Button(label="", width=0)

stt_button.js_on_event("button_click", CustomJS(code="""
var btn = document.getElementById("voiceButton");

btn.onclick = function() {
    btn.style.opacity = "0.5"; // se pone opaco al escuchar
    
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            btn.style.opacity = "1"; // vuelve a normal cuando termina
        }
    }

    recognition.start();
}
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ctrl_moli", message)

    
    try:
        os.mkdir("temp")
    except:
        pass
