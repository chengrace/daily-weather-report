from bs4 import BeautifulSoup
import smtplib
import email
import requests
import random
import os
from dotenv import load_dotenv
import re

'''
This program sends daily email notifications about the weather included with randomized reminders. 
Automatically sent out in the morning at 8 am.
Purpose is to automate me checking the weather every morning with all the information I need.
'''

def get_weather_today():
    # Get html from website by sending a GET request.
    url = "https://forecast.weather.gov/MapClick.php?lat=40.48943500000007&lon=-74.44545499999998#.Yb1N0n3MIq0"
    result = requests.get(url).text
    doc = BeautifulSoup(result, "html.parser")

    # Get info from doc of today's weather in New Brunswick
    weather = {}
    weather['Current'] = doc.find("p", class_="myforecast-current").text
    weather['Temperature'] = doc.find("p", class_="myforecast-current-lrg").text
    div = doc.find("div", id="current_conditions_detail")
    current_conditions = div.find_all("tr")

    # Gets humidity, wind speed, barometer pressure, dewpoint, visibility, and when last updated.
    for info in current_conditions:
        info = info.find_all("td") #gets table td tags
        info_type = info[0].text.strip()
        info_detail = info[1].text.strip()
        weather[info_type] = info_detail

    # Gets weather for afternoon and night.
    div = doc.find("div", id="detailed-forecast-body")
    forecast = div.find("div")

    #Analyze weather.
    if 'rain' in forecast.text:
        weather['Later'] = 'rain' # today's weather may have rain
    
    return weather

def send_daily_email(subject_line, email_body):
    # Sender, reciever, body of email
    sender = 'graces.email.bot@gmail.com'
    receivers = ['gc650@scarletmail.rutgers.edu']

    # Create message, subject line, to, from
    message = email.message.EmailMessage()
    message.set_content(email_body)
    message.add_header("Subject", subject_line)

    # Connects to GMAIL SMTP Server
    s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
    s.login(user = os.environ.get("GMAIL_USER"), password = os.environ.get("GMAIL_PASSWORD"))
    s.sendmail(sender, receivers, message.as_string())
    s.quit()

def random_message_of_the_day(is_weather_good):
    reminders_good_weather = ['Take a walk in the morning!',  'Go for a light morning jog!', 'Ask a friend to get breakfast!']
    reminders_bad_weather = ['Meditate for 5 minutes today!', 'Dance to a random song!', 
    'Journal for 5 minutes of what you want to accomplish today.', 'Write down manifestations for today.', 
    'Respond to someone that you left hanging.']
    if is_weather_good:
        return random.choice(reminders_good_weather + reminders_bad_weather)
    else: 
        return random.choice(reminders_bad_weather)

def random_text_face(is_weather_good):
    happy_text_faces = ['ʕ•ᴥ•ʔ', '(ᵔᴥᵔ)', '~(˘▾˘~)', '\ (•◡•) /', '(◕‿◕✿)', '♪~ ᕕ(ᐛ)ᕗ', '(✿´‿`)', '(▰˘◡˘▰)']
    upset_text_faces = ['(ง ͠° ͟ل͜ ͡°)ง', 'ಠ_ಠ', '(ಥ﹏ಥ)', 'ಠ╭╮ಠ', '¯\(°_o)/¯', 'ლ,ᔑ•ﺪ͟͠•ᔐ.ლ', '¬_¬', 'ಠoಠ']
    return random.choice(happy_text_faces) if is_weather_good else random.choice(upset_text_faces)

def compose_email(weather):
    # Customize email based on the weather conditions given today. 

    # SUBJECT LINE
    rainy_day_messages = ['It is currently raining...BRING AN UMBRELLA ☂', 'Might want to wear your rainboots today',
    "It's raining, it's pouring...", "Earth is crying today."]
    sunny_day_messages = ['Beautiful weather today!', 'Sun is shining in the sky!', "It's Mr. Blue Sky!"]
    neutral_day_messages = ["Just a normal day."]

    is_weather_good = True
    if 'rain' in weather['Current']:
        subject_line = random.choice(rainy_day_messages)
        is_weather_good = False
    elif 'sunny' in weather['Current']:
        subject_line = random.choice(sunny_day_messages)
    else:
        subject_line = random.choice(neutral_day_messages)

    subject_line += ' ' + random_text_face(is_weather_good)

    # EMAIL BODY
    email_body = ''''''
    email_body = 'It is ' + weather['Temperature'] + ' right now!\r\n'
    temp = re.findall(r'\d+', weather['Temperature'])[0]
    if int(temp) >= 70:
        email_body += "nice and warm!☀\r\n"
    elif int(temp) <= 40:
        email_body += "pretty brisk today, so make sure to bundle up! ❆\r\n"
    else:
        email_body += "coldish weather today\r\n"
    
    humidity = re.findall(r'\d+', weather['Humidity'])[0]
    if int(humidity) > 70:
        email_body += "its also kind of humid bro \r\n"
    
    if weather['Wind Speed'] != 'Calm':
        wind_speed = re.findall(r'\d+', weather['Wind Speed'])[-1]
        if int(wind_speed) > 20:
            email_body += "its a bit windy today, might want to bring a hairtie\r\r\n"

    email_body += "\r\nHERE IS WHAT YOU SHOULD DO TO START OFF TODAY... \r\n" + random_message_of_the_day(is_weather_good) + "\r\n"

    send_daily_email(subject_line, email_body)

# GET USER/PASS FOR EMAIL BOT
load_dotenv(".env")

# PUT TOGETHER CUSTOMIZED EMAIL INFO BASED ON CURRENT WEATHER
weather = get_weather_today()
compose_email(weather)