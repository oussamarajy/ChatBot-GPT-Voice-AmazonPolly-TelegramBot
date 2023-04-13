import telebot
import boto3
import openai
import speech_recognition as sr
import time
import os
import soundfile as sf
import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))



bot = telebot.TeleBot("YOUR-API-KEY-BOT")
openai.api_key = "YOUR-API-KEY"
# specify your AWS access key and secret access key
aws_access_key_id = 'YOUR-ACCESS-KEY'
aws_secret_access_key = 'YOUR-SECRET-ACCESS-KEY'


# text message
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.send_message(message.chat.id, f"Your message is: {message.text}")

def process(message):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message,
        temperature=0.5,
        max_tokens=max_token,
        n=1,
        stop=None
    )
    # create an instance of the Polly client with your credentials
    polly = boto3.client('polly',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name='us-east-1')  # specify the region you want to use

    # specify the text you want to synthesize
    text = response.choices[0].text

    # call the synthesize_speech method to synthesize the text
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    return response['AudioStream']


# Define a function that handles audio messages
@bot.message_handler(content_types=['voice'])
def handle_audio(message):
  try:
    # Get the audio file sent by the user
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_user = f'audios/audio-{time.time()}.oga'
    file_speech = f'audios/bot-{time.time()}.wav'
    new_file = open(file_user, 'wb')
    new_file.write(downloaded_file)
    time.sleep(3)
    # Convert oga to wav
    data, samplerate = sf.read(file_user)
    sf.write(file_speech, data, samplerate)

    # Initialize the speech recognizer
    r = sr.Recognizer()

    # Load the audio file into the recognizer
    with sr.AudioFile(file_speech) as source:
        audio = r.record(source)

    # Convert speech to text using Google Speech Recognition
    text = r.recognize_google(audio)
    answer = f'audios/audio{time.time()}.mp3'
    with open(answer, 'wb') as f:
        f.write(process(text).read())
        f.close()
    audio_file = open(answer, 'rb')
    bot.send_voice(chat_id=message.chat.id, voice=audio_file)
    file_paths = [file_user, file_speech, answer]
    os.remove(file_user)
    os.remove(file_speech)
    os.remove(answer)
  except Exception as e:
      #print(e)
      PrintException()
@bot.message_handler(func=lambda message: True)
def send_voice_message(message):
  try:
    # save the audio stream to a file
    answer = f'audios/audio{time.time()}.mp3'
    with open(answer, 'wb') as f:
        f.write(process(message.text).read())
        f.close()
    audio_file = open(answer, 'rb')
    bot.send_voice(chat_id=message.chat.id, voice=audio_file)
    audio_file.close()
    os.remove(answer)
  except Exception as e:
      # print(e)
      PrintException()

bot.polling()







