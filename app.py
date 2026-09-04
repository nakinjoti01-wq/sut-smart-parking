import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import altair as alt
from datetime import datetime, timezone, timedelta

# 1. จัดการ Timezone ประเทศไทย (UTC+7)
TH_TZ = timezone(timedelta(hours=7))

def get_now_th():
    return datetime.now(TH_TZ)

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Smart Campus AI Parking Dashboard",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception:
        return "https://upload.wikimedia.org/wikipedia/th/4/40/Seal_of_Suranaree_University_of_Technology.svg"

SUT_LOGO_SRC = get_image_base64("SUT_Logo.png")
TOTAL_SLOTS = 10

# 3. Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "last_occupied" not in st.session_state:
    st.session_state["last_occupied"] = 5

if "today_rates" not in st.session_state:
    st.session_state["today_rates"] = [50.0]

if "slot_turnover_counts" not in st.session_state:
    st.session_state["slot_turnover_counts"] = {f"SLOT {i:02d}": (4 if i <= 4 else 7) for i in range(1, TOTAL_SLOTS + 1)}

if "heatmap_matrix" not in st.session_state:
    st.session_state["heatmap_matrix"] = {
        "Mon / จันทร์":    [9, 10, 10, 8, 9, 7, 6, 5, 4],
        "Tue / อังคาร":   [8, 9, 10, 9, 8, 6, 5, 4, 3],
        "Wed / พุธ":      [7, 9, 10, 10, 8, 7, 6, 4, 4],
        "Thu / พฤหัส":    [8, 10, 10, 9, 8, 6, 5, 5, 3],
        "Fri (Today) / ศุกร์": [6, 7, 8, 7, 5, 5, 4, 3, 2],
        "Sat / เสาร์":    [2, 3, 4, 5, 5, 4, 3, 2, 1],
        "Sun / อาทิตย์":  [1, 1, 2, 3, 3, 2, 2, 1, 1]
    }

if "activity_logs" not in st.session_state:
    now_str = get_now_th().strftime('%H:%M:%S')
    st.session_state["activity_logs"] = [
        f"[{now_str}] System initialized / เริ่มต้นระบบตรวจจับ B1",
        f"[{now_str}] Spatial ROI 10 slots ready / พื้นที่ 10 ช่องพร้อมใช้งาน"
    ]

# สารบัญ 2 ภาษา
LANG_DICT = {
    "ไทย": {
        "title": "Smart Motorcycle Parking Dashboard",
        "subtitle": "ระบบตรวจจับและนับที่ว่างรถจักรยานยนต์อัตโนมัติ • อาคารเรียนรวม 1 (B1)",
        "total_slots": "ความจุทั้งหมด",
        "zone_tag": "พื้นที่นำร่อง 10 ช่อง อาคาร B1",
        "available": "ช่องว่างพร้อมจอด",
        "avail_tag": "พร้อมเข้าใช้งานทันที",
        "occupied": "จำนวนรถที่จอด",
        "occ_tag": "ปัจจุบันหนาแน่น",
        "status": "สถานะความหนาแน่น",
        "daily_avg": "เฉลี่ยสะสมวันนี้",
        "tab_live": "🔴 ผังตรวจจับสด (Real-time Live)",
        "tab_stat": "📊 เปอร์เซ็นต์เฉลี่ยรายวัน & HeatMap",
        "map_title": "🅿️ ผังระบุสถานะช่องจอด (PARKING SLOTS MAP)",
        "map_sub": "ไฟสถานะตรวจจับแบบเรียลไทม์ 10 ช่องจอด อาคาร B1",
        "busy_txt": "มีรถจอด",
        "free_txt": "ว่าง",
        "alert_center": "🔔 ALERT CENTER",
        "auto_badge": "อัตโนมัติ",
        "recent_act": "RECENT ACTIVITY (1 ช่อง/คัน)",
        "crit_title": "CRITICAL OCCUPANCY",
        "crit_sub": "ที่จอดรถใกล้เต็ม เหลือเพียง {} ช่อง",
        "stab_title": "CAPACITY STABLE",
        "stab_sub": "มีช่องจอดเพียงพอ พร้อมให้บริการ",
        "stats_title": "📊 STATS & HEALTH",
        "rounds": "รอบ",
        "daily_chart_title": "📈 อัตราการใช้งานเฉลี่ยสะสมรายวัน (%)",
        "daily_chart_sub": "ผลรวมเปอร์เซ็นต์ความหนาแน่น ÷ รอบการตรวจจับในแต่ละวัน (ครบ 7 วัน)",
        "slot_chart_title": "🔄 ความถี่การเข้า-ออกของรถในแต่ละช่อง (รอบ)",
        "slot_chart_sub": "วิเคราะห์จำนวนครั้งที่มีการเข้าและออกจากช่องจริง (SLOT 01 - 10)",
        "heat_title": "⏱️ ช่วงเวลาหนาแน่นสูงสุดในรอบสัปดาห์ (Peak Hours HeatMatrix 7 Days)",
        "heat_sub": "จำนวนรถเข้าจอดเฉลี่ยรายชั่วโมง (08:00 - 17:00 น.) • ช่องเวลาปัจจุบันแสดงเป็นสีน้ำเงินเรืองแสง",
        "live_label": "ช่องเวลาปัจจุบัน",
        "logout": "🚪 ออกจากระบบ (Logout)",
        "days": ["1.จันทร์", "2.อังคาร", "3.พุธ", "4.พฤหัส", "5.วันนี้ (ศุกร์)", "6.เสาร์", "7.อาทิตย์"]
    },
    "English": {
        "title": "Smart Motorcycle Parking Dashboard",
        "subtitle": "Automated Motorcycle Vacancy Detection System • Learning Center 1 (B1)",
        "total_slots": "TOTAL CAPACITY",
        "zone_tag": "10 Pilot Slots Zone B1",
        "available": "AVAILABLE SLOTS",
        "avail_tag": "Ready to Park",
        "occupied": "OCCUPIED SLOTS",
        "occ_tag": "Current Density",
        "status": "OCCUPANCY STATUS",
        "daily_avg": "Daily Avg Rate",
        "tab_live": "🔴 Real-time Live Monitoring",
        "tab_stat": "📊 Daily Analytics & HeatMap",
        "map_title": "🅿️ PARKING SLOTS MAP (ROI STATUS)",
        "map_sub": "Real-time Spatial Occupancy Map (10 Slots B1)",
        "busy_txt": "OCCUPIED",
        "free_txt": "VACANT",
        "alert_center": "🔔 ALERT CENTER",
        "auto_badge": "Automated",
        "recent_act": "RECENT ACTIVITY (1 slot/bike)",
        "crit_title": "CRITICAL OCCUPANCY",
        "crit_sub": "Parking almost full! Only {} slot(s) left",
        "stab_title": "CAPACITY STABLE",
        "stab_sub": "Slots available. Ready for parking",
        "stats_title": "📊 STATS & HEALTH",
        "rounds": "cycles",
        "daily_chart_title": "📈 Daily Average Space Utilization (%)",
        "daily_chart_sub": "Sum of occupancy rates ÷ Total detection cycles per day (7 Days)",
        "slot_chart_title": "🔄 Slot Turnover Frequency (Cycles)",
        "slot_chart_sub": "Turnover count based on vehicle arrival and departure (SLOT 01 - 10)",
        "heat_title": "⏱️ Weekly Peak Hours Matrix (7 Days)",
        "heat_sub": "Average occupied slots per hour (08:00 - 17:00) • Active hour in highlighted Cyber Blue",
        "live_label": "Active Hour",
        "logout": "🚪 Log Out",
        "days": ["1.Mon", "2.Tue", "3.Wed", "4.Thu", "5.Today (Fri)", "6.Sat", "7.Sun"]
    }
}

# 4. CSS Stylings
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }

.stApp {
    background: radial-gradient(at 10% 10%, rgba(186, 230, 253, 0.45) 0px, transparent 50%),
                radial-gradient(at 90% 15%, rgba(254, 215, 170, 0.45) 0px, transparent 50%),
                radial-gradient(at 80% 85%, rgba(253, 186, 116, 0.35) 0px, transparent 50%),
                radial-gradient(at 20% 80%, rgba(224, 242, 254, 0.5) 0px, transparent 50%),
                linear-gradient(135deg, #F0F7FF 0%, #FFF8F1 100%);
    background-attachment: fixed;
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1450px; }

.top-navbar {
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(14px);
    padding: 16px 28px; border-radius: 20px; border: 1.5px solid rgba(255, 255, 255, 1);
    box-shadow: 0 8px 30px rgba(234, 88, 12, 0.06); display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}

.kpi-card-styled {
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(14px); border-radius: 20px; padding: 20px 22px;
    border: 1.5px solid rgba(255, 255, 255, 1); box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    position: relative; overflow: hidden; height: 135px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 12px;
}
.kpi-label-text { font-size: 15px; font-weight: 700; color: #1E293B; letter-spacing: 0.3px; }
.kpi-num-text { font-size: 34px; font-weight: 800; line-height: 1.1; margin: 4px 0; }
.kpi-unit-text { font-size: 17px; font-weight: 600; color: #475569; }
.kpi-sub-text { font-size: 13.5px; font-weight: 600; }
.kpi-icon-badge {
    position: absolute; top: 16px; right: 18px; width: 44px; height: 44px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
}

.panel-box {
    background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(14px); border: 1.5px solid rgba(255, 255, 255, 1);
    border-radius: 22px; padding: 22px 24px; box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04); margin-bottom: 18px;
}

/* ปรับแต่งกรอบ st.container(border=True) ให้เป็นสีขาวเนียน ขอบมน 22px */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(14px) !important;
    border: 1.5px solid rgba(255, 255, 255, 1) !important;
    border-radius: 22px !important;
    padding: 22px 24px 16px 24px !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04) !important;
    margin-bottom: 18px !important;
}

.login-card {
    background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(16px); border-radius: 24px;
    border: 1.5px solid rgba(255, 255, 255, 1); padding: 44px 36px; box-shadow: 0 16px 40px rgba(234, 88, 12, 0.08); margin-top: 40px;
}
@media (max-width: 768px) {
    .top-navbar { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>
""", unsafe_allow_html=True)

if not st.session_state["authenticated"]:
    _, col_mid, _ = st.columns([1, 1.1, 1])
    with col_mid:
        st.markdown(f"""
        <div class="login-card">
            <div style="text-align: center; margin-bottom: 22px;">
                <img src="{SUT_LOGO_SRC}" width="85" style="margin-bottom: 12px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.06));">
                <div style="font-size: 13px; font-weight: 700; color: #EA580C; letter-spacing: 1.5px;">SURANAREE UNIVERSITY OF TECHNOLOGY</div>
                <h3 style="margin: 4px 0 0 0; font-weight: 800; color: #0F172A; font-size: 24px;">Smart Parking System</h3>
                <p style="font-size: 15px; color: #334155; font-weight: 500; margin: 4px 0 0 0;">Sign in to access B1 parking dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("auth_form"):
            u_in = st.text_input("Student ID / รหัสนักศึกษา", value="B6700218")
            p_in = st.text_input("Password / รหัสผ่าน (13 digits)", value="1309701264661", type="password")
            login_btn = st.form_submit_button("Sign in to Dashboard →", use_container_width=True)
            if login_btn:
                if u_in == "B6700218" and p_in == "1309701264661":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid Student ID or Password")
else:
    now_th = get_now_th()
    current_hour = now_th.hour
    time_index = min(max(current_hour - 8, 0), 8)

    with st.sidebar:
        st.markdown("### 🌐 Language / ภาษา")
        selected_lang = st.radio("เลือกภาษา (Language):", ["ไทย", "English"], horizontal=True)
        L = LANG_DICT[selected_lang]

        st.divider()
        st.markdown("### 📱 Display Mode")
        view_mode = st.radio("รูปแบบมุมมอง:", ["🖥️ Desktop View", "📱 Mobile View"], index=0)

        st.divider()
        st.markdown("### ⚙️ Simulation Panel")
        occupied_count = st.slider("Occupied Slots", 0, TOTAL_SLOTS, st.session_state["last_occupied"])
        available_count = TOTAL_SLOTS - occupied_count
        current_occupancy_rate = (occupied_count / TOTAL_SLOTS) * 100

        st.session_state["heatmap_matrix"]["Fri (Today) / ศุกร์"][time_index] = occupied_count

        if occupied_count != st.session_state["last_occupied"]:
            curr_time = now_th.strftime("%H:%M:%S")
            if occupied_count > st.session_state["last_occupied"]:
                for slot in range(st.session_state["last_occupied"] + 1, occupied_count + 1):
                    slot_name = f"SLOT {slot:02d}"
                    rate_step = (slot / TOTAL_SLOTS) * 100
                    st.session_state["today_rates"].append(rate_step)
                    st.session_state["slot_turnover_counts"][slot_name] += 1
                    act_txt = f"{slot_name} เข้าจอด ({rate_step:.0f}%)" if selected_lang == "ไทย" else f"{slot_name} Arrived ({rate_step:.0f}%)"
                    st.session_state["activity_logs"].insert(0, f"[{curr_time}] {act_txt}")
            else:
                for slot in range(st.session_state["last_occupied"], occupied_count, -1):
                    slot_name = f"SLOT {slot:02d}"
                    rate_step = ((slot - 1) / TOTAL_SLOTS) * 100
                    st.session_state["today_rates"].append(rate_step)
                    st.session_state["slot_turnover_counts"][slot_name] += 1
                    act_txt = f"{slot_name} ออกจากช่อง ({rate_step:.0f}%)" if selected_lang == "ไทย" else f"{slot_name} Departed ({rate_step:.0f}%)"
                    st.session_state["activity_logs"].insert(0, f"[{curr_time}] {act_txt}")

            st.session_state["activity_logs"] = st.session_state["activity_logs"][:4]
            st.session_state["last_occupied"] = occupied_count

        today_avg_rate = sum(st.session_state["today_rates"]) / len(st.session_state["today_rates"])

        st.divider()
        st.markdown("### 📡 Hardware & AI Status")
        st.markdown(f"""
        * **Camera:** `Hikvision 1080p (B1)`
        * **Model:** `YOLO11-Nano Edge`
        * **Daily Avg:** `{today_avg_rate:.1f}%`
        """)
        if st.button(L["logout"], use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    # Navbar
    st.markdown(f"""
    <div class="top-navbar">
        <div style="display: flex; align-items: center; gap: 18px;">
            <img src="{SUT_LOGO_SRC}" width="50" style="filter: drop-shadow(0 2px 5px rgba(0,0,0,0.08));">
            <div>
                <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #0F172A;">{L["title"]}</h2>
                <p style="margin: 0; font-size: 14px; color: #334155; font-weight: 500;">{L["subtitle"]}</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <span style="background: rgba(220, 252, 231, 0.9); border: 1.5px solid #4ADE80; padding: 7px 16px; border-radius: 20px; font-size: 13px; font-weight: 800; color: #15803D;">● LIVE INFERENCE</span>
            <span style="font-size: 14px; font-weight: 700; color: #1E293B; background: rgba(255, 255, 255, 0.9); padding: 7px 16px; border-radius: 20px; border: 1.5px solid #CBD5E1;">👤 ID: <b>B6700218</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Cards KPI
    k1, k2, k3, k4 = st.columns(4)
    unit_slot = "ช่อง" if selected_lang == "ไทย" else "slots"
    unit_bike = "คัน" if selected_lang == "ไทย" else "bikes"

    with k1:
        st.markdown(f"""
        <div class="kpi-card-styled" style="border-bottom: 4px solid #2563EB;">
            <div class="kpi-icon-badge" style="background: #EFF6FF; color: #2563EB;">🅿️</div>
            <div class="kpi-label-text">{L["total_slots"]}</div>
            <div class="kpi-num-text" style="color: #0F172A;">{TOTAL_SLOTS} <span class="kpi-unit-text">{unit_slot}</span></div>
            <div class="kpi-sub-text" style="color: #2563EB;">{L["zone_tag"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card-styled" style="border-bottom: 4px solid #059669;">
            <div class="kpi-icon-badge" style="background: #ECFDF5; color: #059669;">✨</div>
            <div class="kpi-label-text">{L["available"]}</div>
            <div class="kpi-num-text" style="color: #059669;">{available_count} <span class="kpi-unit-text">{unit_slot}</span></div>
            <div class="kpi-sub-text" style="color: #059669;">{L["avail_tag"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card-styled" style="border-bottom: 4px solid #DC2626;">
            <div class="kpi-icon-badge" style="background: #FEF2F2; color: #DC2626;">🛵</div>
            <div class="kpi-label-text">{L["occupied"]}</div>
            <div class="kpi-num-text" style="color: #DC2626;">{occupied_count} <span class="kpi-unit-text">{unit_bike}</span></div>
            <div class="kpi-sub-text" style="color: #DC2626;">{L["occ_tag"]} {current_occupancy_rate:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st_color = "#DC2626" if available_count <= 2 else "#EA580C" if available_count <= 4 else "#059669"
        st_bg = "#FEF2F2" if available_count <= 2 else "#FFF7ED" if available_count <= 4 else "#ECFDF5"
        
        if selected_lang == "ไทย":
            if available_count == 0:
                st_text = "FULL (ที่จอดเต็ม)"
            elif available_count <= 2:
                st_text = "CRITICAL (ใกล้เต็ม)"
            elif available_count <= 4:
                st_text = "WARNING (เริ่มแน่น)"
            else:
                st_text = "NORMAL (ว่างปกติ)"
        else:
            if available_count == 0:
                st_text = "FULL (NO VACANCY)"
            elif available_count <= 2:
                st_text = "CRITICAL (NEAR FULL)"
            elif available_count <= 4:
                st_text = "WARNING (BUSY)"
            else:
                st_text = "NORMAL (CLEAR)"

        st.markdown(f"""
        <div class="kpi-card-styled" style="border-bottom: 4px solid {st_color};">
            <div class="kpi-icon-badge" style="background: {st_bg}; color: {st_color};">⚡</div>
            <div class="kpi-label-text">{L["status"]}</div>
            <div class="kpi-num-text" style="color: {st_color}; font-size: 23px; margin-top: 6px;">{st_text}</div>
            <div class="kpi-sub-text" style="color: #334155;">{L["daily_avg"]}: <b style="color:{st_color}; font-size:15px;">{today_avg_rate:.1f}%</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    tab_live, tab_heatmap = st.tabs([L["tab_live"], L["tab_stat"]])

    # Tab 1: Live Monitoring
    with tab_live:
        grid_cols_css = "grid-template-columns: repeat(2, 1fr);" if "Mobile" in view_mode else "grid-template-columns: repeat(5, 1fr);"
        iframe_height = 860 if "Mobile" in view_mode else 410
        side_height = 440
        slot_box_height = 135

        slots_boxes = ""
        for i in range(1, TOTAL_SLOTS + 1):
            is_busy = i <= occupied_count
            bg_color = "linear-gradient(145deg, #EF4444 0%, #DC2626 100%)" if is_busy else "linear-gradient(145deg, #10B981 0%, #059669 100%)"
            box_shadow = "0 8px 20px rgba(220, 38, 38, 0.28)" if is_busy else "0 8px 20px rgba(5, 150, 105, 0.28)"
            icon = "🛵" if is_busy else "🅿️"
            status_text = L["busy_txt"] if is_busy else L["free_txt"]

            slots_boxes += f"""
            <div style="background: {bg_color}; box-shadow: {box_shadow}; border-radius: 16px; padding: 12px 10px; text-align: center; color: white; display: flex; flex-direction: column; justify-content: space-between; height: {slot_box_height}px; border: 1px solid rgba(255,255,255,0.25);">
                <div style="font-size: 15px; font-weight: 800; letter-spacing: 0.8px; opacity: 0.95;">SLOT {i:02d}</div>
                <div style="font-size: 38px; line-height: 1.1; filter: drop-shadow(0 3px 5px rgba(0,0,0,0.2));">{icon}</div>
                <div style="font-size: 15px; font-weight: 800; background: rgba(0,0,0,0.25); border-radius: 10px; padding: 4px 0;">{status_text}</div>
            </div>
            """

        slot_panel_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; font-family: 'Kanit', sans-serif; margin: 0; padding: 0; }}
            body {{ background: transparent; }}
            .panel {{ 
                background: rgba(255, 255, 255, 0.95); 
                backdrop-filter: blur(14px); 
                border: 1.5px solid rgba(255, 255, 255, 1); 
                border-radius: 22px; 
                padding: 20px 24px 22px 24px; 
                box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04); 
            }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1.5px solid #E2E8F0; flex-wrap: wrap; gap: 8px; }}
            .grid-container {{ display: grid; {grid_cols_css} gap: 14px; }}
        </style>
        </head>
        <body>
            <div class="panel">
                <div class="header">
                    <div>
                        <h4 style="color:#0F172A; font-size:18px; font-weight:800;">{L["map_title"]}</h4>
                        <p style="color:#334155; font-size:14px; font-weight:500; margin-top:2px;">{L["map_sub"]}</p>
                    </div>
                    <div style="font-size:15px; font-weight:800; display:flex; gap:16px;">
                        <span style="color:#059669;">● {L['free_txt']} ({available_count})</span>
                        <span style="color:#DC2626;">● {L['busy_txt']} ({occupied_count})</span>
                    </div>
                </div>
                <div class="grid-container">{slots_boxes}</div>
            </div>
        </body>
        </html>
        """

        if available_count == 0:
            alert_title = "PARKING FULL" if selected_lang == "English" else "ที่จอดรถเต็ม"
            alert_msg = "No available slots left / ไม่มีช่องว่างพร้อมให้บริการ"
            alert_color = "#DC2626"
            alert_bg = "#FEF2F2"
        elif available_count <= 2:
            alert_title = L["crit_title"]
            alert_msg = L["crit_sub"].format(available_count)
            alert_color = "#DC2626"
            alert_bg = "#FEF2F2"
        else:
            alert_title = L["stab_title"]
            alert_msg = L["stab_sub"]
            alert_color = "#16A34A"
            alert_bg = "#F0FDF4"

        logs_html = "".join([f"<li style='margin-bottom:8px; font-size:13px; color:#1E293B; font-weight:500;'>{log}</li>" for log in st.session_state["activity_logs"][:3]])

        side_component = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; font-family: 'Kanit', sans-serif; margin: 0; padding: 0; }}
            body {{ background: transparent; }}
            .panel {{ 
                background: rgba(255, 255, 255, 0.95); 
                backdrop-filter: blur(14px); 
                border: 1.5px solid rgba(255, 255, 255, 1); 
                border-radius: 22px; 
                padding: 20px 22px; 
                box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04); 
            }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1.5px solid #E2E8F0; }}
        </style>
        </head>
        <body>
            <div class="panel">
                <div class="header">
                    <h4 style="color:#0F172A; font-size:16px; font-weight:800;">{L["alert_center"]}</h4>
                    <span style="font-size:12px; color:#2563EB; font-weight:700;">{L["auto_badge"]}</span>
                </div>
                <div style="background:{alert_bg}; border-left:5px solid {alert_color}; padding:12px 14px; border-radius:12px; margin-bottom:12px;">
                    <div style="font-size:13.5px; font-weight:800; color:{alert_color};">{alert_title}</div>
                    <div style="font-size:13px; color:#0F172A; font-weight:600; margin-top:2px;">{alert_msg}</div>
                </div>
                <div style="background: rgba(248, 250, 252, 0.9); border: 1.5px solid #CBD5E1; padding:12px 14px; border-radius:14px; margin-bottom:14px;">
                    <div style="font-size:13px; font-weight:800; color:#1E293B; margin-bottom:6px;">{L["recent_act"]}</div>
                    <ul style="margin:0; padding-left:16px; line-height:1.5;">{logs_html}</ul>
                </div>
                <div class="header" style="margin-bottom:8px; padding-bottom:6px;">
                    <h4 style="color:#0F172A; font-size:15px; font-weight:800;">{L["stats_title"]}</h4>
                </div>
                <div style="font-size:13.5px; color:#334155; font-weight:600; display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; justify-content:space-between;"><span>Inference Engine:</span><b style="color:#2563EB; font-weight:800;">YOLO11-Nano</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>{L["daily_avg"]}:</span><b style="color:#2563EB; font-weight:800;">{today_avg_rate:.1f}%</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>History Logs:</span><b style="color:#0F172A;">{len(st.session_state['today_rates'])} {L['rounds']}</b></div>
                </div>
            </div>
        </body>
        </html>
        """

        if "Mobile" in view_mode:
            components.html(slot_panel_html, height=iframe_height)
            components.html(side_component, height=side_height)
            st.markdown("""
            <div class="panel-box" style="margin-top: -8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <h4 style="margin:0; font-size:17px; font-weight:800; color:#0F172A;">📹 Live CCTV Feed & AI Bounding Box</h4>
                        <p style="margin:0; font-size:13.5px; color:#334155; font-weight:500;">Zone B1 Learning Center 1</p>
                    </div>
                    <span style="background:#FEF2F2; color:#DC2626; border:1px solid #FEE2E2; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:800;">● LIVE 1080P</span>
                </div>
            """, unsafe_allow_html=True)
            try:
                st.image("parking_10slots.jpg", caption="Spatial Detection 10 Slots - SUT Zone B1", use_container_width=True)
            except Exception:
                st.info("💡 Place 'parking_10slots.jpg' in workspace directory")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            col_main, col_side = st.columns([7.2, 2.8])
            with col_main:
                components.html(slot_panel_html, height=iframe_height)
                st.markdown("""
                <div class="panel-box" style="margin-top: -6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <h4 style="margin:0; font-size:17px; font-weight:800; color:#0F172A;">📹 Live CCTV Feed & AI Bounding Box</h4>
                            <p style="margin:0; font-size:13.5px; color:#334155; font-weight:500;">Zone B1 Learning Center 1</p>
                        </div>
                        <span style="background:#FEF2F2; color:#DC2626; border:1px solid #FEE2E2; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:800;">● LIVE 1080P</span>
                    </div>
                """, unsafe_allow_html=True)
                try:
                    st.image("parking_10slots.jpg", caption="Spatial Detection 10 Slots - SUT Zone B1", use_container_width=True)
                except Exception:
                    st.info("💡 Place 'parking_10slots.jpg' in workspace directory")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_side:
                components.html(side_component, height=side_height)

    # Tab 2: Analytics & HeatMap
    with tab_heatmap:
        st.write("")
        g_col1, g_col2 = st.columns(2) if "Desktop" in view_mode else (st.container(), st.container())

        # กล่องที่ 1: อัตราการใช้งานเฉลี่ยสะสมรายวัน
        with g_col1:
            with st.container(border=True):
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <h4 style="margin:0; font-size:16px; font-weight:800; color:#0F172A;">{L["daily_chart_title"]}</h4>
                    <p style="margin:3px 0 0 0; font-size:13px; color:#334155; font-weight:500;">{L["daily_chart_sub"]}</p>
                </div>
                """, unsafe_allow_html=True)

                df_days = pd.DataFrame({
                    "Day": L["days"],
                    "Rate": [72.0, 81.5, 76.0, 84.0, round(today_avg_rate, 1), 38.5, 26.0],
                    "Color": ["#EAB308", "#EC4899", "#10B981", "#F97316", "#0284C7", "#8B5CF6", "#EF4444"]
                })

                # ขยายความหนาแท่งกราฟเป็น size=32
                chart_days = alt.Chart(df_days).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=32).encode(
                    x=alt.X('Day:N', sort=None, axis=alt.Axis(title=None, labelAngle=-25, labelFontSize=11.5, labelColor='#1E293B', labelFontWeight='bold')),
                    y=alt.Y('Rate:Q', axis=alt.Axis(title='ความหนาแน่น (%)' if selected_lang == 'ไทย' else 'Occupancy (%)', labelFontSize=11.5, titleFontSize=11.5), scale=alt.Scale(domain=[0, 115])),
                    color=alt.Color('Color:N', scale=None),
                    tooltip=[alt.Tooltip('Day:N', title='วัน / Day'), alt.Tooltip('Rate:Q', title='อัตราเฉลี่ย (%)', format='.1f')]
                ).properties(height=185).configure_view(strokeWidth=0)

                st.altair_chart(chart_days, use_container_width=True)

        # กล่องที่ 2: ความถี่การเข้า-ออกของรถในแต่ละช่อง
        with g_col2:
            with st.container(border=True):
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <h4 style="margin:0; font-size:16px; font-weight:800; color:#0F172A;">{L["slot_chart_title"]}</h4>
                    <p style="margin:3px 0 0 0; font-size:13px; color:#334155; font-weight:500;">{L["slot_chart_sub"]}</p>
                </div>
                """, unsafe_allow_html=True)

                df_slots = pd.DataFrame(
                    list(st.session_state["slot_turnover_counts"].items()),
                    columns=["Slot", "Cycles"]
                )
                max_cycles = max(df_slots["Cycles"]) if len(df_slots) > 0 else 10

                # ขยายความหนาแท่งกราฟเป็น size=22
                chart_slots = alt.Chart(df_slots).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=22, color='#2563EB').encode(
                    x=alt.X('Slot:N', axis=alt.Axis(title=None, labelAngle=-30, labelFontSize=11, labelColor='#1E293B', labelFontWeight='bold')),
                    y=alt.Y('Cycles:Q', axis=alt.Axis(title='รอบ / Cycles', labelFontSize=11.5, titleFontSize=11.5, tickMinStep=1), scale=alt.Scale(domain=[0, max_cycles + 2.5])),
                    tooltip=[alt.Tooltip('Slot:N', title='ช่องจอด'), alt.Tooltip('Cycles:Q', title='จำนวนรอบ (ครั้ง)')]
                ).properties(height=185).configure_view(strokeWidth=0)

                st.altair_chart(chart_slots, use_container_width=True)

        # HeatMatrix 7 Days
        time_cols = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        active_time_label = time_cols[time_index]

        st.markdown(f"""
        <div class="panel-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:8px;">
                <h4 style="margin:0; font-size:16px; font-weight:800; color:#0F172A;">{L["heat_title"]}</h4>
                <span style="background: rgba(239, 246, 255, 0.95); color:#2563EB; font-size:12px; font-weight:800; padding:4px 12px; border-radius:14px; border:1.5px solid #BFDBFE;">
                    ⚡ {L["live_label"]}: {active_time_label}
                </span>
            </div>
            <p style="margin:0 0 12px 0; font-size:13px; color:#334155; font-weight:500;">{L["heat_sub"]}</p>
        """, unsafe_allow_html=True)

        table_rows = ""
        for day_name, row in st.session_state["heatmap_matrix"].items():
            is_today = "Today" in day_name or "วันนี้" in day_name
            day_label_style = "color:#EA580C; font-weight:800; background: rgba(255, 247, 237, 0.95);" if is_today else "color:#1E293B; font-weight:700; background: rgba(248, 250, 252, 0.95);"
            row_tds = f"<td style='padding:8px 12px; font-size:13.5px; {day_label_style}'>{day_name}</td>"
            for idx, val in enumerate(row):
                if is_today and idx == time_index:
                    bg = "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)"
                    txt_color = "#FFFFFF"
                    cell_style = "border: 2px solid #60A5FA; transform: scale(1.06); box-shadow: 0 4px 12px rgba(37,99,235,0.45); z-index: 2;"
                    badge_html = f"<div style='font-size:17px; font-weight:800; line-height:1.1;'>{val}</div><div style='font-size:9px; background:rgba(255,255,255,0.25); border-radius:4px; padding:1px 0; margin-top:2px; letter-spacing:0.5px; font-weight:800;'>● LIVE NOW</div>"
                else:
                    alpha = max(0.08, (val - 1) / 9)
                    bg = f"rgba(234, 88, 12, {alpha:.2f})"
                    txt_color = "#FFFFFF" if alpha > 0.52 else "#0F172A"
                    cell_style = "border: none;"
                    badge_html = f"<div style='font-size:13.5px; font-weight:800;'>{val}</div>"
                row_tds += f"<td style='padding:7px; text-align:center; background:{bg}; color:{txt_color}; border-radius:8px; {cell_style}'>{badge_html}</td>"
            table_rows += f"<tr>{row_tds}</tr>"

        th_headers = "".join([f"<th style='padding:8px; text-align:center; font-size:13px; color:#1E293B; font-weight:700;'>{t}</th>" for t in time_cols])
        st.markdown(f"""
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:separate; border-spacing:5px;">
                    <thead><tr><th style="padding:8px 12px; text-align:left; font-size:13px; color:#1E293B; font-weight:800;">Day / Time</th>{th_headers}</tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
