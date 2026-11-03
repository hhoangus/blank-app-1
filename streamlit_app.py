from datetime import date, timedelta

from html import escape

import pandas as pd
import streamlit as st

try:
    for _k, _v in {"theme.base": "light", "theme.backgroundColor": "#f7f9f6",
                   "theme.secondaryBackgroundColor": "#ffffff", "theme.textColor": "#1f2d26",
                   "theme.primaryColor": "#28745a"}.items():
        st._config.set_option(_k, _v)
except Exception:
    pass

st.set_page_config(page_title="Smart Fridge", page_icon="🥬", layout="wide")

ALLERGY_OPTIONS = ["Tôm", "Cua", "Hải sản", "Đậu phộng", "Sữa", "Trứng", "Đậu nành", "Lúa mì", "Cá", "Khác"]
CATEGORIES = ["Rau củ", "Trái cây", "Thịt", "Cá & hải sản", "Sữa & chế phẩm", "Trứng", "Đồ khô", "Khác"]
CATEGORY_EMOJI = {
    "Rau củ": "🥬", "Trái cây": "🍎", "Thịt": "🥩", "Cá & hải sản": "🐟",
    "Sữa & chế phẩm": "🥛", "Trứng": "🥚", "Đồ khô": "🌾", "Khác": "🍽️",
}
# Emoji riêng theo tên món (nếu tên có chứa từ khóa), không khớp thì dùng emoji của danh mục
NAME_EMOJI = {
    "cà rốt": "🥕", "cà chua": "🍅", "khoai tây": "🥔", "bắp": "🌽", "ngô": "🌽", "hành": "🧅", "tỏi": "🧄",
    "ớt": "🌶️", "dưa leo": "🥒", "dưa chuột": "🥒", "bông cải": "🥦", "cà tím": "🍆", "nấm": "🍄",
    "chuối": "🍌", "táo": "🍎", "cam": "🍊", "chanh": "🍋", "nho": "🍇", "dâu": "🍓", "xoài": "🥭", "dưa hấu": "🍉",
    "gà": "🍗", "heo": "🥓", "bò": "🥩", "tôm": "🦐", "cua": "🦀", "mực": "🦑", "cá": "🐟",
    "sữa": "🥛", "phô mai": "🧀", "bơ": "🧈", "trứng": "🥚", "gạo": "🍚", "mì": "🍜", "bánh mì": "🍞",
}


def food_emoji(item):
    name = item["name"].lower()
    for key, icon in NAME_EMOJI.items():
        if key in name:
            return icon
    return CATEGORY_EMOJI.get(item["category"], "🍽️")


st.markdown("""
<style>
:root { --line:#cfd8d1; --ink:#1f2d26; --muted:#55675c; --green:#28745a; --green-dark:#174c3c; }

/* ===== Nền và chữ chung (luôn kiểu sáng, kể cả khi trình duyệt/Streamlit đang ở chế độ tối) ===== */
.stApp { background:#f7f9f6; color:var(--ink); color-scheme:light; }
[data-testid="stHeader"] { background:transparent; }
.main .block-container { padding-top:1.8rem; max-width:1200px; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp li,
[data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p { color:var(--ink); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:var(--muted) !important; }
ư
/* ===== Tab ===== */
button[data-baseweb="tab"] p { color:#3d5247 !important; font-weight:600; font-size:1.02rem; }
button[data-baseweb="tab"][aria-selected="true"] p { color:var(--green-dark) !important; }
div[data-baseweb="tab-highlight"] { background-color:var(--green) !important; }

/* ===== Ô nhập, dropdown, chọn ngày, chọn nhiều: trắng + viền mảnh ===== */
[data-baseweb="input"], [data-baseweb="input"] *,
[data-baseweb="textarea"], [data-baseweb="textarea"] *,
[data-baseweb="select"], [data-baseweb="select"] * {
    background-color:#ffffff !important; color:var(--ink) !important;
    -webkit-text-fill-color:var(--ink) !important; border-color:transparent !important; box-shadow:none !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    border:1px solid var(--line) !important; border-radius:10px !important; }
[data-baseweb="input"] input::placeholder, [data-baseweb="textarea"] textarea::placeholder {
    color:#8a978f !important; -webkit-text-fill-color:#8a978f !important; }
[data-baseweb="select"] svg, [data-baseweb="input"] svg { fill:var(--muted) !important; color:var(--muted) !important; }
[data-baseweb="select"] span[data-baseweb="tag"], [data-baseweb="select"] span[data-baseweb="tag"] * {
    background-color:#dcfce7 !important; color:#166534 !important; -webkit-text-fill-color:#166534 !important; }

/* Danh sách xổ xuống và lịch */
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li, div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="calendar"], div[data-baseweb="calendar"] div, div[data-baseweb="calendar"] button {
    background-color:#ffffff !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
div[data-baseweb="popover"] li:hover { background-color:#eef4ef !important; }
div[data-baseweb="calendar"] [aria-selected="true"], div[data-baseweb="calendar"] [aria-selected="true"] div {
    background-color:var(--green) !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; }
div[data-baseweb="popover"] > div { border:1px solid var(--line); border-radius:10px; }

/* ===== Form, expander, thẻ số liệu: trắng + viền mảnh ===== */
[data-testid="stForm"], [data-testid="stExpander"] details {
    background:#ffffff !important; border:1px solid var(--line) !important; border-radius:14px !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {
    background:#ffffff !important; color:var(--ink) !important; font-weight:600; }
[data-testid="stExpander"] summary svg { fill:var(--muted) !important; }
div[data-testid="stMetric"] { background:#ffffff; border:1px solid var(--line); padding:.8rem 1rem; border-radius:14px; }
[data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] { color:var(--ink) !important; }

/* ===== Nút bấm ===== */
[data-testid^="stBaseButton"] { background:#ffffff !important; border:1px solid var(--line) !important; border-radius:10px !important; }
[data-testid^="stBaseButton"], [data-testid^="stBaseButton"] * { color:var(--ink) !important; }
[data-testid^="stBaseButton"]:hover { border-color:var(--green) !important; }
[data-testid^="stBaseButton"]:hover, [data-testid^="stBaseButton"]:hover * { color:var(--green-dark) !important; }


/* ===== Form nhập liệu dạng bảng (cột trái: tên trường, cột phải: ô nhập) ===== */
[data-testid="stHorizontalBlock"]:has(.rowmark) {
    gap:0 !important; align-items:stretch !important; background:#ffffff;
    border:1px solid var(--line); margin-top:-1px; }
[data-testid="stHorizontalBlock"]:has(.rowmark) > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(.rowmark) > [data-testid="column"] { padding:.4rem .7rem; min-width:0; }
[data-testid="stHorizontalBlock"]:has(.rowmark) > [data-testid="stColumn"]:first-child,
[data-testid="stHorizontalBlock"]:has(.rowmark) > [data-testid="column"]:first-child {
    background:#eef4ef; border-right:1px solid var(--line); display:flex; align-items:center; }
.cell-label { font-weight:600; color:var(--ink); }
[data-testid="stHorizontalBlock"]:has(.rowmark) [data-baseweb="input"],
[data-testid="stHorizontalBlock"]:has(.rowmark) [data-baseweb="select"] > div { border-color:#e1e8e2 !important; }
.table-gap { height:.8rem; }

/* ===== Bảng ===== */
.tbl-wrap { background:#ffffff; border:1px solid var(--line); border-radius:12px; overflow-x:auto; margin-bottom:1rem; }
.tbl { width:100%; border-collapse:collapse; font-size:.93rem; color:var(--ink); }
.tbl th { background:#eef4ef; text-align:left; padding:.6rem .8rem; font-weight:700; border-bottom:1px solid var(--line); white-space:nowrap; }
.tbl td { padding:.55rem .8rem; border-bottom:1px solid #e6ece7; white-space:nowrap; }
.tbl tr:last-child td { border-bottom:none; }

/* ===== Khung tiêu đề, thẻ dị ứng, chú thích màu ===== */
.hero { display:flex; align-items:center; justify-content:space-between; gap:1rem; overflow:hidden;
        padding:1.5rem 1.8rem; border-radius:18px;
        background:linear-gradient(120deg,#174c3c,#28745a); margin-bottom:1.2rem; }
.stApp .hero h1 { color:#ffffff !important; margin:0; font-size:2.15rem; }
.stApp .hero p { color:#e0f1e7 !important; margin:.45rem 0 0; }
.hero-emoji { font-size:2.6rem; letter-spacing:.35rem; white-space:nowrap; }
.allergy-tag { display:inline-block; background:#fee2e2; color:#b42318 !important; border:1px solid #fecaca;
               border-radius:999px; padding:.35rem .75rem; margin:.15rem .25rem .15rem 0; font-weight:600; }
.legend { display:flex; gap:.5rem; flex-wrap:wrap; margin:.5rem 0 1rem; }
.legend span { border-radius:999px; padding:.35rem .7rem; font-size:.82rem; font-weight:600; }
.stApp .legend-red { background:#fee2e2; color:#991b1b; }
.stApp .legend-yellow { background:#fef3c7; color:#92400e; }
.stApp .legend-green { background:#dcfce7; color:#166534; }
@media (max-width:700px) { .hero-emoji { display:none; } }
</style>
""", unsafe_allow_html=True)


def html_table(df, row_colors=None):
    """Vẽ bảng bằng HTML để luôn trắng, viền mảnh và đồng bộ với các khung khác."""
    def fmt(v):
        return f"{v:g}" if isinstance(v, float) else str(v)
    head = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body = ""
    for n, (_, r) in enumerate(df.iterrows()):
        style = f' style="background:{row_colors[n]}"' if row_colors else ""
        body += f"<tr{style}>" + "".join(f"<td>{escape(fmt(v))}</td>" for v in r) + "</tr>"
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def cell(label):
    """Một dòng của bảng nhập liệu: trả về cột bên phải để đặt ô nhập."""
    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<span class="rowmark"></span><div class="cell-label">{label}</div>', unsafe_allow_html=True)
    return right


# ---------- Dữ liệu demo (chỉ lưu trong phiên Streamlit hiện tại) ----------
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "type": "Cá nhân",
        "name": "", "weight": 60.0, "allergies": [],       # hồ sơ cá nhân
        "family_name": "", "members": [],                   # hồ sơ gia đình
    }
if "inventory" not in st.session_state:
    today = date.today()
    st.session_state.inventory = [
        {"name": "Sữa tươi", "quantity": 2.0, "unit": "hộp", "expiry_date": today + timedelta(days=1), "category": "Sữa & chế phẩm"},
        {"name": "Thịt gà", "quantity": 1.0, "unit": "kg", "expiry_date": today + timedelta(days=3), "category": "Thịt"},
        {"name": "Cà rốt", "quantity": 5.0, "unit": "củ", "expiry_date": today + timedelta(days=7), "category": "Rau củ"},
    ]


def expiry_status(expiry_date):
    days = (expiry_date - date.today()).days
    if days <= 1:
        status = "🔴 Khẩn cấp"
    elif days <= 3:
        status = "🟡 Cần ăn sớm"
    else:
        status = "🟢 An toàn"
    return days, status


def all_allergies():
    """Dị ứng của cá nhân, hoặc gộp dị ứng của cả gia đình."""
    p = st.session_state.user_profile
    if p["type"] == "Cá nhân":
        return set(p["allergies"])
    result = set()
    for m in p["members"]:
        result.update(m["allergies"])
    return result


def allergy_warnings():
    """Thực phẩm trong tủ có thể liên quan tới dị ứng đã khai báo."""
    allergies = all_allergies() - {"Khác"}
    found = []
    for item in st.session_state.inventory:
        name = item["name"].lower()
        for a in sorted(allergies):
            hit = a.lower() in name
            if a in ("Hải sản", "Cá") and item["category"] == "Cá & hải sản":
                hit = True
            if hit:
                found.append((item["name"], a))
    return found


# ---------- Đầu trang ----------
st.markdown("""
<div class="hero">
  <div>
    <h1>🥬 Smart Fridge</h1>
    <p>Quản lý thực phẩm thông minh · Hạn chế lãng phí · Ăn uống an toàn</p>
  </div>
  <div class="hero-emoji">🥕🍅🥬🍋🥛</div>
</div>
""", unsafe_allow_html=True)

items = st.session_state.inventory
urgent = sum(expiry_status(x["expiry_date"])[0] <= 1 for x in items)
soon = sum(2 <= expiry_status(x["expiry_date"])[0] <= 3 for x in items)
c1, c2, c3 = st.columns(3)
c1.metric("🥗 Số loại thực phẩm", len(items))
c2.metric("🔴 Cần xử lý khẩn cấp", urgent)
c3.metric("🟡 Cần dùng sớm", soon)

profile_tab, fridge_tab = st.tabs(["👤 Hồ sơ người dùng", "🥗 Tủ lạnh thông minh"])

# ======================= HỒ SƠ =======================
with profile_tab:
    st.subheader("Hồ sơ người dùng")
    st.caption("Chọn dùng cho cá nhân hoặc cả gia đình, rồi nhập các dị ứng cần lưu ý.")
    profile = st.session_state.user_profile

    # Để ngoài form để chọn xong là giao diện đổi ngay
    profile_type = st.radio("Loại hồ sơ", ["Cá nhân", "Gia đình"], horizontal=True,
                            index=0 if profile["type"] == "Cá nhân" else 1)
    if profile_type != profile["type"]:
        profile["type"] = profile_type
        st.rerun()

    if profile_type == "Cá nhân":
        with st.form("profile_form"):
            with cell("Họ và tên"):
                name = st.text_input("Họ và tên", value=profile["name"], placeholder="Ví dụ: Hoàng Nguyễn",
                                     label_visibility="collapsed")
            with cell("Cân nặng (kg)"):
                weight = st.number_input("Cân nặng (kilogram))", min_value=1.0, max_value=400.0,
                                         value=float(profile["weight"]), step=0.5, label_visibility="collapsed")
            with cell("Dị ứng thực phẩm"):
                allergies = st.multiselect("Dị ứng thực phẩm", ALLERGY_OPTIONS, default=profile["allergies"],
                                           label_visibility="collapsed")
            st.markdown('<div class="table-gap"></div>', unsafe_allow_html=True)
            save_profile = st.form_submit_button("Lưu hồ sơ", use_container_width=True)
        if save_profile:
            profile.update({"name": name.strip(), "weight": weight, "allergies": allergies})
            st.success("Đã cập nhật hồ sơ trong phiên hiện tại.")
            st.rerun()

        st.markdown("#### Thông tin hồ sơ hiện tại")
        a, b = st.columns(2)
        a.metric("Người dùng", profile["name"] or "Chưa nhập tên")
        b.metric("Cân nặng", f'{profile["weight"]:g} kg')

    else:
        family_name = st.text_input("Tên gia đình", value=profile["family_name"],
                                    placeholder="Ví dụ: Gia đình anh Hoàng")
        profile["family_name"] = family_name.strip()

        with st.expander("➕ Thêm thành viên", expanded=not profile["members"]):
            with st.form("member_form", clear_on_submit=True):
                with cell("Tên thành viên *"):
                    m_name = st.text_input("Tên thành viên", label_visibility="collapsed")
                with cell("Vai trò"):
                    m_role = st.selectbox("Vai trò", ["Bố", "Mẹ", "Con", "Ông", "Bà", "Khác"], label_visibility="collapsed")
                with cell("Cân nặng (kg)"):
                    m_weight = st.number_input("Cân nặng (kg)", min_value=1.0, max_value=400.0, value=50.0, step=0.5,
                                               label_visibility="collapsed")
                with cell("Dị ứng"):
                    m_allergies = st.multiselect("Dị ứng", ALLERGY_OPTIONS, label_visibility="collapsed")
                st.markdown('<div class="table-gap"></div>', unsafe_allow_html=True)
                add_member = st.form_submit_button("➕ Thêm thành viên", use_container_width=True)
        if add_member:
            if not m_name.strip():
                st.error("Bạn cần nhập tên thành viên.")
            else:
                profile["members"].append({"name": m_name.strip(), "role": m_role,
                                           "weight": m_weight, "allergies": m_allergies})
                st.success(f"Đã thêm {m_name.strip()}.")
                st.rerun()

        st.markdown("#### Thông tin hồ sơ hiện tại")
        a, b = st.columns(2)
        a.metric("Gia đình", profile["family_name"] or "Chưa nhập tên")
        b.metric("Số thành viên", len(profile["members"]))

        if profile["members"]:
            member_df = pd.DataFrame([{
                "Tên": m["name"], "Vai trò": m["role"], "Cân nặng (kg)": m["weight"],
                "Dị ứng": ", ".join(m["allergies"]) or "Không",
            } for m in profile["members"]])
            st.markdown(html_table(member_df), unsafe_allow_html=True)
            labels = [f'{m["name"]} ({m["role"]})' for m in profile["members"]]
            chosen_member = st.selectbox("Chọn thành viên muốn xóa", labels)
            if st.button("🗑️ Xóa thành viên đã chọn"):
                del profile["members"][labels.index(chosen_member)]
                st.rerun()
        else:
            st.info("Chưa có thành viên nào trong gia đình.")

    st.markdown("**Cảnh báo dị ứng**" + (" (cả gia đình)" if profile_type == "Gia đình" else ""))
    current_allergies = sorted(all_allergies())
    if current_allergies:
        st.markdown("".join(f'<span class="allergy-tag">⚠️ {x}</span>' for x in current_allergies),
                    unsafe_allow_html=True)
        st.warning("Hãy kiểm tra thành phần và nhãn cảnh báo trước khi sử dụng thực phẩm.")
    else:
        st.info("Chưa chọn dị ứng nào.")

# ======================= TỦ LẠNH =======================
with fridge_tab:
    st.subheader("Tủ lạnh thông minh")
    st.caption("Thêm thực phẩm và theo dõi hạn sử dụng.")

    with st.expander("➕ Thêm thực phẩm", expanded=True):
        with st.form("add_food_form", clear_on_submit=True):
            with cell("Tên thực phẩm *"):
                food_name = st.text_input("Tên thực phẩm", placeholder="Ví dụ: Trứng gà", label_visibility="collapsed")
            with cell("Số lượng *"):
                quantity = st.number_input("Số lượng", min_value=0.1, value=1.0, step=1.0, label_visibility="collapsed")
            with cell("Đơn vị"):
                unit = st.selectbox("Đơn vị", ["cái", "quả", "hộp", "gói", "kg", "gram", "lít", "chai", "bó", "củ"],
                                    label_visibility="collapsed")
            with cell("Danh mục"):
                category = st.selectbox("Danh mục", CATEGORIES, label_visibility="collapsed")
            with cell("Hạn sử dụng"):
                expiry_date = st.date_input("Hạn sử dụng", value=date.today() + timedelta(days=7),
                                            label_visibility="collapsed")
            st.markdown('<div class="table-gap"></div>', unsafe_allow_html=True)
            add_food = st.form_submit_button("➕ Thêm vào tủ lạnh", use_container_width=True)
    if add_food:
        if not food_name.strip():
            st.error("Bạn cần nhập tên thực phẩm.")
        else:
            st.session_state.inventory.append({
                "name": food_name.strip(), "quantity": quantity, "unit": unit,
                "expiry_date": expiry_date, "category": category,
            })
            st.success(f"Đã thêm {food_name.strip()} vào tủ lạnh.")
            st.rerun()

    warnings = allergy_warnings()
    if warnings:
        text = ", ".join(f"{n} (dị ứng {a})" for n, a in warnings)
        st.error(f"⚠️ Trong tủ có thực phẩm liên quan đến dị ứng đã khai báo: {text}")

    st.markdown("""
    <div class="legend">
      <span class="legend-red">🔴 Còn ≤ 1 ngày: Khẩn cấp</span>
      <span class="legend-yellow">🟡 Còn 2–3 ngày: Cần ăn sớm</span>
      <span class="legend-green">🟢 Còn &gt; 3 ngày: An toàn</span>
    </div>
    """, unsafe_allow_html=True)

    fcol, scol = st.columns([1, 2])
    with fcol:
        status_filter = st.selectbox("Lọc trạng thái", ["Tất cả", "🔴 Khẩn cấp", "🟡 Cần ăn sớm", "🟢 An toàn"])
    with scol:
        search_text = st.text_input("Tìm thực phẩm", placeholder="Nhập tên cần tìm...")

    rows = []
    for i, item in enumerate(st.session_state.inventory):
        days, status = expiry_status(item["expiry_date"])
        if days < 0:
            remaining = f"Quá hạn {abs(days)} ngày"
        elif days == 0:
            remaining = "Hết hạn hôm nay"
        else:
            remaining = f"{days} ngày"
        rows.append({
            "ID": i, "Thực phẩm": f'{food_emoji(item)} {item["name"]}', "Danh mục": item["category"],
            "Số lượng": item["quantity"], "Đơn vị": item["unit"],
            "Hạn sử dụng": item["expiry_date"].strftime("%d/%m/%Y"),
            "Còn lại": remaining, "Trạng thái": status,
        })

    df = pd.DataFrame(rows)
    filtered = df.copy()
    if status_filter != "Tất cả":
        filtered = filtered[filtered["Trạng thái"] == status_filter]
    if search_text.strip():
        filtered = filtered[filtered["Thực phẩm"].str.contains(search_text.strip(), case=False, na=False)]

    if filtered.empty:
        st.info("Không tìm thấy thực phẩm phù hợp.")
    else:
        shown = filtered.drop(columns=["ID"])
        bg = {"🔴 Khẩn cấp": "#FEE2E2", "🟡 Cần ăn sớm": "#FEF3C7", "🟢 An toàn": "#DCFCE7"}
        st.markdown(html_table(shown, [bg.get(x, "#FFFFFF") for x in shown["Trạng thái"]]), unsafe_allow_html=True)

    st.markdown("#### Xóa thực phẩm")
    if st.session_state.inventory:
        choices = {
            f'{x["name"]} — {x["quantity"]:g} {x["unit"]} (hạn {x["expiry_date"].strftime("%d/%m/%Y")})': i
            for i, x in enumerate(st.session_state.inventory)
        }
        chosen = st.selectbox("Chọn thực phẩm muốn xóa", list(choices.keys()))
        if st.button("🗑️ Xóa thực phẩm đã chọn"):
            del st.session_state.inventory[choices[chosen]]
            st.success("Đã xóa thực phẩm.")
            st.rerun()
    else:
        st.info("Tủ lạnh hiện chưa có thực phẩm.")

st.divider()
st.caption("Smart Fridge · Bản giao diện thử nghiệm. Dữ liệu chỉ được giữ trong phiên đang mở, chưa lưu lâu dài.")