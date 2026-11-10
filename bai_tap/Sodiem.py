import csv
import io
from flask import Flask, jsonify, request, url_for, render_template, abort, redirect, make_response

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
    
    return render_template(
        "index.html",
        page="home",
        so_sv=so_sv,
        so_lop=so_lop,
        link_students=url_for('student_list'),
        link_api=url_for('api_students')
    )

@app.route("/students", endpoint="student_list")
def student_list():
    all_classes = sorted(list({info["Lop"] for info in STUDENTS.values() if "Lop" in info}))
    filter_lop = request.args.get("lop", "").strip().upper()
    
    filtered_students = {}
    for mssv, info in STUDENTS.items():
        student_lop = info.get("Lop", "").upper()
        if not filter_lop or student_lop == filter_lop:
            filtered_students[mssv] = info

    return render_template(
        "index.html",
        page="list",
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
    
    return render_template(
        "index.html",
        page="detail",
        student=student,
        mssv=mssv,
        dtb=dtb,
        xeploai=xeploai,
        short_link=url_for('redirect_student', mssv=mssv),
        export_link=url_for('export_student_csv', mssv=mssv)
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

    return render_template("index.html", page="search", q=q, results=results)

@app.route("/api/students", endpoint="api_students")
def api_students():
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True, port=8000)