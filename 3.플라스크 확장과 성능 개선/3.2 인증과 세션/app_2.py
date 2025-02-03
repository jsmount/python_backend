# 세션을 이용한 상태 관리
from flask import Flask, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user

app = Flask(__name__)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/flaskdb'
# 수정 추척 기능을 비활성화합니다. (성능상의 이유로 권장합니다.)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Flask 애플리케이션을 위한 비밀 키 설정
app.config['SECRET_KEY'] = 'mysecretkey'

db = SQLAlchemy(app) # SQLAlchemy 인스턴스 생성

login_manager = LoginManager() # Flask-Login의 LoginManager 인스턴스 생성
login_manager.init_app(app) # 애플리케이션에 LoginManager 적용
login_manager.login_view = 'login' # 로그인 페이지의 뷰 함수 이름을 설정합니다.

# 사용자 모델 정의
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # 사용자의 ID, 고유 식별자
    username = db.Column(db.String(80), unique=True, nullable=False) # 사용자 이름, 고유해야 함
    email = db.Column(db.String(120), unique=True, nullable=False) # 사용자 이메일, 고유해야 함
    password = db.Column(db.String(128)) # 사용자 비밀번호

    # 객체의 문자열 표현을 정의합니다.
    def __repr__(self):
        return f'<User {self.username}>'

# 사용자 ID로 사용자를 로드하는 콜백 함수를 정의합니다.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
# 애플리케이션 컨텍스트 안에서 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()

# 인덱스 뷰를 정의합니다.
@app.route('/')
def index():
    user_id = session.get('user_id') # 세션에서 user_id를 가져옵니다.
    if user_id:
        user = User.query.get(user_id)
        return f'Logged in as {user.username}' # 로그인된 상태를 표시합니다.
    return 'You are not logged in' # 로그인되지 않은 상태를 표시합니다.

# 보호된 페이지를 위한 뷰를 정의합니다.
@app.route('/protected')
@login_required # 로그인이 필요하다는 데코레이터
def protected():
    # 현재 로그인한 사용자의 이름을 표시합니다.
    return f'Logged in as {current_user.username}'

# 로그인 뷰를 정의합니다.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 폼 데이터로부터 사용자 이름과 비밀번호를 가져옵니다.
        username = request.form['username']
        password = request.form['password']
        # 데이터베이스에서 사용자를 조회합니다.
        user = User.query.filter_by(username=username).first()
        # 사용자가 존재하고 비밀번호가 맞다면
        if user and user.password == password:
            login_user(user) # 사용자를 로그인시킵니다.
            session['user_id'] = user.id # 세션에 user_id를 저장합니다.
            return redirect(url_for('protected')) # 보호된 페이지로 리다이렉트합니다.
    return '''
        <form method="post">
            Username: <input type='text' name='username'><br>
            Password: <input type='password' name='password'><br>
            <input type='submit' value='Login'>
        </form>    
        '''

# 로그아웃 뷰를 정의합니다.
@app.route('/logout')
@login_required
def logout():
    logout_user() # 사용자를 로그아웃시킵니다.
    session.pop('user_id', None) # 세션에서 user_id를 제거시킵니다.
    return redirect(url_for('index'))

@app.route('/create_test_user')
def create_test_user():
    test_user = User(username='testuser', email='test@example.com', password='testpassword') # 테스트 사용자 생성
    db.session.add(test_user)
    db.session.commit() # 데이터베이스에 테스트 사용자 추가
    return 'Test User created' # 사용자 생성 완료 메시지 반환

if __name__ == '__main__':
    app.run(debug=False)