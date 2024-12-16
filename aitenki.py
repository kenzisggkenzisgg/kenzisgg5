import streamlit as st
import requests # リクエストするための機能をインポート
from datetime import datetime # 現在時刻などの時間を扱う機能をインポート
import pandas as pd # データフレームを扱う機能をインポート

st.write("天気アプリ")


# 選択肢を作成
city_code_list = {
    "盛岡市":"030010",
    "東京":"130010"
}

city_code_index = st.selectbox("地域を選んでください。", options=list(city_code_list.keys()), index=0)
city_code = city_code_list[city_code_index] # 選択したキーからAPIのリクエストに使うcityコードに変換し、city_codeに代入

url = "https://weather.tsukumijima.net/api/forecast/city/" + city_code # APIにリクエストするURLを作成


response = requests.get(url) # 作成したリクエスト用URLでアクセスして、responseに代入

weather_json = response.json() # responseにjson形式の天気のデータが返ってくるので、response.json()をweather_jsonに代入
now_hour = datetime.now().hour # 現在の天気情報取得のために、現在時刻の時間をnow_hourに代入

# 今日の天気はweather_json['forecasts'][0]['chanceOfRain']
# 明日の天気はweather_json['forecasts'][1]['chanceOfRain']
# 明後日の天気はweather_json['forecasts'][2]['chanceOfRain']
# にそれぞれ格納されている

# 天気の情報を0-6時、6-12時、12-18時、18-24時の4つに分けて降水確率を今日、明日、明後日の３日間の天気を返すため、場合分けする。
if 0 <= now_hour and now_hour < 6:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T00_06'] # 今日の0-6時の降水確率を取得し、weather_nowに代入
elif 6 <= now_hour and now_hour < 12:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T06_12'] # 今日の6-12時の降水確率を取得し、weather_nowに代入
elif 12 <= now_hour and now_hour < 18:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T12_18'] # 今日の12-18時の降水確率を取得し、weather_nowに代入
else:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T18_24'] # 今日の18-24時の降水確率を取得し、weather_nowに代入

# 現在時刻の降水確率をweather_now_textに代入
weather_now_text = "現在の降水確率 : " + weather_now
st.write(weather_now_text) # 現在時刻の降水確率を表示

# 今日、明日、明後日の降水確率をDadaFrameに代入
df1 = pd.DataFrame(weather_json['forecasts'][0]['chanceOfRain'],index=["今日"]) # index名を今日という文字列に設定
df2 = pd.DataFrame(weather_json['forecasts'][1]['chanceOfRain'],index=["明日"]) # index名を明日という文字列に設定
df3 = pd.DataFrame(weather_json['forecasts'][2]['chanceOfRain'],index=["明後日"]) # index名を明後日という文字列に設定

df = pd.concat([df1,df2,df3]) # 今日、明日、明後日の降水確率を結合して一覧にしてdfに代入
st.dataframe(df) # 一覧にした降水確率を表示


from openai import OpenAI
import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
# ここにご自身のAPIキーを入力してください！

API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)


# chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
def run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt):
    # リクエスト内容を決める
    request_to_gpt = f"{content_text_to_gpt} {content_maxStr_to_gpt} {content_kind_of_to_gpt}"

    
    # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    response =  client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": request_to_gpt },
        ],
    )

    # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    output_content = response.choices[0].message.content.strip()
    return output_content # 返って来たレスポンスの内容を返す

st.write('マリーアントワネットから貴方へ')# タイトル

# 書かせたい内容
content_text_to_gpt = '取得した天気の内容を１００字以内で伝えてください。'
            
# 書かせたい内容のテイストを選択肢として表示する
content_kind_of_to_gpt = "マリーアントワネットが貴族達に話しかける感じで現代に置き換えた内容として"

# chatGPTに出力させる文字数
content_maxStr_to_gpt = "100"

output_content_text = run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt)
st.write(output_content_text)