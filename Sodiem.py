import csv
import io
from flask import Flask, jsonify, request, url_for, render_template_string, abort, redirect, make_response

app = Flask(__name__)

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "Lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.07}
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "Lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "Lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.07}
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng", 
        "Lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "Lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "Lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.03}
    }
}

def calculate_grade(scores):
    if not scores:
        return "-", "-"
    
    avg = sum(scores.values()) / len(scores)
    avg_rounded = round(avg, 2)
    
    if avg_rounded >= 8.0:
        rank = "Giỏi"
    elif avg_rounded >= 6.5:
        rank = "Khá"
    elif avg_rounded >= 5.0:
        rank = "Trung bình"
    else:
        rank = "Yếu"
        
    return avg_rounded, rank

@app.route("/", endpoint="home")
def home():
    so_sv = len(STUDENTS)
    so_lop = len({info["Lop"] for info in STUDENTS.values() if "Lop" in info})
    
    link_students = url_for('student_list')
    link_api = url_for('api_students')
    
    return f"""
    <p>số sinh viên: {so_sv}</p>
    <p>số lớp: {so_lop}</p>
    <p>Liên kết:</p>
    <ul>
        <li><a href="{link_students}">{link_students}</a></li>
        <li><a href="{link_api}">{link_api}</a></li>
    </ul>
    """

@app.route("/students", endpoint="student_list")
def student_list():
    all_classes = sorted(list({info["Lop"] for info in STUDENTS.values() if "Lop" in info}))
    filter_lop = request.args.get("lop", "").strip().upper()
    
    filtered_students = {}
    for mssv, info in STUDENTS.items():
        student_lop = info.get("Lop", "").upper()
        if not filter_lop or student_lop == filter_lop:
            filtered_students[mssv] = info

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Danh sách sinh viên</title>
        <style>
            table { border-collapse: collapse; width: 80%; margin-top: 15px; }
            th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
            th { background-color: #f2f2f2; }
            .filter-bar { margin-bottom: 15px; }
            .filter-bar a { margin-right: 10px; text-decoration: none; color: blue; }
            .filter-bar a.active { font-weight: bold; text-decoration: underline; color: red; }
        </style>
    </head>
    <body>
        <h2>DANH SÁCH SINH VIÊN</h2>
        
        <div class="filter-bar">
            Lọc theo lớp: 
            <a href="{{ url_for('student_list') }}" class="{{ 'active' if not current_filter else '' }}">Tất cả</a>
            {% for c in all_classes %}
                | <a href="{{ url_for('student_list', lop=c) }}" class="{{ 'active' if current_filter == c.upper() else '' }}">{{ c }}</a>
            {% endfor %}
        </div>

        {% if filtered_students %}
        <table>
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {% for mssv, info in filtered_students.items() %}
                {% set dtb, xeploai = get_grade(info.scores) %}
                <tr>
                    <td><a href="{{ url_for('student_detail', mssv=mssv) }}">{{ mssv }}</a></td>
                    <td>{{ info.name }}</td>
                    <td>{{ info.Lop }}</td>
                    <td>{{ dtb }}</td>
                    <td>{{ xeploai }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: red; font-style: italic;">Không có sinh viên phù hợp.</p>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(
        template, 
        filtered_students=filtered_students, 
        all_classes=all_classes, 
        current_filter=filter_lop,
        get_grade=calculate_grade
    )

@app.route("/students/<mssv>", endpoint="student_detail")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    student = STUDENTS[mssv]
    dtb, xeploai = calculate_grade(student["scores"])
    
    short_link = url_for('redirect_student', mssv=mssv)
    export_link = url_for('export_student_csv', mssv=mssv)
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Chi tiết sinh viên</title>
        <style>
            table { border-collapse: collapse; width: 50%; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
            th { background-color: #f2f2f2; }
            .meta-info { margin-top: 15px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h2>THÔNG TIN SINH VIÊN</h2>
        <p><strong>Họ tên:</strong> {{ student.name }}</p>
        <p><strong>MSSV:</strong> {{ mssv }}</p>
        <p><strong>Lớp:</strong> <a href="{{ url_for('student_list', lop=student.Lop) }}">{{ student.Lop }}</a></p>
        <p><strong>Điểm TB:</strong> {{ dtb }}</p>
        <p><strong>Xếp loại:</strong> {{ xeploai }}</p>
        
        <div class="meta-info">
            <p><strong>Link rút gọn:</strong> <a href="{{ short_link }}">{{ short_link }}</a></p>
            <p><a href="{{ export_link }}" style="font-weight: bold; color: green;">📥 Tải bảng điểm (CSV)</a></p>
        </div>

        <h3>Bảng điểm từng học phần:</h3>
        {% if student.scores %}
        <table>
            <thead>
                <tr>
                    <th>Môn học</th>
                    <th>Điểm</th>
                </tr>
            </thead>
            <tbody>
                {% for subject, score in student.scores.items() %}
                <tr>
                    <td>{{ subject }}</td>
                    <td>{{ score }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p><em>Chưa có điểm học phần nào.</em></p>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(
        template,
        student=student,
        mssv=mssv,
        dtb=dtb,
        xeploai=xeploai,
        short_link=short_link,
        export_link=export_link
    )

@app.route("/sv/<mssv>", endpoint="redirect_student")
def redirect_student(mssv):
    return redirect(url_for('student_detail', mssv=mssv), code=301)

@app.route("/students/<mssv>/export", endpoint="export_student_csv")
def export_student_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    student = STUDENTS[mssv]
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["hoc_phan", "diem"])
    
    for subject, score in student["scores"].items():
        writer.writerow([subject, score])
        
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    
    return response

@app.route("/search", endpoint="search_students")
def search_students():
    q = request.args.get("q", "")
    results = {}
    
    if q.strip():
        q_lower = q.lower()
        for mssv, info in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in info["name"].lower():
                results[mssv] = info

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Tìm kiếm sinh viên</title>
    </head>
    <body>
        <h2>TÌM KIẾM SINH VIÊN</h2>
        <form action="{{ url_for('search_students') }}" method="GET">
            <input type="text" name="q" value="{{ q }}" placeholder="Nhập tên hoặc MSSV...">
            <button type="submit">Tìm kiếm</button>
        </form>
        <br>
        {% if q %}
            <p>Tìm thấy {{ results|length }} kết quả cho "{{ q }}"</p>
            <ul>
            {% for mssv, info in results.items() %}
                <li>
                    <a href="{{ url_for('student_detail', mssv=mssv) }}">{{ info.name }} ({{ mssv }})</a> - Lớp: {{ info.Lop }}
                </li>
            {% endfor %}
            </ul>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(template, q=q, results=results)

@app.route("/api/students", endpoint="api_students")
def api_students():
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True, port=8000)