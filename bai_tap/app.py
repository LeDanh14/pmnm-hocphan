from flask import Flask
from flask import Flask, jsonify, url_for
from werkzeug.routing import BaseConverter, ValidationError
app = Flask(__name__)

@app.route("/")
@app.route("/home")
@app.route("/index")
def hello():
    return "Hello world"    

@app.route("/chia-nhom")
def chia_nhom():
    so_bai = 12
    so_nhom = 0 
    return f"Mỗi nhóm làm {so_bai / so_nhom} bài"

@app.route("/user/<username>")
def user_profile(username):
    rs=f"Xin chào bạn{username}"
    return rs

@app.route("/square/<float:x>")
def square(x):
        return f"bình phương của{x} là: {x**2}"




# 1. Định nghĩa Custom Converter
class ListConverter(BaseConverter):
    # Matches các số nguyên (có thể mang dấu âm) phân cách bằng dấu phẩy
    regex = r"-?\d+(?:,-?\d+)*"

    def to_python(self, value):
        # Chuyển chuỗi URL thành danh sách số nguyên
        try:
            return [int(x) for x in value.split(",")]
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        # Chuyển danh sách số nguyên ngược lại thành chuỗi URL
        if isinstance(value, list):
            return ",".join(str(x) for x in value)
        return str(value)

# 2. Đăng ký converter với Flask app
app.url_map.converters["list"] = ListConverter

# 3. Định nghĩa Route /sum/<list:numbers>
@app.route("/sum/<list:numbers>", endpoint="sum_numbers")
def sum_numbers(numbers):
    return jsonify({
        "numbers": numbers,
        "sum": sum(numbers)
    })



if __name__ == "__main__":
    app.run(debug=True, port=8000)