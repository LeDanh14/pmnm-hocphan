from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return '<p>Đây là Trang chủ. Bấm vào <a href="/about">Giới thiệu</a> để xem trang About.</p>'

# Route gọi chạy file about.html
@app.route("/about")
def about():
    return render_template("about.html")
# Thêm route này vào view.py
@app.route("/contact", endpoint="contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)