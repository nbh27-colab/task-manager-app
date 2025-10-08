import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Task Manager", layout="wide")
st.title("📋 Quản Lý Tác Vụ Thông Minh")

# Tabs for different features
tabs = st.tabs(["Dashboard", "Tác vụ", "Dự án", "Danh mục", "Người dùng"])

# ----------------------- TÁC VỤ -----------------------
with tabs[1]:
    st.header("📝 Danh sách tác vụ")

    # Form to create a new task
    with st.form("create_task"):
        title = st.text_input("Tiêu đề")
        description = st.text_area("Mô tả")
        due_date = st.date_input("Hạn hoàn thành")
        status = st.selectbox("Trạng thái", ["todo", "in progress", "done"])
        category_id = st.number_input("ID Danh mục", min_value=1, step=1)
        project_id = st.number_input("ID Dự án", min_value=1, step=1)
        col1, col2, col3 = st.columns(3)
        classify_clicked = col1.form_submit_button("Phân loại")
        estimate_clicked = col2.form_submit_button("Ước tính thời gian")
        submitted = col3.form_submit_button("➕ Thêm tác vụ")

        if classify_clicked and description:
            ai_payload = {"task_id": title or "tmp_id", "description": description}
            try:
                category_res = requests.post(f"{API_URL}/ai/classify", json=ai_payload)
                if category_res.status_code == 200:
                    category = category_res.json().get("category", "Không rõ")
                    st.info(f"🔍 Danh mục gợi ý: `{category}`")
                else:
                    st.error("❌ Lỗi khi gọi AI service.")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")

        if estimate_clicked and description:
            ai_payload = {"task_id": title or "tmp_id", "description": description}
            try:
                time_res = requests.post(f"{API_URL}/ai/estimate-time", json=ai_payload)
                if time_res.status_code == 200:
                    minutes = time_res.json().get("estimated_minutes", "N/A")
                    st.info(f"⏱ Thời gian ước lượng: **{minutes} phút**")
                else:
                    st.error("❌ Lỗi khi gọi AI service.")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")

        if submitted:
            ai_payload = {"task_id": title or "tmp_id", "description": description}
            try:
                requests.post(f"{API_URL}/ai/embed", json=ai_payload)
                response = requests.post(f"{API_URL}/tasks/", json={
                    "title": title,
                    "description": description,
                    "due_date": datetime.combine(due_date, datetime.min.time()).isoformat(),
                    "status": status,
                    "category_id": int(category_id),
                    "project_id": int(project_id),
                })
                if response.status_code == 200:
                    st.success("✅ Tác vụ đã được thêm thành công!")
                else:
                    st.error(f"❌ Lỗi khi thêm tác vụ! Status: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Lỗi khi gọi API tác vụ: {e}")

    # Show all tasks
    st.subheader("📋 Danh sách tác vụ hiện có")
    try:
        res = requests.get(f"{API_URL}/tasks/")
        if res.status_code == 200:
            tasks = res.json()
            for task in tasks:
                with st.expander(f"{task['title']} ({task['status']})"):
                    st.write(f"📅 Hạn: {task['due_date']}")
                    st.write(f"📂 Danh mục ID: {task['category_id']}, 📁 Dự án ID: {task['project_id']}")
                    st.write(f"✏️ {task['description']}")
        else:
            st.warning(f"⚠️ Không thể tải tác vụ. Status: {res.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi gọi API tác vụ: {e}")

# ----------------------- DỰ ÁN -----------------------
with tabs[2]:
    st.header("📁 Quản lý Dự án")
    project_name = st.text_input("Tên dự án mới")
    if st.button("Thêm dự án"):
        try:
            res = requests.post(f"{API_URL}/projects/", json={"name": project_name})
            if res.status_code == 200:
                st.success("✅ Dự án đã được thêm!")
            else:
                st.error(f"❌ Thêm dự án thất bại! Status: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Lỗi khi gọi API dự án: {e}")

    st.subheader("Danh sách Dự án")
    try:
        res = requests.get(f"{API_URL}/projects/")
        if res.status_code == 200:
            projects = res.json()
            st.table(projects)
        else:
            st.warning(f"⚠️ Không thể tải danh sách dự án. Status: {res.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi gọi API dự án: {e}")

# ----------------------- DANH MỤC -----------------------
with tabs[3]:
    st.header("📂 Quản lý Danh mục")
    cat_name = st.text_input("Tên danh mục mới")
    if st.button("Thêm danh mục"):
        try:
            res = requests.post(f"{API_URL}/categories/", json={"name": cat_name})
            if res.status_code == 200:
                st.success("✅ Danh mục đã được thêm!")
            else:
                st.error(f"❌ Thêm danh mục thất bại! Status: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Lỗi khi gọi API danh mục: {e}")

    st.subheader("Danh sách Danh mục")
    try:
        res = requests.get(f"{API_URL}/categories/")
        if res.status_code == 200:
            categories = res.json()
            st.table(categories)
        else:
            st.warning(f"⚠️ Không thể tải danh sách danh mục. Status: {res.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi gọi API danh mục: {e}")

# ----------------------- NGƯỜI DÙNG -----------------------
with tabs[4]:
    st.header("👤 Quản lý Người dùng")
    user_name = st.text_input("Tên người dùng mới")
    if st.button("Thêm người dùng"):
        try:
            res = requests.post(f"{API_URL}/users/", json={"name": user_name})
            if res.status_code == 200:
                st.success("✅ Người dùng đã được thêm!")
            else:
                st.error(f"❌ Thêm người dùng thất bại! Status: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Lỗi khi gọi API người dùng: {e}")

    st.subheader("Danh sách Người dùng")
    try:
        res = requests.get(f"{API_URL}/users/")
        if res.status_code == 200:
            users = res.json()
            st.table(users)
        else:
            st.warning(f"⚠️ Không thể tải danh sách người dùng. Status: {res.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi gọi API người dùng: {e}")

# ----------------------- DASHBOARD -----------------------
with tabs[0]:
    st.header("📊 Dashboard Tổng hợp")
    col1, col2, col3, col4 = st.columns(4)
    try:
        tasks = requests.get(f"{API_URL}/tasks/").json()
        projects = requests.get(f"{API_URL}/projects/").json()
        categories = requests.get(f"{API_URL}/categories/").json()
        users = requests.get(f"{API_URL}/users/").json()
        col1.metric("Tổng số tác vụ", len(tasks))
        col2.metric("Tổng số dự án", len(projects))
        col3.metric("Tổng số danh mục", len(categories))
        col4.metric("Tổng số người dùng", len(users))
        # Thống kê trạng thái tác vụ
        status_count = {"todo": 0, "in progress": 0, "done": 0}
        for t in tasks:
            status_count[t.get("status", "todo")] += 1
        st.subheader("Thống kê trạng thái tác vụ")
        st.bar_chart(status_count)
        # Thống kê thời gian ước lượng nếu có
        est_times = [t.get("estimated_minutes") for t in tasks if t.get("estimated_minutes")]
        if est_times:
            st.subheader("Phân bố thời gian ước lượng")
            st.line_chart(est_times)
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu dashboard: {e}")
