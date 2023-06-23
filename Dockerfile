# 選擇基礎映像
FROM python:3.9

# 設定工作目錄為/app
WORKDIR /app

# 複製專案代碼到容器中的/app目錄
COPY . /app

# 安裝相關套件
RUN pip install -r requirements.txt

# 監聽 port 號
EXPOSE 5000

# 定義容器啟動後要執行的命令
CMD ["python", "app.py"]