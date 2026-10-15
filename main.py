import sqlite3
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# تصميم الواجهة مدمج مباشرة لمنع أي خطأ في المجلدات
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم - طلبات سند</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f7f6; padding: 20px; direction: rtl; }
        h1 { color: #0086cc; text-align: center; }
        table { width: 100%; border-collapse: collapse; background: white; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: center; }
        th { background-color: #0086cc; color: white; }
        .btn-approve { background-color: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
        .btn-reject { background-color: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>لوحة تحكم المسؤول - طلبات منصة سند</h1>
    <table>
        <thead>
            <tr>
                <th>الرقم</th>
                <th>الرقم الوطني</th>
                <th>رقم الهاتف</th>
                <th>نوع الخدمة</th>
                <th>الحالة</th>
                <th>تاريخ الطلب</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            {% for req in requests %}
            <tr>
                <td>{{ req[0] }}</td>
                <td>{{ req[1] }}</td>
                <td>{{ req[2] }}</td>
                <td>{{ req[3] }}</td>
                <td><b>{{ req[4] }}</b></td>
                <td>{{ req[5] }}</td>
                <td>
                    <button class="btn-approve" onclick="updateStatus({{ req[0] }}, 'Approved')">قبول</button>
                    <button class="btn-reject" onclick="updateStatus({{ req[0] }}, 'Rejected')">رفض</button>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="7">لا توجد طلبات مسجلة حالياً.</td></tr>
            {% endfor %}
        </tbody>
    </table>

    <script>
        function updateStatus(reqId, status) {
            fetch('/update_status/' + reqId + '/' + status, { method: 'POST' })
            .then(res => res.json())
            .then(data => { if(data.status === 'success') location.reload(); });
        }
    </script>
</body>
</html>
"""


def init_db():
    conn = sqlite3.connect("sanad.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            national_id TEXT,
            service_type TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return "مرحباً بك في منصة سند الذكية"


@app.route("/admin")
def admin_dashboard():
    conn = sqlite3.connect("sanad.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, national_id, service_type, status, created_at FROM"
        " service_requests ORDER BY created_at DESC"
    )
    raw_data = cursor.fetchall()
    conn.close()

    requests_list = []
    for row in raw_data:
        requests_list.append((row[0], row[1], "غير متوفر", row[2], row[3], row[4]))

    return render_template_string(ADMIN_HTML, requests=requests_list)


@app.route("/update_status/<int:req_id>/<status>", methods=["POST"])
def update_status(req_id, status):
    if status not in ["Approved", "Rejected"]:
        return jsonify({"status": "error", "message": "حالة غير صالحة"}), 400

    conn = sqlite3.connect("sanad.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE service_requests SET status = ? WHERE id = ?", (status, req_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "تم التحديث بنجاح"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
