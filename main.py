import os
import math
import random
import requests

from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = datetime.now()

# 微信公众测试号ID和SECRET
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

# 可把os.environ结果替换成字符串在本地调试
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')
citys = os.environ["CITY"].split(',')
solarys = os.environ["SOLARY"].split(',')
start_dates = os.environ["START_DATE"].split(',')
birthdays = os.environ["BIRTHDAY"].split(',')


# 获取天气和温度
def get_weather(city):
    url = "https://api.seniverse.com/v3/weather/daily.json?key=i2ljafer9jmgrnyj&location={}&language=zh-Hans&unit=c&start=0&days=1".format(city)
    res = requests.get(url).json()
    weather = res['results'][0]['daily'][0]
    return weather['text_night'], weather['high'],weather['low'],weather['wind_scale']


# 当前城市、日期
def get_city_date(city):
    return city, today.date().strftime("%m"),today.date().strftime("%d")


# 距离设置的日期过了多少天
def get_count(start_date):
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 距离发工资还有多少天
def get_solary(solary):
    next = datetime.strptime(str(date.today().year) + "-" + str(date.today().month) + "-" + solary, "%Y-%m-%d")+datetime.timedelta(days=1)
    if next < datetime.now():
        if next.month == 12:
            next = next.replace(year=next.year + 1)
        next = next.replace(month=(next.month + 1) % 12)
    return (next - today).days


# 距离过生日还有多少天
def get_birthday(birthday):
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")+datetime.timedelta(days=1)
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


# 每日一句
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 字体随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

for i in range(len(user_ids)):
    wea, high,low,wind_scale, = get_weather(citys[i])
    cit, mon,day = get_city_date(citys[i])
    data = {
        "date": {"value": "今天是{}月{}号".format(mon,day), "color": get_random_color()},
        "love_days": {"value": "是我们在一起的第{}天,爱你哟~".format(get_count(start_dates[i])), "color": get_random_color()},
        "weather": {"value": "{}今天的天气：{}".format(cit,wea), "color": get_random_color()},
        "temperature": {"value": "最高温度：{}℃ ，最低温度：{}℃， 风力：{}级".format(high,low,wind_scale), "color": get_random_color()},
        "birthday_left": {"value": "还有{}天就是你的生日啦！".format(get_birthday(birthdays[i])), "color": get_random_color()},
        "solary": {"value": "距离发工资还有{}天,挣钱的日子辛苦了~".format(get_solary(solarys[i])), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()}
    }
    if get_birthday(birthdays[i]) == 0:
        data["birthday_left"]['value'] = "今天是你的生日哦，要开心幸福呀"
    if get_solary(solarys[i]) == 0:
        data["solary"]['value'] = "今天发工资啦，快去犒劳一下自己吧"
    res = wm.send_template(user_ids[i], template_ids[i], data)
    print(res)
