import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.title("天気アプリ")

# 選択肢を作成
city_code_list = {
    "盛岡市":"030010",
    "東京":"130010"
}

city_code_index = st.selectbox("地域を選んでください。", options=list(city_code_list.keys()), index=0)
city_code = city_code_list[city_code_index] # 選択したキーからAPIのリクエストに使うcityコードに変換し、city_codeに代入

city_code = city_code_list[city_code_index]  # 選択したキーからAPIのリクエストに使うcityコードに変換し、city_codeに代入

url = "https://weather.tsukumijima.net/api/forecast/city/" + city_code  # APIにリクエストするURLを作成

response = requests.get(url)  # 作成したリクエスト用URLでアクセスして、responseに代入

weather_json = response.json()  # responseにjson形式の天気のデータが返ってくるので、response.json()をweather_jsonに代入
now_hour = datetime.now().hour  # 現在の天気情報取得のために、現在時刻の時間をnow_hourに代入


# 天気の情報を0-6時、6-12時、12-18時、18-24時の4つに分けて降水確率を取得
if 0 <= now_hour < 6:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T00_06']
elif 6 <= now_hour < 12:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T06_12']
elif 12 <= now_hour < 18:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T12_18']
else:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T18_24']

# 現在時刻の降水確率を表示
weather_now_text = "現在の降水確率 : " + weather_now
st.write(weather_now_text)

# 時間帯ラベルをマッピングする辞書
time_labels = {
    "T00_06": "0時～6時",
    "T06_12": "6時～12時",
    "T12_18": "12時～18時",
    "T18_24": "18時～24時"
}

# 今日、明日、明後日の降水確率をDataFrameに代入
df1 = pd.DataFrame(weather_json['forecasts'][0]['chanceOfRain'], index=["今日"])
df2 = pd.DataFrame(weather_json['forecasts'][1]['chanceOfRain'], index=["明日"])
df3 = pd.DataFrame(weather_json['forecasts'][2]['chanceOfRain'], index=["明後日"])

# DataFrameを結合
df = pd.concat([df1, df2, df3])

# 列名を「T00_06」などから「0時～6時」などに変更
df.rename(columns=time_labels, inplace=True)

# 表示
st.write("降水確率")
st.dataframe(df)

# 最高気温と最低気温を取得 
def get_temperature_data(forecast):
    max_temp = forecast['temperature']['max']['celsius'] if forecast['temperature']['max'] else "N/A"
    min_temp = forecast['temperature']['min']['celsius'] if forecast['temperature']['min'] else "N/A"
    return {"最高気温 (°C)": max_temp, "最低気温 (°C)": min_temp}

# 今日、明日、明後日の最高気温と最低気温をDataFrameにまとめる
temp_data = {
    "日付": ["今日", "明日", "明後日"],
    "最高気温 (°C)": [],
    "最低気温 (°C)": []
}

for forecast in weather_json['forecasts']:
    temp_info = get_temperature_data(forecast)
    temp_data["最高気温 (°C)"].append(temp_info["最高気温 (°C)"])
    temp_data["最低気温 (°C)"].append(temp_info["最低気温 (°C)"])

temp_df = pd.DataFrame(temp_data)

# インデックスを削除して再表示
st.write("最高気温と最低気温")
temp_df_no_index = temp_df.set_index("日付")  # "日付" 列をインデックスに設定して表示
st.dataframe(temp_df_no_index)


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

# 全ての入力値をまとめて1つの変数に格納
content_text_to_gpt =(
    f"私はマリーアントワネットです。\n"
    f"{city_code}の場所の{weather_now_text}と{temp_data}を基に天気情報を８０字以内で書いてください。場所の表示は不要です。\n"
)

            
# 書かせたい内容のテイストを選択肢として表示する
content_kind_of_to_gpt =   "マリーアントワネットが貴族達に話しかける想定で現代に置き換えた内容としてユーモアを交えて"

# chatGPTに出力させる文字数
content_maxStr_to_gpt = "4"

output_content_text = run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt)
st.write(output_content_text)

st.text