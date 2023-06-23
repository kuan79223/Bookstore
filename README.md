# Flask 個人資料專案

這是一個使用 Python Flask 框架 與 html 的個人專案，讓使用者登入、即可購買書籍、查詢。  
管理員可登入後，看到後台的所有使用購買狀況。

## 使用虛擬環境 (venv)

建議在專案中使用虛擬環境來隔離專案所需的 Python 套件。

## 依賴套件

專案所需的 Python 套件列於 `requirements.txt` 檔案中。

## 建立虛擬環境與啟動

```shell
python -m venv venv
```

在 Windows 環境中，啟動虛擬環境：

```shell
venv\Scripts\activate
```

在 macOS/Linux 環境中，啟動虛擬環境：

```shell
source venv/bin/activate
```

## 安裝所需套件與啟動應用程式

```shell
python -m venv venv
pip install -r requirements.txt
python app.py
```

在瀏覽器中訪問 [http://localhost:5000](http://localhost:5001) 即可使用應用程式。  
訪問 [http://localhost:5000/manager_login](http://127.0.0.1:5000/manager_login) 即可登入管理員查看所有訂單資料。

    管理員ID為: manager    
    密碼為: 888  
