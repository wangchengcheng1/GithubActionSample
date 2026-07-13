# 安装依赖 pip3 install requests schedule
import os
import requests
import json

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId = os.environ.get("OPEN_ID")
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")

# 气象厅(JMA)预报接口是按都道府県分区的，这里维护 城市 -> 所属地域/代表观测点 的映射
# 城市所属地域(region_name)决定天气/风向，代表观测点(temp_station)决定气温
CITY_AREA_MAP = {
    "市川市": {"area_code": "120000", "region_name": "北西部", "temp_station": "千葉"},
}


def get_weather(my_city):
    city_info = CITY_AREA_MAP.get(my_city)
    if city_info is None:
        raise ValueError(f"暂不支持的城市: {my_city}，请先在 CITY_AREA_MAP 中添加对应的JMA地域信息")

    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{city_info['area_code']}.json"
    forecast = requests.get(url).json()[0]

    region_series = forecast["timeSeries"][0]
    region = next(a for a in region_series["areas"] if a["area"]["name"] == city_info["region_name"])
    weather_typ = region["weathers"][0].replace("　", "")
    wind = region["winds"][0].replace("　", "")

    temp_series = forecast["timeSeries"][2]
    station = next(a for a in temp_series["areas"] if a["area"]["name"] == city_info["temp_station"])
    temps = sorted(int(t) for t in station["temps"] if t)
    if not temps:
        temp = "气温数据暂缺"
    elif len(temps) >= 2:
        temp = f"{temps[0]}——{temps[-1]}摄氏度"
    else:
        temp = f"{temps[0]}摄氏度"

    return my_city, temp, weather_typ, wind


def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def get_daily_love():
    # 每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love


def send_weather(access_token, weather):
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值

    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {
                "value": today_str
            },
            "region": {
                "value": weather[0]
            },
            "weather": {
                "value": weather[2]
            },
            "temp": {
                "value": weather[1]
            },
            "wind_dir": {
                "value": weather[3]
            },
            "today_note": {
                "value": get_daily_love()
            }
        }
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)



def weather_report(this_city):
    # 1.获取access_token
    access_token = get_access_token()
    # 2. 获取天气
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    # 3. 发送消息
    send_weather(access_token, weather)



if __name__ == '__main__':
    weather_report("市川市")