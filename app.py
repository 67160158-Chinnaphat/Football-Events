import streamlit as st
import pandas as pd
import joblib
import os

# ===== 1. การตั้งค่าหน้าเว็บและธีม AC Milan =====
st.set_page_config(
    page_title="ระบบวิเคราะห์โอกาสทำประตู (xG)",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ธีม AC Milan (ดำ-แดง-ขาว)
st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A; }
    .stApp p, .stApp span, .stApp label, .stRadio label, div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important; font-weight: 500;
    }
    h1, h2, h3 { color: #E32221 !important; font-weight: bold; text-shadow: 2px 2px 4px #000000; }
    .stButton>button {
        background-color: #E32221 !important; color: #FFFFFF !important;
        border: 2px solid #000000 !important; border-radius: 6px; width: 100%; font-weight: bold; font-size: 18px;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; color: #E32221 !important; border: 2px solid #E32221 !important; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #1A1A1A !important; border: 1px solid #E32221 !important;
    }
    div[data-baseweb="select"] span, input { color: #FFFFFF !important; }
    .result-box {
        padding: 20px; border-radius: 8px; background-color: #121212; 
        border-left: 6px solid #E32221; border-right: 6px solid #E32221; margin-top: 20px;
        box-shadow: 0px 4px 10px rgba(227, 34, 33, 0.2); 
    }
    .stAlert { background-color: #2b0000 !important; color: #ffcccc !important; }
    </style>
    """, unsafe_allow_html=True)


# ===== 2. โหลดโมเดลและข้อมูล (ทำครั้งเดียว) =====
@st.cache_resource
def load_system_files():
    pipeline, data_shot = None, None
    try:
        # 🌟 แก้ไข: เพิ่มโฟลเดอร์ model_artifacts/ นำหน้า
        pipeline = joblib.load('model_artifacts/xg_pipeline.pkl')
    except Exception as e:
        st.error(f"❌ โหลดไฟล์โมเดลไม่สำเร็จ: {e}")
        st.stop()

    if os.path.exists('data_shot.csv'):
        data_shot = pd.read_csv('data_shot.csv')
    else:
        data_shot = pd.DataFrame()

    return pipeline, data_shot

with st.spinner("กำลังโหลดข้อมูลและโมเดล AI..."):
    pipeline, data_shot = load_system_files()

# ===== 3. Sidebar: ข้อมูลเกี่ยวกับโมเดล =====
with st.sidebar:
    st.header("ℹ️ เกี่ยวกับระบบนี้")
    st.write("**โมเดล:** Machine Learning (xG Pipeline)")
    if not data_shot.empty:
        st.write(f"**ฐานข้อมูลลูกยิง:** {len(data_shot):,} รายการ")
    else:
        st.warning("**ไม่พบไฟล์สถิติ:** data_shot.csv ระบบจะไม่สามารถแสดง Top 5 นักเตะได้")

    st.divider()

    st.subheader("⚠️ ข้อควรระวัง")
    st.warning(
        "ผลลัพธ์นี้เป็นการประเมินความน่าจะเป็นเบื้องต้น (Expected Goals) จากสถิติในอดีตเท่านั้น "
        "โอกาสเข้าจริงขึ้นอยู่กับปัจจัยหน้างานอื่นๆ เช่น ความสามารถของผู้รักษาประตู หรือทักษะเฉพาะตัวของนักเตะ"
    )

# ===== 4. เตรียม Dict สำหรับตัวเลือก =====
options_side = {'เหย้า': 1, 'เยือน': 2}
options_bodypart = {'เท้าขวา': 1, 'เท้าซ้าย': 2, 'โหม่ง': 3}
options_location = {
    'แดนบุก': 1, 'แดนรับ': 2, 'กลางกรอบเขตโทษ': 3, 'ปีกซ้าย': 4,
    'ปีกขวา': 5, 'มุมแคบและไกล': 6, 'มุมแคบฝั่งซ้าย': 7, 'มุมแคบฝั่งขวา': 8,
    'ฝั่งซ้ายของกรอบเขตโทษ': 9, 'ซ้ายกรอบ 6 หลา': 10, 'ฝั่งขวาของกรอบเขตโทษ': 11,
    'ขวากรอบ 6 หลา': 12, 'ยิงจ่อๆ / หน้าปากประตู': 13, 'จุดโทษ': 14,
    'นอกกรอบเขตโทษ': 15, 'ยิงไกล': 16, 'ยิงไกลกว่า 35 หลา': 17, 'ยิงไกลกว่า 40 หลา': 18,
    'ไม่ได้บันทึก': 19 # 🌟 เพิ่มตัวเลือกที่ 19 ให้ครบถ้วน
}
options_situation = {'โอเพ่นเพลย์': 1, 'เซ็ตพีซ': 2, 'เตะมุม': 3, 'ฟรีคิก': 4}
options_assist = {'ไม่มี / เลี้ยงมาเอง': 0, 'จ่ายปกติ': 1, 'โยน / ครอส': 2, 'โหม่งชง': 3, 'จ่ายทะลุช่อง': 4}
options_fast_break = {'ไม่ใช่': 0, 'ใช่ (สวนกลับ)': 1}

# ===== 5. ส่วนหลัก: Header & UI =====
st.title("⚽ ระบบประเมินโอกาสทำประตู (xG)")
st.markdown("""
กรอกสถานการณ์และรูปแบบการยิงประตู ระบบจะประเมิน **โอกาสที่จะเป็นประตู (Expected Goals)** พร้อมค้นหาศูนย์หน้าที่มีสไตล์การยิงตรงกับจังหวะนี้มากที่สุด
""")
st.divider()

st.subheader("📋 กำหนดสถานการณ์ลูกยิง")

col1, col2 = st.columns(2)
with col1:
    user_time = st.number_input("นาทีที่ยิง (1-120)", min_value=1, max_value=120, value=90,
                                help="นาทีที่เกิดการง้างเท้ายิง")
    user_side = st.selectbox("ทีมที่กำลังบุก", list(options_side.keys()))
    user_situation = st.selectbox("รูปแบบการเล่น", list(options_situation.keys()))
    user_fast_break = st.radio("เป็นการสวนกลับเร็วหรือไม่?", list(options_fast_break.keys()), horizontal=True)

with col2:
    user_bodypart = st.selectbox("ส่วนที่ใช้ทำประตู", list(options_bodypart.keys()))
    user_location = st.selectbox("ตำแหน่งที่ง้างเท้ายิง", list(options_location.keys()))
    user_assist = st.selectbox("รูปแบบการแอสซิสต์", list(options_assist.keys()))

st.divider()

# ===== 6. ปุ่มทำนายและแสดงผล =====
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    predict_button = st.button("🚀 ประเมินโอกาสเข้าประตู", use_container_width=True)

if predict_button:
    # 🌟 แก้ไข: เปลี่ยนชื่อคีย์ให้ตรงกับที่โมเดลเทรนมาเป๊ะๆ (ลบ _encode ออก)
    user_inputs = {
        'time': user_time,
        'side': options_side[user_side],
        'bodypart': options_bodypart[user_bodypart],
        'location': options_location[user_location],
        'situation': options_situation[user_situation],
        'assist_method': options_assist[user_assist],
        'fast_break': options_fast_break[user_fast_break]
    }

    try:
        with st.spinner("กำลังวิเคราะห์วิถีลูกยิง..."):
            # 🌟 แก้ไข: จัดการสร้าง DataFrame แบบคลีนๆ แค่บรรทัดเดียวจบ!
            input_df = pd.DataFrame([user_inputs])

            # ทำนายผล
            xg_prob = pipeline.predict_proba(input_df)[0, 1]

        # แสดงผลลัพธ์
        st.subheader("📊 ผลการวิเคราะห์ (Analysis Result)")
        st.markdown(f"""
            <div class="result-box">
                <h2 style='text-align: center; color: #FFFFFF !important;'>🎯 โอกาสที่จะเป็นประตู (xG)</h2>
                <h1 style='font-size: 65px; color: #E32221 !important; text-align: center;'>{xg_prob * 100:.2f}%</h1>
                <p style='text-align: center; color: #AAAAAA;'>ค่า Expected Goals = <b>{xg_prob:.4f}</b></p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.write("**ระดับความอันตรายของลูกยิง:**")
        st.progress(float(xg_prob), text=f"Probability: {xg_prob * 100:.2f}%")

        # แสดงข้อมูลที่กรอกสรุปกลับ (Expander)
        with st.expander("📋 ดูสรุปข้อมูลจังหวะการยิงที่บันทึก"):
            summary = {
                "นาทีที่ยิง": f"นาทีที่ {user_time}",
                "ทีม": user_side,
                "ส่วนที่ใช้ยิง": user_bodypart,
                "ตำแหน่ง": user_location,
                "รูปแบบการเล่น": user_situation,
                "การส่งบอล": user_assist,
                "การสวนกลับ": user_fast_break
            }
            st.dataframe(
                pd.DataFrame.from_dict(summary, orient="index", columns=["รายละเอียด"]),
                use_container_width=True
            )

        # ค้นหา Top 5 นักเตะ
        st.write("---")
        st.markdown("### 🌟 Top 5 นักเตะที่ง้างเท้ายิงสไตล์นี้บ่อยที่สุด")

        if not data_shot.empty:
            # 🌟 แก้ไข: ดึงรหัสตัวเลขมาใช้เปรียบเทียบกับใน DataFrame
            body_code = options_bodypart[user_bodypart]
            loc_code = options_location[user_location]
            sit_code = options_situation[user_situation]
            ast_code = options_assist[user_assist]
            fb_code = options_fast_break[user_fast_break]

            # เช็คว่าคอลัมน์ใน CSV ชื่อว่าอะไร (รองรับทั้งแบบมี _encode และไม่มี)
            c_body = 'bodypart_encode' if 'bodypart_encode' in data_shot.columns else 'bodypart'
            c_loc = 'location_encode' if 'location_encode' in data_shot.columns else 'location'
            c_sit = 'situation_encode' if 'situation_encode' in data_shot.columns else 'situation'
            c_ast = 'assist_method_encode' if 'assist_method_encode' in data_shot.columns else 'assist_method'
            c_fb = 'fast_break_encode' if 'fast_break_encode' in data_shot.columns else 'fast_break'

            similar_shots = data_shot[
                (data_shot[c_body] == body_code) &
                (data_shot[c_loc] == loc_code) &
                (data_shot[c_sit] == sit_code) &
                (data_shot[c_ast] == ast_code) &
                (data_shot[c_fb] == fb_code)
            ]

            if len(similar_shots) > 0:
                top_players = similar_shots['player'].value_counts().head(5)
                for i, (player, count) in enumerate(top_players.items(), 1):
                    st.markdown(f"<span style='font-size: 18px;'><b>{i}. {player.title()}</b> : {count} ครั้ง</span>",
                                unsafe_allow_html=True)
            else:
                st.info("ไม่พบสถิตินักเตะที่ยิงด้วยเงื่อนไขเป๊ะๆ แบบนี้ในฐานข้อมูลครับ")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการคำนวณ: {e}")