# Weather App (Flask) - GCP CI/CD 練習

這份專案使用 Cloud Run 部署 Flask 應用，並用 GitHub Actions 自動完成：
Build Docker image -> Push 到 Artifact Registry -> Deploy 到 Cloud Run

## 你需要準備
1. 已有 GCP 專案（Project）
2. 已有 GitHub repo（這份程式要 push 上去）
3. OpenWeather 的 API Key（`WEATHER_API_KEY`）

## 專案檔案重點
- `Dockerfile`：把 Flask app 容器化（Cloud Run 會用 `gunicorn` 跑）
- `.github/workflows/ci.yml`：GitHub Actions 的 CI/CD 流程
- `app.py`：改用 `PORT` 環境變數，並關閉 `debug`
- `requirements.txt`：加入 `gunicorn`（production 用 WSGI server）
- `.dockerignore`：避免把 `.env`、`.venv` 等檔案打進 image

## 在 GCP 建立資源（概念步驟）
以下名稱預設值會對應 `.github/workflows/ci.yml` 的 env：
- Cloud Run Service：`weather-app`
- Artifact Registry repo：`weather-app-repo`
- Artifact image 名稱：`weather-app`
- Secret Manager secret：`weather-api-key`
- Region：`asia-east1`

若你想用不同名稱，請改 `.github/workflows/ci.yml` 裡 deploy job 的 env。

### 1) 啟用 API
`Cloud Run`、`Artifact Registry`、`Secret Manager`。

### 2) 建立 Artifact Registry（Docker）
建立一個位置為 `asia-east1` 的 Docker repo（名稱用 `weather-app-repo` 或你自己在 workflow 設定的 `AR_REPO`）。

### 3) 建立 Secret Manager secret
建立一個 secret（名稱用 `weather-api-key` 或你自己在 workflow 設定的 `SECRET_NAME`），內容為你的 `WEATHER_API_KEY`。

### 4) 準備 GitHub Secrets
到 GitHub repo -> Settings -> Secrets and variables -> Actions，新增：

- `GCP_PROJECT_ID`：你的 GCP Project ID
- `GCP_SA_KEY`：GCP Service Account 金鑰 JSON（整段內容）

這個 Service Account 需具備權限：
- deploy Cloud Run
- push 到 Artifact Registry
- 讀取 Secret Manager secret（用於 `--set-secrets` 注入 `WEATHER_API_KEY`）

### 5) 觸發方式
workflow 在 `push` 到 `main` 時會自動：
1. 先跑測試（健康檢查與 compile）
2. Build Docker image
3. Push 到 Artifact Registry
4. Deploy 到 Cloud Run（允許未驗證呼叫）

## 部署後怎麼驗證
Cloud Run 部署完成後會有一個服務網址（例如 `https://xxx-...run.app`）：
- `GET /`：前端頁面
- `GET /health`：`{"status":"healthy"}`
- `GET /weather/Taipei`：回傳即時天氣 JSON

## 重要提醒（目前前端的小問題）
`templates/index.html` 裡的 `getCurrentLocation()` 使用 `YOUR_API_KEY` 直接打 OpenWeather reverse API。
你目前沒有後端/環境去替它填入 key，所以點「定位」可能會失敗。
（若你要，我也可以幫你把它改成由後端代呼叫或由伺服器注入 key。）

