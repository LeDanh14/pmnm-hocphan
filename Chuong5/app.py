from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp

app = Flask(__name__)
app.secret_key = 'secret_key_chuong5'
app.permanent_session_lifetime = timedelta(days=30)

USERS = {
    "admin": "admin123",
    "an": "an123456"
}

def quy_doi_diem_chu(diem_10):
    if diem_10 >= 8.5: return 'A'
    elif diem_10 >= 7.0: return 'B'
    elif diem_10 >= 5.5: return 'C'
    elif diem_10 >= 4.0: return 'D'
    else: return 'F'

class RegisterForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập.'),
        Length(min=4, max=20, message='Tên đăng nhập phải từ 4 đến 20 ký tự.'),
        Regexp(r'^[a-z0-9_]+$', message='Chỉ chấp nhận chữ thường không dấu, số, dấu gạch dưới.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email.'),
        Email(message='Email không đúng định dạng.')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu.'),
        Length(min=8, message='Mật khẩu tối thiểu 8 ký tự.')
    ])
    confirm_password = PasswordField('Nhập lại mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập lại mật khẩu.'),
        EqualTo('password', message='Mật khẩu nhập lại không khớp.')
    ])
    agree_terms = BooleanField('Tôi đồng ý với các điều khoản', validators=[
        DataRequired(message='Bạn phải đồng ý với điều khoản.')
    ])
    submit = SubmitField('Đăng ký')

    def validate_username(self, field):
        if field.data in USERS:
            raise ValidationError('Tên đăng nhập đã được sử dụng.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    old_username = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            session.permanent = bool(remember)
            flash(f"Đăng nhập thành công. Xin chào {username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")
            old_username = username
    return render_template('login.html', old_username=old_username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        USERS[form.username.data] = form.password.data
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash("Vui lòng đăng nhập để xem Profile.", "warning")
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for('index'))

@app.route('/calc', methods=['GET', 'POST'])
def calculator():
    a_str, b_str, op, calc_result = '', '', '+', None
    if request.method == 'POST':
        a_str = request.form.get('a', '').strip()
        b_str = request.form.get('b', '').strip()
        op = request.form.get('op', '+')
        try:
            a = float(a_str.replace(',', '.'))
            b = float(b_str.replace(',', '.'))
            res_val = None
            if op == '+': res_val = a + b
            elif op == '-': res_val = a - b
            elif op == '*': res_val = a * b
            elif op == '/':
                if b != 0: res_val = a / b
                else: calc_result = "Lỗi chia 0"
            if res_val is not None:
                if res_val.is_integer(): res_val = int(res_val)
                a_display = int(a) if a.is_integer() else a
                b_display = int(b) if b.is_integer() else b
                calc_result = f"{a_display} {op} {b_display} = {res_val}"
        except ValueError:
            calc_result = "Lỗi nhập liệu"
    return render_template('maytinh.html', a=a_str, b=b_str, op=op, calc_result=calc_result)

@app.route('/score', methods=['GET', 'POST'])
def score():
    cc_str, gk_str, ck_str, score_result = '', '', '', None
    if request.method == 'POST':
        cc_str = request.form.get('cc', '').strip()
        gk_str = request.form.get('gk', '').strip()
        ck_str = request.form.get('ck', '').strip()
        try:
            cc = float(cc_str.replace(',', '.'))
            gk = float(gk_str.replace(',', '.'))
            ck = float(ck_str.replace(',', '.'))
            if not (0 <= cc <= 10 and 0 <= gk <= 10 and 0 <= ck <= 10):
                score_result = "Lỗi: Điểm phải từ 0 đến 10"
            else:
                tong_ket = cc * 0.1 + gk * 0.3 + ck * 0.6
                tong_ket_round = round(tong_ket, 2)
                diem_chu = 'F' if ck < 1.0 else quy_doi_diem_chu(tong_ket_round)
                score_result = f"{tong_ket_round} (Điểm chữ: {diem_chu})"
        except ValueError:
            score_result = "Lỗi nhập liệu số"
    return render_template('tinhdiem.html', cc=cc_str, gk=gk_str, ck=ck_str, score_result=score_result)

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    cao_str, nang_str = '', ''
    err_cao, err_nang = None, None
    bmi_result, bmi_status, bmi_color, target_weight = None, None, None, None
    if request.method == 'POST':
        cao_str = request.form.get('cao', '').strip()
        nang_str = request.form.get('nang', '').strip()
        if not cao_str: err_cao = "Lỗi ô chiều cao: Vui lòng không để trống"
        else:
            try:
                cao = float(cao_str.replace(',', '.'))
                if not (50 <= cao <= 250): err_cao = "Lỗi ô chiều cao: Giá trị phải từ 50 đến 250."
            except ValueError: err_cao = "Lỗi ô chiều cao: Vui lòng nhập một số."
        if not nang_str: err_nang = "Lỗi ô cân nặng: Vui lòng không để trống"
        else:
            try:
                nang = float(nang_str.replace(',', '.'))
                if not (10 <= nang <= 300): err_nang = "Lỗi ô cân nặng: Giá trị phải từ 10 đến 300."
            except ValueError: err_nang = "Lỗi ô cân nặng: Vui lòng nhập một số."
        if not err_cao and not err_nang:
            h_m = cao / 100
            bmi = round(nang / (h_m ** 2), 1)
            min_w = round(18.5 * (h_m ** 2), 1)
            max_w = round(22.9 * (h_m ** 2), 1)
            bmi_result = bmi
            target_weight = f"nên có {min_w} - {max_w} kg"
            if bmi < 18.5: bmi_status, bmi_color = "Thiếu cân", "text-warning"
            elif bmi < 23: bmi_status, bmi_color = "Bình thường", "text-success"
            elif bmi < 25: bmi_status, bmi_color = "Thừa cân", "text-warning"
            else: bmi_status, bmi_color = "Béo phì", "text-danger"
    return render_template('bmi.html', cao=cao_str, nang=nang_str, err_cao=err_cao, err_nang=err_nang, bmi_result=bmi_result, bmi_status=bmi_status, bmi_color=bmi_color, target_weight=target_weight)

if __name__ == '__main__':
    app.run(debug=True, port=5000)