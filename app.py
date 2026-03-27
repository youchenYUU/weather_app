from flask import Flask, jsonify, render_template, request
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 新增前端頁面路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather/<city>')
def get_weather(city):
    api_key = os.getenv('WEATHER_API_KEY') or app.config.get('WEATHER_API_KEY')
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"]
        }
        return jsonify(weather_data)
    except Exception as e:
        print(f"Error: {str(e)}")  # 增加日誌
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/forecast/<city>')
def get_forecast(city):
    api_key = os.getenv('WEATHER_API_KEY') or app.config.get('WEATHER_API_KEY')
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500
        
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # 處理數據，每天取一個時間點 (正午)
        processed_data = []
        days_processed = set()
        
        for item in data['list']:
            date = item['dt_txt'].split(' ')[0]
            # 每天只取一個時間點的數據
            if date not in days_processed and '12:00:00' in item['dt_txt']:
                days_processed.add(date)
                processed_data.append({
                    'date': date,
                    'temp': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon']
                })
                
                # 取得5天數據即可
                if len(processed_data) >= 5:
                    break
        
        return jsonify(processed_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/historical/<city>')
def get_historical(city):
    # 通常需要付費API或模擬歷史資料
    # 這裡為了範例，我們生成模擬資料
    api_key = os.getenv('WEATHER_API_KEY') or app.config.get('WEATHER_API_KEY')
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500
    
    # 首先獲取當前天氣，生成模擬歷史資料
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        current_data = response.json()
        
        current_temp = current_data['main']['temp']
        current_humidity = current_data['main']['humidity']
        
        # 生成過去7天的模擬數據 (實際專案中應使用真實歷史API)
        historical_data = []
        import random
        import datetime
        
        today = datetime.date.today()
        
        for i in range(7, 0, -1):
            day = today - datetime.timedelta(days=i)
            # 隨機變化在合理範圍內的歷史溫度
            temp_variation = random.uniform(-3, 3)
            humidity_variation = random.uniform(-10, 10)
            
            historical_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'temp': round(current_temp + temp_variation, 1),
                'humidity': round(min(max(current_humidity + humidity_variation, 0), 100), 1)
            })
            
        return jsonify(historical_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)