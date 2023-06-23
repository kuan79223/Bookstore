from datetime import timedelta, datetime

from flask import Flask, abort, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = f'{secrets.token_hex()}'
app.permanent_session_lifetime = timedelta(minutes=5)

                                                        
app.config['SQLALCHEMY_BINDS'] = {'managers': 'sqlite:///managers.db'}
app.config['SECRET_KEY'] = f'{secrets.token_hex()}'

db = SQLAlchemy(app)


# 客戶清單
class Users(db.Model):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Integer)
    email = db.Column(db.String(30))
    phone = db.Column(db.String(12))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    order_user = db.relationship('Orders', backref='users', uselist=False)

# 書本清單
class Books(db.Model): 
   
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    order_book = db.relationship('Orders', backref='books', uselist=False)


# 訂單訊息:
class Orders(db.Model):

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    total = db.Column(db.Integer)

    address = db.Column(db.String(50))
    remark = db.Column(db.String(50))
    
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

# 管理員資料庫
class Admin(db.Model):

    __tablename__ = 'Admin'
    __bind_key__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    

with app.app_context():
    # db.drop_all()
    db.create_all()

    # 檢查管理員帳號是否已存在
    admin = Admin.query.filter_by(owner='manager').first()

    if admin is None:
        admin = Admin(owner='manager')
        admin.set_password('888')
        db.session.add(admin)
        db.session.commit()


    add_book = [
        Books(id=1, cover='book1.png', name='金獎剪輯師', price=299, 
                desc='金獎剪輯師的電影深層學！ 電影敘事 "17階段戲劇結構"類型電影心法攻略 《月老》、《紅衣小女孩》、《麻醉風暴》、《神算》…… 金獎剪輯師阿晟告訴你，電影都是如何說故事 如何才能逼出觀眾的大把眼淚……'),
        Books(id=2, cover='book2.png', name='先讓英雄救貓咪1+2套書', price=399,
                desc='史上最誠實的電影編劇指南 告訴你好萊塢賣座片是怎樣寫出來的！ 《先讓英雄救貓咪1：你這輩子唯一需要的電影編劇指南》 ★全球最多人討論的劇本破關祕笈 ★出版十年，締造指南書銷售傳奇 ……'),
        Books(id=3, cover='book3.png', name='先讓英雄救貓咪：你這輩子唯一需要的電影編劇指南', price=349,
                desc='史上最誠實的電影編劇指南 告訴你好萊塢賣座片是怎樣寫出來的！ ★全球最多人討論的劇本破關祕笈 ★出版十年，締造指南書銷售傳奇 ★年年蟬聯美國亞馬遜同類暢銷NO.1 ★長期攻占日本亞馬……')
    ]

    for book in add_book:
        existing_book = Books.query.filter_by(id=book.id).first()
        if existing_book is None:
            db.session.add(book)
            db.session.commit()

    @app.context_processor
    def inject_variables():

        if 'user' in session:

            # 同時符合
            found_user = Users.query.filter_by(account=session['user'], email=session['email']).first()

            if found_user:
                # app.logger.info('success login')

                return dict(logged_in=True)
            
        return dict(logged_in=False)

    @app.route('/', methods=['GET', 'POST'])
    def home():

        book_list = []
        if posting() and 'user' in session:

            user = Users.query.filter_by(account=session['user']).first()
            name = session['name']
            price = session['price']
            app.logger.info(f'從session中獲取書名與價格 : {name}{price}')

            amount = request.form['amount'] 
            address = request.form['address']
            remark = request.form['remark']
            book = Books.query.filter_by(name=name).first()
           
            # 確認有下數量，才加入資料庫
            if int(amount) > 0:
                
                total = int(amount) * price
                app.logger.info(f'前端輸入數量 : {amount} 單價: {price} 總額: {total}')
                order = Orders(user_id=user.id, book_id=book.id, amount=amount,address=address, remark=remark, total=total)
                order.status = 'complete'
                db.session.add(order)
                db.session.commit()

                app.logger.info(f'完成手續')
                
            return redirect(url_for('home'))
        else:
            context = inject_variables()  # 調用 inject_variables 函數獲取模板上下文
            return render_template('home.html', books=Books.query.all(), **context)  
                

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        
        if posting():
            session.permanent = True

            account = request.form['account']
            email = request.form['email']

            if not account or not email:
                abort(404, 'Missing information !')

            else:
                session['user'] = account
                session['email'] = email
                
                # 同時符合
                found_user = Users.query.filter_by(account=account, email=email).first()
                
                if found_user is None:
                    abort(404, 'Not found user !')
                
                else:
                    
                    app.logger.info(f'找到客戶資料返回home，帳戶:{found_user.account}信箱:{found_user.email}')

                    return redirect(url_for('home'))
        
        else:
            context = inject_variables()  # 調用 inject_variables 函數獲取模板上下文
            app.logger.info('沒有登入，進入登入畫面')
            return render_template('login.html', **context)


    @app.route('/index', methods=['GET', 'POST'])
    def index():
        
        if 'user' in session:

            account = session['user']
            email = session['email']

            found_user = Users.query.filter_by(account=account, email=email).first() 
            
            if found_user and getting():
            
                book_id = request.values.get('book_id')
                found_book = Books.query.filter_by(id=book_id).first()
                found_book.name, found_book.price
                print(found_book.name, found_book.price)
                session['name'] = found_book.name
                session['price'] =  found_book.price
                return render_template('index.html', cover=found_book.cover, name=found_book.name, price=found_book.price)    
                  
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

    @app.route('/apply_account', methods=['GET', 'POST'])
    def apply_account():
        
        if posting():

            account = request.form['account']
            email = request.form['email']
            phone = request.form['phone']
            exist_account = Users.query.filter_by(account=account).first()
            exist_email = Users.query.filter_by(email=email).first()
            exist_phone = Users.query.filter_by(phone=phone).first()

            if exist_account:
                app.logger.info('帳戶名稱已經存在')
                return render_template('apply_account.html', message='Account ID is exist, please try again!')
            elif exist_email:
                app.logger.info('信箱名稱已經存在')
                return render_template('apply_account.html', message='This email is exist, please try again!')
            elif exist_phone:
                app.logger.info('連絡電話已經存在')
                return render_template('apply_account.html', message='Your phone is exist, please try again!')
            
            else:
                user = Users(account=account, email=email, phone=phone)

                db.session.add(user)
                db.session.commit()
                app.logger.info('客戶資料不存在，將資料加進資料庫中')

            return redirect(url_for('login'))
        else:

            return render_template('apply_account.html')


    @app.route('/logout', methods=['GET'])
    def logout():

        session.clear()
        # 標記 Session 對象已被修改
        session.modified = True

        return redirect(url_for('home'))


    @app.route('/check_order', methods=['GET', 'POST'])
    def check_order():

        order_info = []

        if 'user' in session:
            account = session['user']
            email = session['email']
            found_user = Users.query.filter_by(account=account, email=email).first()

            if not found_user:
                return redirect(url_for('login'))
            
            else:
               
                if getting():
                    
                    orders = Orders.query.filter_by(user_id=found_user.id).all()
                    
                    for order in orders:
                        book = Books.query.filter_by(id=order.book_id).first()
                        # 確認訂單是否完成才能輸出
                        if order.status == 'complete':
                            
                            order_info.append({
                                'user_id': order.user_id,
                                '書名': book.name,
                                '數量': order.amount,
                                '價格': book.price,
                                '地址': order.address,
                                '總額': order.total,
                                '備註': order.remark,
                                '訂購時間':order.timestamp.strftime('%Y-%m-%d %H:%M:%S')    
                                            })
                               
                    return render_template('check_order.html', order_info=order_info)
                        
                else:
                                    
                    return render_template('check_order.html', order_info=order_info)              
        else:
            
            return redirect(url_for('login'))


    @app.route('/manager_login', methods=['GET', 'POST'])
    def manager_login():
        json_data = []

        if posting():

            owner = request.form['owner']
            password = request.form['password']

            admin = Admin.query.filter_by(owner=owner).first()
            
            if admin and admin.check_password(password):
                
                session['admin_id'] = admin.id
                
                datas = Orders.query.all()
                # 迭代每個資料記錄，將欄位資料組成字典並添加到列表中
                for data in datas:
                    json_data.append({
                        'ID': data.id,
                        '數量': data.amount,
                        '地址': data.address,
                        '總額': data.total,
                        'book_id': data.book_id,
                        'user_id': data.user_id,
                        '狀態': data.status,
                        '訂購時間': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        '備註': data.remark,
                    })
                app.logger.info('登入成功', datas)
                # 使用 jsonify 函式將資料轉換為 JSON 格式
                return render_template('admin_dashboard.html', datas=json_data)
            else:
                error_msg = 'Invalid username or password'
                app.logger.info('登入失敗', error_msg)
                return render_template('manager.html', error_msg=error_msg)
            
        else:
            return render_template('manager.html')

    # 自定義abort message
    @app.errorhandler(404)
    def page_not_found(error):
        message = error.description  # 取得自定義錯誤訊息
        return render_template('error.html', message=message), 404


def getting():
    return request.method == 'GET'

def posting():
    return request.method == 'POST'



if __name__ == '__main__':
    
    app.logger.setLevel(logging.INFO)
    file_handler = RotatingFileHandler('app.log', encoding='utf-8', maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    app.logger.addHandler(file_handler)

    app.run(host='0.0.0.0', port=5000)

    
    
    