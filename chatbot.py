import telebot
import boto3
import openai
import speech_recognition as sr
from pydub import AudioSegment
import subprocess
import time
import os

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
        max_tokens=50,
        n=1,
        stop=None
    )
    
    polly = boto3.client('polly',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name='us-east-1')

    text = response.choices[0].text

    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    return response['AudioStream']


@bot.message_handler(content_types=['voice'])
def handle_audio(message):
  try:
    # Get the audio file sent by the user
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_user = f'audio-{time.time()}.wav'
    file_speech = f'bot-{time.time()}.wav'
    new_file = open(file_user, 'wb')
    new_file.write(downloaded_file)
    time.sleep(3)
    # Set the path to the FFmpeg executable
    ffmpeg_path = r"C:\<YOUR-PATH>\ffmpeg.exe"

    # Load the audio file using FFmpeg
    subprocess.call([ffmpeg_path, '-i', file_user, file_speech])

    # Load the audio file
    audio_file = AudioSegment.from_file(file_speech, format="wav")

    # Initialize the speech recognizer
    r = sr.Recognizer()

    # Load the audio file into the recognizer
    with sr.AudioFile(file_speech) as source:
        audio = r.record(source)

    # Convert speech to text using Google Speech Recognition
    text = r.recognize_google(audio)
    answer = f'audio{time.time()}.mp3'
    with open(answer, 'wb') as f:
        f.write(process(text).read())
        f.close()
    audio_file = open(answer, 'rb')
    bot.send_voice(chat_id=message.chat.id, voice=audio_file)
    file_paths = [file_user, file_speech, answer]
    for file_path in file_paths:
        # Check if the file exists
        if os.path.exists(file_path):
            # Remove the file
            os.remove(file_path)
        else:
            print(f"File {file_path} does not exist")
  except:
    print("error")
@bot.message_handler(func=lambda message: True)
def send_voice_message(message):

    # save the audio stream to a file
    answer = f'audio{time.time()}.mp3'
    with open(answer, 'wb') as f:
        f.write(process(message.text).read())
        f.close()
    audio_file = open(answer, 'rb')
    bot.send_voice(chat_id=message.chat.id, voice=audio_file)
    if os.path.exists(answer):
        # Remove the file
        os.remove(answer)
    else:
        print(f"File {answer} does not exist")


bot.polling()



