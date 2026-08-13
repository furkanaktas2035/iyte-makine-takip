import streamlit as st
import pandas as pd
from datetime import datetime, date
import database as db
import plotly.graph_objects as go
import time
import html

# =============================================================================
# 1. SAYFA KONFİGÜRASYONU & CSS
# =============================================================================

st.set_page_config(
    page_title="İYTE Makine | Akademik Yönetim Platformu",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        margin-bottom: 10px;
    }
    .profile-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(49, 46, 129, 0.3);
    }
    .custom-header {
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
    }
    .alert-card {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.08);
    }
    .pomo-card {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    .live-badge {
        display: inline-block;
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
    }
    @media (max-width: 768px) {
        .stApp { padding: 5px; }
        div[data-testid="stMetric"] { padding: 12px; }
        .custom-header { font-size: 22px !important; }
        .stButton > button { width: 100%; border-radius: 10px; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# 2. VERİTABANI İNİT
# =============================================================================

db.init_db()
conn = db.get_connection()

# =============================================================================
# 3. KULLANICI GİRİŞ SİSTEMİ
# =============================================================================

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

if not st.session_state["user_id"]:
    st.markdown("<h1 class='custom-header' style='text-align:center;'>🎓 İYTE Akademik Yönetim Platformu</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#a5b4fc; font-size:15px;'>Verilerinizin kaybolmaması için adınızı/rumuzunuzu veya öğrenci numaranızı girin.</p>", unsafe_allow_html=True)
    
    col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
    with col_g2:
        input_user = st.text_input("Kullanıcı Adı / Öğrenci No / Rumuz", placeholder="Örn: furkan_3302")
        if st.button("🚀 Panetime Giriş Yap", use_container_width=True):
            if input_user.strip():
                st.session_state["user_id"] = input_user.strip().lower()
                st.toast(f"Giriş başarılı! Hoş geldin {input_user}", icon="🎉")
                time.sleep(0.3)
                st.rerun()
            else:
                st.warning("Lütfen geçerli bir kullanıcı adı girin.")
    st.stop()

user_id = st.session_state["user_id"]

prof_row = db.get_or_create_profile(user_id)
profile = {
    "name": prof_row[0],
    "department": prof_row[1],
    "grade": prof_row[2],
    "current_gpa": prof_row[3] if prof_row[3] is not None else 3.00,
    "current_credits": prof_row[4] if prof_row[4] is not None else 60
}

# =============================================================================
# 4. HARF NOTLARI VE DERS HAVUZU
# =============================================================================

HARF_KATSAYI = {"AA": 4.0, "BA": 3.5, "BB": 3.0, "CB": 2.5, "CC": 2.0, "DC": 1.5, "DD": 1.0, "FF": 0.0}
HARF_ALT_SINIR = {"AA": 90, "BA": 85, "BB": 80, "CB": 75, "CC": 70, "DC": 65, "DD": 60}

IYTE_ALL_COURSES = [
    {"code": "CHEM121", "name": "GENEL KİMYA I", "credit": 3, "ects": 5, "sem": 1},
    {"code": "CHEM141", "name": "GENEL KİMYA LABORATUVARI I", "credit": 1, "ects": 2, "sem": 1},
    {"code": "ENG101", "name": "İNGİLİZCE OKUMA VE YAZMA BECERİLERİ I", "credit": 3, "ects": 3, "sem": 1},
    {"code": "MATH101", "name": "ÖN MATEMATİK", "credit": 0, "ects": 2, "sem": 1},
    {"code": "MATH141", "name": "TEMEL ANALİZ I", "credit": 4, "ects": 5, "sem": 1},
    {"code": "ME101", "name": "MAKİNA MÜHENDİSLİĞİNE GİRİŞ", "credit": 2, "ects": 5, "sem": 1},
    {"code": "ME113", "name": "BİLGİSAYAR DESTEKLİ TEKNİK RESİM I", "credit": 3, "ects": 3, "sem": 1},
    {"code": "PHYS101", "name": "GENEL FİZİK I", "credit": 4, "ects": 5, "sem": 1},
    {"code": "PHYS111", "name": "GENEL FİZİK LAB. I", "credit": 1, "ects": 2, "sem": 1},
    {"code": "OHS 101", "name": "İş Sağlığı ve Güvenliği I", "credit": 1, "ects": 1, "sem": 1},
    
    {"code": "CS106", "name": "TEMEL BİLGİSAYAR BİLİMİ VE PROGRAMLAMASI", "credit": 3, "ects": 5, "sem": 2},
    {"code": "ENG102", "name": "İNGİLİZCE OKUMA VE YAZMA BECERİLERİ II", "credit": 3, "ects": 3, "sem": 2},
    {"code": "GCC101", "name": "KARİYER PLANLAMA VE GELİŞTİRME", "credit": 0, "ects": 2, "sem": 2},
    {"code": "MATH142", "name": "TEMEL ANALİZ II", "credit": 4, "ects": 6, "sem": 2},
    {"code": "ME114", "name": "BİLGİSAYAR DESTEKLİ TEKNİK RESİM II", "credit": 3, "ects": 4, "sem": 2},
    {"code": "ME150", "name": "MALZEME BİLİMİ VE MÜHENDİSLİĞİ I", "credit": 3, "ects": 4, "sem": 2},
    {"code": "PHYS102", "name": "GENEL FİZİK II", "credit": 4, "ects": 5, "sem": 2},
    {"code": "PHYS112", "name": "GENEL FİZİK LAB. II", "credit": 1, "ects": 2, "sem": 2},
    {"code": "OHS 102", "name": "İş Sağlığı ve Güvenliği II", "credit": 1, "ects": 1, "sem": 2},

    {"code": "HIST201", "name": "ATATÜRK İLKELERİ VE İNKILAP TARİHİ I", "credit": 0, "ects": 2, "sem": 3},
    {"code": "TURK201", "name": "TÜRK DİLİ DERSLERİ I", "credit": 0, "ects": 2, "sem": 3},
    {"code": "ECON205", "name": "EKONOMİNİN PRENSİPLERİ", "credit": 3, "ects": 4, "sem": 3},
    {"code": "MATH255", "name": "DİFERANSİYEL DENKLEMLER", "credit": 4, "ects": 6, "sem": 3},
    {"code": "ME207", "name": "TERMODİNAMİK I", "credit": 3, "ects": 6, "sem": 3},
    {"code": "ME221", "name": "STATİK", "credit": 3, "ects": 5, "sem": 3},
    {"code": "ME251", "name": "MALZEME BİLİMİ VE MÜHENDİSLİĞİ II", "credit": 3, "ects": 5, "sem": 3},

    {"code": "HIST202", "name": "ATATÜRK İLKELERİ VE İNKILAP TARİHİ II", "credit": 0, "ects": 2, "sem": 4},
    {"code": "TURK202", "name": "TÜRK DİLİ DERSLERİ II", "credit": 0, "ects": 2, "sem": 4},
    {"code": "EE210", "name": "ELEKTRİK VE ELEKTRONİK DEVRELERİNİN TEMELLERİ", "credit": 3, "ects": 4, "sem": 4},
    {"code": "ME208", "name": "TERMODİNAMİK II", "credit": 3, "ects": 6, "sem": 4},
    {"code": "ME222", "name": "DİNAMİK", "credit": 3, "ects": 5, "sem": 4},
    {"code": "ME224", "name": "CİSİMLERİN MUKAVEMETİ", "credit": 3, "ects": 5, "sem": 4},
    {"code": "ME242", "name": "MÜHENDİSLER İÇİN UYGULAMALI MATEMATİK", "credit": 4, "ects": 6, "sem": 4},

    {"code": "ENG301", "name": "TEKNİK YAZIM VE İLETİŞİM", "credit": 3, "ects": 3, "sem": 5},
    {"code": "ME300", "name": "TALAŞLI İMALAT / METAL ŞEKİLLENDİRME STAJI", "credit": 0, "ects": 7, "sem": 5},
    {"code": "ME301", "name": "AKIŞKANLAR MEKANİĞİ I", "credit": 3, "ects": 5, "sem": 5},
    {"code": "ME311", "name": "MAKİNA ELEMANLARI I", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME323", "name": "ÜRETİM YÖNTEMLERİ", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME331", "name": "MAKİNA TEORİSİ I", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME343", "name": "MÜHENDİSLİKTE SAYISAL YÖNTEMLER", "credit": 3, "ects": 3, "sem": 5},

    {"code": "ME302", "name": "AKIŞKANLAR MEKANİĞİ II", "credit": 3, "ects": 6, "sem": 6},
    {"code": "ME312", "name": "MAKİNA ELEMANLARI II", "credit": 3, "ects": 6, "sem": 6},
    {"code": "ME328", "name": "ÜRETİM MÜHENDİSLİĞİ", "credit": 3, "ects": 5, "sem": 6},
    {"code": "ME332", "name": "MAKİNA TEORİSİ II", "credit": 3, "ects": 5, "sem": 6},
    {"code": "ME340", "name": "ISI TRANSFERİ", "credit": 4, "ects": 5, "sem": 6},
    {"code": "ME352", "name": "SİSTEM ANALİZİ VE KONTROL", "credit": 4, "ects": 5, "sem": 6},

    {"code": "ME400", "name": "ENDÜSTRİYEL ORGANİZASYON STAJI", "credit": 0, "ects": 9, "sem": 7},
    {"code": "ME401", "name": "MÜHENDİSLİK EKONOMİSİ VE TASARIM", "credit": 4, "ects": 6, "sem": 7},
    {"code": "ME409", "name": "MAKİNA MÜHENDİSLİĞİ LABORATUVARI", "credit": 3, "ects": 4, "sem": 7},
    {"code": "ME402", "name": "MÜHENDİSLİK TASARIM DERSLERİ", "credit": 4, "ects": 12, "sem": 8}
]

# =============================================================================
# 5. YARDIMCI HESAPLAMA FONKSİYONLARI
# =============================================================================

def calculate_iyte_letter(score):
    if score is None: return "Henüz Belli Değil"
    if score >= 90: return "AA (4.0)"
    elif score >= 85: return "BA (3.5)"
    elif score >= 80: return "BB (3.0)"
    elif score >= 75: return "CB (2.5)"
    elif score >= 70: return "CC (2.0)"
    elif score >= 65: return "DC (1.5)"
    elif score >= 60: return "DD (1.0)"
    else: return "FF (0.0)"

def score_to_coefficient(score):
    if score >= 90: return 4.0
    elif score >= 85: return 3.5
    elif score >= 80: return 3.0
    elif score >= 75: return 2.5
    elif score >= 70: return 2.0
    elif score >= 65: return 1.5
    elif score >= 60: return 1.0
    else: return 0.0

def get_live_exam_score(exam_id, database_score):
    key = f"ex_{exam_id}"
    if key in st.session_state:
        try:
            return float(st.session_state[key])
        except (ValueError, TypeError):
            return 0.0
    if database_score is None:
        return 0.0
    try:
        return float(database_score)
    except (ValueError, TypeError):
        return 0.0

def calculate_combined_gpa():
    courses_df = pd.read_sql_query("SELECT id, credit, ects FROM courses WHERE user_id = ?", conn, params=(user_id,))
    if courses_df.empty:
        return 0.0, float(profile["current_gpa"]), 0, 0

    total_term_credits = int(courses_df["credit"].sum())
    total_term_ects = int(courses_df["ects"].sum())
    evaluated_term_credits = 0
    term_weighted_points = 0.0

    for _, c_row in courses_df.iterrows():
        course_id = int(c_row["id"])
        c_credit = float(c_row["credit"])

        exams_df = pd.read_sql_query("SELECT id, weight, score FROM exams WHERE course_id = ? AND user_id = ?", conn, params=(course_id, user_id))
        if exams_df.empty:
            continue

        weighted_sum = 0.0
        total_weight = 0.0

        for _, exam in exams_df.iterrows():
            exam_id = int(exam["id"])
            score = get_live_exam_score(exam_id, exam["score"])
            if score <= 0: continue
            try:
                weight = float(exam["weight"])
            except (ValueError, TypeError): continue
            if weight <= 0: continue

            weighted_sum += score * weight
            total_weight += weight

        if total_weight > 0:
            course_average = weighted_sum / total_weight
            letter_coefficient = score_to_coefficient(course_average)
            if c_credit > 0:
                evaluated_term_credits += c_credit
                term_weighted_points += c_credit * letter_coefficient

    term_gpa = (term_weighted_points / evaluated_term_credits) if evaluated_term_credits > 0 else 0.0
    previous_gpa = float(profile["current_gpa"])
    previous_credits = float(profile["current_credits"])
    previous_points = previous_gpa * previous_credits

    total_accumulated_credits = previous_credits + evaluated_term_credits
    total_accumulated_points = previous_points + term_weighted_points

    new_combined_cgpa = (total_accumulated_points / total_accumulated_credits) if total_accumulated_credits > 0 else previous_gpa
    return term_gpa, new_combined_cgpa, total_term_credits, total_term_ects

def generate_html_report(profile_data, df_courses_summary, df_exams_summary, df_notes_summary):
    html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>İYTE Akademik Durum Raporu</title>
<style>
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; color: #0f172a; background: #ffffff; }}
.header {{ border-bottom: 3px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px; }}
.header h1 {{ margin: 0; color: #1e3a8a; font-size: 22px; text-transform: uppercase; }}
.profile-info {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 25px; font-size: 14px; line-height: 1.6; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 9px 12px; text-align: left; font-size: 13px; }}
th {{ background-color: #2563eb; color: #ffffff; font-weight: bold; }}
tr:nth-child(even) {{ background-color: #f1f5f9; }}
.section-title {{ color: #1e3a8a; font-size: 16px; border-left: 4px solid #2563eb; padding-left: 8px; margin-top: 25px; margin-bottom: 12px; font-weight: bold; }}
.note-box {{ background: #fefce8; border-left: 4px solid #eab308; padding: 10px 14px; margin-bottom: 10px; border-radius: 4px; font-size: 13px; }}
</style>
</head>
<body>
<div class="header">
<h1>İZMİR YÜKSEK TEKNOLOJİ ENSTİTÜSÜ - AKADEMİK DURUM RAPORU</h1>
<p style="margin:5px 0 0 0; color:#64748b; font-size:12px;">Rapor Oluşturma Tarihi: {date.today().strftime('%d.%m.%Y')}</p>
</div>
<div class="profile-info">
<strong>Öğrenci / Kullanıcı:</strong> {html.escape(str(profile_data['name']))}<br>
<strong>Bölüm / Akademik Düzey:</strong> {html.escape(str(profile_data['department']))} - {html.escape(str(profile_data['grade']))}<br>
<strong>Girdiği Birikimli AGNO (CGPA):</strong> {profile_data['current_gpa']:.2f} / 4.00 &nbsp; <strong>Tamamlanan Kredi:</strong> {profile_data['current_credits']}
</div>
<div class="section-title">1. Aktif Dönem Ders Listesi ve Kredi Yükü</div>
"""
    html_content += df_courses_summary.to_html(index=False, escape=False) if not df_courses_summary.empty else "<p>Kayıtlı ders bulunmamaktadır.</p>"
    html_content += '<div class="section-title">2. Değerlendirmeler & Sınav Not Transkripti</div>'
    html_content += df_exams_summary.to_html(index=False, escape=False) if not df_exams_summary.empty else "<p>Sınav kaydı bulunmamaktadır.</p>"
    html_content += '<div class="section-title">3. Önemli Ders Notları Defteri</div>'

    if not df_notes_summary.empty:
        for _, n in df_notes_summary.head(10).iterrows():
            html_content += f"""
<div class="note-box">
<strong>[{html.escape(str(n['Ders']))}] {html.escape(str(n['Konu']))}</strong> <span style="font-size:11px; color:#64748b;">({html.escape(str(n['Tarih']))})</span><br>
<span>{html.escape(str(n['İçerik']))}</span>
</div>"""
    else:
        html_content += "<p>Kayıtlı ders notu yok.</p>"
    html_content += "</body></html>"
    return html_content

# =============================================================================
# 6. SIDEBAR
# =============================================================================

with st.sidebar:
    safe_name = html.escape(str(profile["name"]))
    safe_user_id = html.escape(str(user_id))
    safe_grade = html.escape(str(profile["grade"]))

    st.markdown(f"""
    <div class="profile-card">
        <h3 style="margin:0; color:#f8fafc; font-size:18px;">🎓 {safe_name}</h3>
        <p style="margin:4px 0 0 0; color:#a5b4fc; font-size:12px;">Oturum: <b>{safe_user_id}</b></p>
        <span style="display:inline-block; background:#4f46e5; color:white; padding:3px 9px; border-radius:10px; font-size:10px; font-weight:bold; margin-top:5px;">{safe_grade}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Oturumu Kapat / Kullanıcı Değiştir", use_container_width=True):
        st.session_state["user_id"] = ""
        keys_to_delete = [k for k in st.session_state.keys() if str(k).startswith("ex_")]
        for key in keys_to_delete:
            del st.session_state[key]
        st.rerun()

    with st.expander("👤 Kullanıcı Profil Bilgilerini Değiştir"):
        u_name = st.text_input("Ad Soyad / Kullanıcı Adı", value=profile["name"])
        u_dept = st.text_input("Bölüm", value=profile["department"])
        grade_options = ["1. Sınıf", "2. Sınıf", "3. Sınıf", "4. Sınıf", "Lisans"]
        grade_index = grade_options.index(profile["grade"]) if profile["grade"] in grade_options else 2
        u_grade = st.selectbox("Sınıf", grade_options, index=grade_index)
        u_gpa = st.number_input("Geçmiş AGNO (CGPA)", min_value=0.0, max_value=4.0, value=float(profile["current_gpa"]), step=0.01)
        u_credits = st.number_input("Geçmiş Tamamlanan Kredi", min_value=0, max_value=250, value=int(profile["current_credits"]), step=1)

        if st.button("💾 Bilgilerimi Kalıcı Kaydet", use_container_width=True):
            db.update_profile(user_id, u_name, u_dept, u_grade, u_gpa, u_credits)
            st.toast("Profil bilgileriniz başarıyla kaydedildi!", icon="🎉")
            time.sleep(0.3)
            st.rerun()

    st.divider()
    menu = st.radio("Navigasyon", [
        "📈 Dönem & Sınav Not Takibi",
        "🎯 Gerekli Final Notu Hesaplayıcı",
        "🎯 Dinamik AGNO / GANO Simülatörü",
        "⏱️ Pomodoro Çalışma Sayacı",
        "📊 Aylık Başarı Trendi",
        "📅 Sınav Takvimi & Geri Sayım",
        "📝 Ders Notları",
        "🖨️ PDF / HTML Rapor Al",
        "⚙️ Ders & Müfredat Yönetimi"
    ])

# =============================================================================
# 7. SINAV UYARISI METNİ (HTML DÜZELTİLDİ)
# =============================================================================

df_alert = pd.read_sql_query("""
    SELECT c.code, e.title, e.event_date 
    FROM exams e JOIN courses c ON e.course_id = c.id 
    WHERE e.user_id = ? AND e.event_date >= DATE('now') 
    ORDER BY e.event_date ASC LIMIT 1
""", conn, params=(user_id,))

if not df_alert.empty and menu not in ["⏱️ Pomodoro Çalışma Sayacı", "🖨️ PDF / HTML Rapor Al"]:
    ex_date = datetime.strptime(str(df_alert.iloc[0]["event_date"]), "%Y-%m-%d").date()
    days_left = (ex_date - date.today()).days
    exam_code = html.escape(str(df_alert.iloc[0]["code"]))
    exam_title = html.escape(str(df_alert.iloc[0]["title"]))
    exam_date = html.escape(str(df_alert.iloc[0]["event_date"]))

    # Çift girinti temizlendi, düzgün render edilmesi sağlandı
    alert_html = f'<div class="alert-card"><div style="font-size:15px; line-height:1.5; color:#f8fafc;">🚨 <strong>YAKLAŞAN AKADEMİK ETKİNLİK UYARISI:</strong> <strong>{exam_code} - {exam_title}</strong> sınavına <strong style="color:#fca5a5; font-size:16px;">{days_left} gün</strong> kaldı! Tarih: <em>{exam_date}</em></div></div>'
    st.markdown(alert_html, unsafe_allow_html=True)

# =============================================================================
# 8. MODÜLLER
# =============================================================================

if menu == "📈 Dönem & Sınav Not Takibi":
    st.markdown("<h1 class='custom-header'>Akademik Performans & Not Takibi</h1>", unsafe_allow_html=True)
    term_gpa, combined_cgpa, total_term_credits, total_term_ects = calculate_combined_gpa()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Geçmiş Birikimli AGNO", f"{profile['current_gpa']:.2f}")
    c2.metric("Güncel Dönem Ortalaması", f"{term_gpa:.2f}")
    cgpa_delta = combined_cgpa - float(profile["current_gpa"])
    c3.metric("DÖNEM SONU BEKLENEN AGNO", f"{combined_cgpa:.2f}", delta=f"{cgpa_delta:+.2f}")
    c4.metric("Aktif Dönem Kredisi", f"{total_term_credits} Kredi")
    c5.metric("Aktif Dönem AKTS", f"{total_term_ects} AKTS")

    st.divider()
    courses_df = pd.read_sql_query("SELECT id, code, name, credit, ects FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))

    if not courses_df.empty:
        for _, c_row in courses_df.iterrows():
            course_id = int(c_row["id"])
            with st.expander(f"📘 {c_row['code']} - {c_row['name']} ({c_row['credit']} Kredi / {c_row['ects']} AKTS)", expanded=True):
                exams_df = pd.read_sql_query("SELECT id, title, event_type, weight, score FROM exams WHERE course_id = ? AND user_id = ? ORDER BY id", conn, params=(course_id, user_id))
                col_e1, col_e2 = st.columns([2, 1])

                with col_e1:
                    if not exams_df.empty:
                        for _, ex in exams_df.iterrows():
                            exam_id = int(ex["id"])
                            ca, cb, cc, cd = st.columns([2, 1, 1, 1])
                            with ca: st.write(f"• **{ex['title']}** (%{ex['weight']})")
                            
                            database_score = ex["score"]
                            default_score = float(database_score) if database_score is not None else 0.0
                            
                            with cb:
                                new_s = st.number_input("Not", min_value=0.0, max_value=100.0, value=default_score, step=0.5, key=f"ex_{exam_id}")
                            
                            with cc:
                                if st.button("Kaydet", key=f"btn_s_{exam_id}", use_container_width=True):
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE exams SET score = ? WHERE id = ? AND user_id = ?", (new_s, exam_id, user_id))
                                    conn.commit()
                                    st.toast(f"✅ {ex['title']} notu kaydedildi!", icon="💾")
                                    time.sleep(0.2)
                                    st.rerun()

                            with cd:
                                if st.button("🗑️ Sil", key=f"btn_del_ex_{exam_id}", use_container_width=True):
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
                                    conn.commit()
                                    if f"ex_{exam_id}" in st.session_state: del st.session_state[f"ex_{exam_id}"]
                                    st.toast("🗑️ Sınav silindi!", icon="⚠️")
                                    time.sleep(0.2)
                                    st.rerun()
                    else:
                        st.info("Bu ders için henüz sınav eklenmedi.")

                with col_e2:
                    if not exams_df.empty:
                        weighted_sum, total_weight = 0.0, 0.0
                        for _, ex in exams_df.iterrows():
                            score = get_live_exam_score(int(ex["id"]), ex["score"])
                            if score <= 0: continue
                            try: weight = float(ex["weight"])
                            except (ValueError, TypeError): continue
                            if weight <= 0: continue

                            weighted_sum += score * weight
                            total_weight += weight

                        if total_weight > 0:
                            c_avg = weighted_sum / total_weight
                            st.markdown(f'<div style="color:#cbd5e1; font-weight:600; margin-bottom:5px;">Ağırlıklı Ortalama (%{total_weight:.0f})</div>', unsafe_allow_html=True)
                            st.subheader(f"{c_avg:.2f} / 100")
                            st.caption(f"Tahmini Harf Notu: **{calculate_iyte_letter(c_avg)}**")
                            st.markdown('<span class="live-badge">● CANLI HESAPLANIYOR</span>', unsafe_allow_html=True)
                        else:
                            st.write("Girilmiş sınav notu yok.")

elif menu == "🎯 Gerekli Final Notu Hesaplayıcı":
    st.markdown("<h1 class='custom-header'>Hedef Harf Notu İçin Gerekli Final Notu</h1>", unsafe_allow_html=True)
    st.caption("Girdiğiniz vize/quiz notlarına göre istediğiniz harf notunu alabilmek için Final sınavından kaç almanız gerektiğini hesaplar.")

    courses_df = pd.read_sql_query("SELECT id, code, name FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))
    if not courses_df.empty:
        for _, c_row in courses_df.iterrows():
            course_id = int(c_row["id"])
            with st.expander(f"🎯 {c_row['code']} - {c_row['name']}", expanded=True):
                exams_df = pd.read_sql_query("SELECT id, title, weight, score FROM exams WHERE course_id = ? AND user_id = ?", conn, params=(course_id, user_id))
                if not exams_df.empty:
                    completed_weight, current_weighted_sum = 0.0, 0.0
                    for _, exam in exams_df.iterrows():
                        score = get_live_exam_score(int(exam["id"]), exam["score"])
                        if score <= 0: continue
                        weight = float(exam["weight"])
                        completed_weight += weight
                        current_weighted_sum += score * weight

                    if completed_weight > 0:
                        rem_weight = 100 - completed_weight
                        if rem_weight > 0:
                            st.write(f"Mevcut Tamamlanan Ağırlık: **%{completed_weight:.0f}** | Kalan Final Ağırlığı: **%{rem_weight:.0f}**")
                            target_letter = st.selectbox("Hedeflediğiniz Harf Notunu Seçin", list(HARF_ALT_SINIR.keys()), index=4, key=f"target_l_{course_id}")
                            target_min_score = HARF_ALT_SINIR[target_letter]
                            needed_final = (target_min_score * 100 - current_weighted_sum) / rem_weight

                            if needed_final <= 0:
                                st.success(f"🎉 Tebrikler! Zaten vize notlarınızla **{target_letter}** harf notunu garantilediniz.")
                            elif needed_final > 100:
                                st.error(f"⚠️ Finalden 100 bile alsanız bu dersten **{target_letter}** almak matematiksel olarak mümkün değil.")
                            else:
                                st.info(f"💡 **{target_letter}** alabilmek için Final sınavından minimum **{needed_final:.1f}** almanız gerekiyor.")
                        else:
                            st.write("Bu dersin tüm %100 değerlendirmeleri tamamlanmış.")
                    else:
                        st.warning("Girilmiş vize/quiz notu yok.")
                else:
                    st.info("Sınav eklenmemiş.")
    else:
        st.info("Lütfen önce derslerinizi tanımlayın.")

elif menu == "🎯 Dinamik AGNO / GANO Simülatörü":
    st.markdown("<h1 class='custom-header'>Dinamik AGNO / GANO (CGPA) Hesaplayıcı</h1>", unsafe_allow_html=True)
    st.caption("Şimdiye kadarki birikimli durumunuzu girin; ardından dönem derslerinizin harf notlarını seçerek YENİ GANO'nuzu ve Dönem Ortalamanızı canlı izleyin.")

    col_prev1, col_prev2, col_prev3 = st.columns(3)
    prev_gpa = col_prev1.number_input("Geçmiş Birikimli AGNO (CGPA)", min_value=0.0, max_value=4.0, value=float(profile["current_gpa"]), step=0.01, key="sim_prev_gpa")
    prev_credits = col_prev2.number_input("Tamamlanan Toplam Kredi", min_value=0, max_value=250, value=int(profile["current_credits"]), step=1, key="sim_prev_credits")
    prev_points = prev_gpa * prev_credits
    col_prev3.metric("Önceki Toplam Kalite Puanı", f"{prev_points:.1f} Puan")

    st.divider()
    st.subheader("📝 Aktif Dönem Tahmini Harf Notları")
    courses_df = pd.read_sql_query("SELECT id, code, name, credit, ects FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))

    if not courses_df.empty:
        term_credits, term_weighted_points = 0.0, 0.0
        col_c1, col_c2 = st.columns([2, 1])

        with col_c1:
            for _, c_row in courses_df.iterrows():
                course_id = int(c_row["id"])
                cc1, cc2, cc3 = st.columns([1, 2, 1])
                cc1.write(f"**{c_row['code']}**")
                cc2.write(f"{c_row['name']} *({c_row['credit']} Kredi)*")
                selected_letter = cc3.selectbox("Not", list(HARF_KATSAYI.keys()), index=0, key=f"letter_sim_{course_id}")
                c_credit = float(c_row["credit"])
                if c_credit > 0:
                    term_credits += c_credit
                    term_weighted_points += c_credit * HARF_KATSAYI[selected_letter]

        term_gpa = (term_weighted_points / term_credits) if term_credits > 0 else 0.0
        total_accumulated_credits = prev_credits + term_credits
        total_accumulated_points = prev_points + term_weighted_points
        new_cgpa = (total_accumulated_points / total_accumulated_credits) if total_accumulated_credits > 0 else 0.0
        cgpa_diff = new_cgpa - prev_gpa

        with col_c2:
            st.markdown("### 📊 Canlı Sonuçlar")
            st.metric("Dönem Ortalaması (GPA)", f"{term_gpa:.2f} / 4.00")
            st.metric("YENİ BİRİKİMLİ AGNO (CGPA)", f"{new_cgpa:.2f}", delta=f"{cgpa_diff:+.2f} Değişim")
            st.info(f"**Özet Tablo**\n\n• **Dönem Kredisi:** {term_credits:.0f} Kredi\n• **Dönem Kalite Puanı:** {term_weighted_points:.1f} Puan\n• **Yeni Toplam Kredi:** {total_accumulated_credits:.0f} Kredi\n• **Yeni AGNO:** {new_cgpa:.2f}")
    else:
        st.info("Simülasyon yapmak için öncelikle '⚙️ Ders & Müfredat Yönetimi' sekmesinden bu dönemin derslerini seçip ekleyin.")

elif menu == "⏱️ Pomodoro Çalışma Sayacı":
    st.markdown("<h1 class='custom-header'>Ders Odaklanma & Pomodoro Kronometresi</h1>", unsafe_allow_html=True)
    if "pomo_run" not in st.session_state: st.session_state["pomo_run"] = False
    if "pomo_seconds" not in st.session_state: st.session_state["pomo_seconds"] = 0

    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        pomo_minutes = st.number_input("Çalışma Süresi (Dakika)", min_value=1, max_value=120, value=25, step=1, key="pomo_minutes")
        if st.button("🚀 Çalışmayı Başlat", use_container_width=True):
            st.session_state["pomo_run"] = True
            st.session_state["pomo_seconds"] = int(pomo_minutes) * 60
            st.rerun()
        if st.session_state.get("pomo_run", False):
            if st.button("⏹️ Durdur", use_container_width=True):
                st.session_state["pomo_run"] = False
                st.rerun()

    with col_p2:
        if st.session_state.get("pomo_run", False):
            timer_placeholder = st.empty()
            while st.session_state["pomo_seconds"] > 0 and st.session_state.get("pomo_run", False):
                mins, secs = divmod(st.session_state["pomo_seconds"], 60)
                timer_str = f"{mins:02d}:{secs:02d}"
                timer_placeholder.markdown(f'<div class="pomo-card"><h1 style="font-size:64px; color:#38bdf8; margin:0;">{timer_str}</h1><p style="color:#a5b4fc;">Odaklanma Modu Aktif - İyi Çalışmalar!</p></div>', unsafe_allow_html=True)
                time.sleep(1)
                st.session_state["pomo_seconds"] -= 1

            if st.session_state["pomo_seconds"] == 0 and st.session_state.get("pomo_run", False):
                st.balloons()
                st.success("🎉 Harika! Çalışma seansı tamamlandı. Şimdi mola verebilirsin!")
                st.session_state["pomo_run"] = False
        else:
            st.markdown('<div class="pomo-card"><h2 style="color:#818cf8; margin:0;">25:00</h2><p style="color:#cbd5e1;">Başlamak için soldaki butona basın.</p></div>', unsafe_allow_html=True)

elif menu == "📊 Aylık Başarı Trendi":
    st.markdown("<h1 class='custom-header'>Aylık Başarı Eğrisi & Trend Analizi</h1>", unsafe_allow_html=True)
    df_trend = pd.read_sql_query("SELECT strftime('%Y-%m', event_date) AS Ay, AVG(score) AS Ortalama, COUNT(score) AS SinavSayisi FROM exams WHERE user_id = ? AND score IS NOT NULL AND score > 0 GROUP BY Ay ORDER BY Ay ASC", conn, params=(user_id,))

    if not df_trend.empty and len(df_trend) >= 1:
        st.subheader("📈 Pro Seviye Aylık Not Gelişim Grafiği")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_trend["Ay"], y=df_trend["Ortalama"], mode="lines+markers", name="Aylık Ortalama", line=dict(color="#38bdf8", width=4, shape="spline"), marker=dict(size=10, color="#818cf8", line=dict(color="#38bdf8", width=2)), hovertemplate="<b>Ay:</b> %{x}<br><b>Ortalama Not:</b> %{y:.2f} Puan<extra></extra>"))
        fig.update_layout(paper_bgcolor="rgba(15, 23, 42, 0.6)", plot_bgcolor="rgba(15, 23, 42, 0.6)", font=dict(color="#f8fafc", family="Inter, sans-serif"), margin=dict(l=20, r=20, t=30, b=20), xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Dönem / Ay"), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Ağırlıklı Sınav Ortalaması (0-100)", range=[0, 105]), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aylık başarı eğrisi için sınav tarihlerini ve aldığınız notları girmelisiniz.")

elif menu == "📅 Sınav Takvimi & Geri Sayım":
    st.markdown("<h1 class='custom-header'>Sınav Takvimi & Geri Sayım</h1>", unsafe_allow_html=True)
    with st.expander("➕ Yeni Sınav / Ödev Ekle"):
        courses = pd.read_sql_query("SELECT id, code FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))
        if not courses.empty:
            c_dict = dict(zip(courses["code"], courses["id"]))
            sel_c = st.selectbox("Ders", list(c_dict.keys()), key="new_exam_course")
            title = st.text_input("Etkinlik Adı", placeholder="Vize 1, Quiz 2 vb.", key="new_exam_title")
            e_type = st.selectbox("Tür", ["Vize", "Final", "Quiz", "Ödev / Rapor"], key="new_exam_type")
            e_date = st.date_input("Tarih", min_value=date.today(), key="new_exam_date")
            weight = st.slider("Ağırlık Yüzdesi (%)", 1, 100, 30, key="new_exam_weight")

            if st.button("Takvime Ekle", use_container_width=True):
                if not title.strip(): st.warning("Lütfen etkinlik adını girin.")
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO exams (user_id, course_id, title, event_type, event_date, weight) VALUES (?, ?, ?, ?, ?, ?)", (user_id, c_dict[sel_c], title.strip(), e_type, e_date, weight))
                    conn.commit()
                    st.toast(f"✅ {title} sınavı takvime eklendi!", icon="📅")
                    time.sleep(0.2)
                    st.rerun()
        else:
            st.info("Önce bir ders eklemeniz gerekiyor.")

    df_e = pd.read_sql_query("SELECT e.id, c.code AS Ders, e.title AS Etkinlik, e.event_type AS Tür, e.event_date AS Tarih, e.weight AS Agirlik, e.score AS Notu FROM exams e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ? ORDER BY e.event_date ASC", conn, params=(user_id,))
    if not df_e.empty:
        st.subheader("⏳ Yaklaşan Etkinlikler")
        today = date.today()
        for _, r in df_e.iterrows():
            ex_dt = datetime.strptime(str(r["Tarih"]), "%Y-%m-%d").date()
            d_left = (ex_dt - today).days
            col1, col2 = st.columns([4, 1])
            with col1:
                note_text = r["Notu"] if r["Notu"] is not None else "Girilmedi"
                st.write(f"📌 **{r['Ders']} - {r['Etkinlik']}** ({r['Tür']}) | Tarih: **{r['Tarih']}** | Kalan: **{d_left} Gün** | Not: **{note_text}**")
            with col2:
                if st.button("🗑️ Sil", key=f"del_ex_main_{r['id']}", use_container_width=True):
                    exam_id = int(r["id"])
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
                    conn.commit()
                    if f"ex_{exam_id}" in st.session_state: del st.session_state[f"ex_{exam_id}"]
                    st.toast("🗑️ Sınav silindi!", icon="🗑️")
                    time.sleep(0.2)
                    st.rerun()
    else:
        st.info("Henüz sınav veya etkinlik eklenmemiş.")

elif menu == "📝 Ders Notları":
    st.markdown("<h1 class='custom-header'>Ders Notları & Formül Defteri</h1>", unsafe_allow_html=True)
    courses = pd.read_sql_query("SELECT id, code, name FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))

    if not courses.empty:
        c_dict = dict(zip(courses["code"] + " - " + courses["name"], courses["id"]))
        sel_str = st.selectbox("Ders Seçin", list(c_dict.keys()), key="notes_course")
        sel_id = c_dict[sel_str]

        with st.expander("📝 Yeni Not Ekle", expanded=True):
            topic = st.text_input("Konu / Formül Başlığı", key="note_topic")
            tag = st.selectbox("Etiket", ["Genel Not", "Vize Konusu", "Final Konusu", "Formül / Denklemler"], key="note_tag")
            content = st.text_area("İçerik", height=120, key="note_content")

            if st.button("Notu Kaydet", use_container_width=True):
                if not topic.strip(): st.warning("Lütfen konu başlığı girin.")
                elif not content.strip(): st.warning("Lütfen not içeriğini girin.")
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO notes (user_id, course_id, topic, content, tag) VALUES (?, ?, ?, ?, ?)", (user_id, sel_id, topic.strip(), content.strip(), tag))
                    conn.commit()
                    st.toast("📝 Ders notu başarıyla eklendi!", icon="✅")
                    time.sleep(0.2)
                    st.rerun()

        st.subheader("📌 Geçmiş Notlar")
        notes_df = pd.read_sql_query("SELECT id, topic, content, tag, created_at FROM notes WHERE course_id = ? AND user_id = ? ORDER BY created_at DESC", conn, params=(sel_id, user_id))
        if not notes_df.empty:
            for _, n in notes_df.iterrows():
                with st.expander(f"📌 [{n['tag']}] {n['topic']} ({n['created_at']})"):
                    st.markdown(str(n["content"]))
                    if st.button("🗑️ Notu Sil", key=f"del_note_{n['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (int(n["id"]), user_id))
                        conn.commit()
                        st.toast("🗑️ Ders notu silindi!", icon="🗑️")
                        time.sleep(0.2)
                        st.rerun()
        else:
            st.info("Bu derse ait henüz not bulunmuyor.")
    else:
        st.info("Ders notu eklemek için önce ders ekleyin.")

elif menu == "🖨️ PDF / HTML Rapor Al":
    st.markdown("<h1 class='custom-header'>Akademik Durum Raporu (PDF / Baskı)</h1>", unsafe_allow_html=True)
    st.write("Derslerinizi, sınav notlarınızı ve ders notlarınızı tam Türkçe karakter desteğiyle raporlandırıp çıktı alın.")

    df_c_exp = pd.read_sql_query("SELECT code AS 'Ders Kodu', name AS 'Ders Adı', credit AS 'Yerel Kredi', ects AS 'AKTS' FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))
    df_e_exp = pd.read_sql_query("SELECT c.code AS 'Ders', e.title AS 'Etkinlik', e.event_type AS 'Tür', e.event_date AS 'Tarih', e.weight AS 'Ağırlık (%)', IFNULL(e.score, 'Girilmedi') AS 'Aldığı Not' FROM exams e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ? ORDER BY e.event_date ASC", conn, params=(user_id,))
    df_n_exp = pd.read_sql_query("SELECT c.code AS 'Ders', n.topic AS 'Konu', n.content AS 'İçerik', n.created_at AS 'Tarih' FROM notes n JOIN courses c ON n.course_id = c.id WHERE n.user_id = ? ORDER BY n.created_at DESC", conn, params=(user_id,))

    html_code = generate_html_report(profile, df_c_exp, df_e_exp, df_n_exp)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(label="📄 Rapor Belgesini İndir (.html / Baskıya Hazır)", data=html_code, file_name=f"IYTE_Akademik_Rapor_{date.today()}.html", mime="text/html", use_container_width=True)
    with col_d2:
        st.info("💡 **PDF Olarak Kaydetme**\n\nİndirdiğiniz HTML dosyasını tarayıcıda açın.\n\nArdından: **Ctrl + P → PDF Olarak Kaydet** seçeneğini kullanabilirsiniz.")

elif menu == "⚙️ Ders & Müfredat Yönetimi":
    st.markdown("<h1 class='custom-header'>Ders & Müfredat Yönetimi</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔍 İYTE Ders Havuzundan Seç", "➕ Özel / Seçmeli Ders Ekle", "🗑️ Kayıtlı Dersleri Yönet & Sil"])

    with tab1:
        st.subheader("İYTE Makine Mühendisliği Ders Havuzu")
        st.caption("İstediğin yarıyıllardan almak istediğin dersleri tikleyerek tek tek ekleyebilirsin.")
        sem_filter = st.multiselect("Yarıyıla Göre Filtrele (Tümü Görmek İçin Boş Bırakın)", [1, 2, 3, 4, 5, 6, 7, 8], default=[5], key="semester_filter")
        filtered_courses = [c for c in IYTE_ALL_COURSES if c["sem"] in sem_filter] if sem_filter else IYTE_ALL_COURSES
        selected_to_add = []

        for item in filtered_courses:
            chk = st.checkbox(f"**{item['code']}** - {item['name']} *({item['credit']} Kredi / {item['ects']} AKTS)*", key=f"chk_{item['code']}")
            if chk: selected_to_add.append(item)

        if st.button("✅ Seçilen Dersleri Sayfama Ekle", use_container_width=True):
            if selected_to_add:
                count = 0
                cursor = conn.cursor()
                for c in selected_to_add:
                    check_db = pd.read_sql_query("SELECT id FROM courses WHERE code = ? AND user_id = ?", conn, params=(c["code"], user_id))
                    if check_db.empty:
                        cursor.execute("INSERT INTO courses (user_id, code, name, credit, ects, semester) VALUES (?, ?, ?, ?, ?, ?)", (user_id, c["code"], c["name"], c["credit"], c["ects"], c["sem"]))
                        count += 1
                conn.commit()
                st.toast(f"🎉 {count} yeni ders sayfanıza eklendi!", icon="✅")
                time.sleep(0.3)
                st.rerun()
            else:
                st.warning("Lütfen eklemek istediğiniz dersleri işaretleyin.")

    with tab2:
        st.subheader("Manuel / Seçmeli Ders Ekleme")
        m_code = st.text_input("Ders Kodu", placeholder="Örn: ME 451", key="manual_course_code")
        m_name = st.text_input("Ders Adı", placeholder="Örn: Isıl Sistemler Tasarımı", key="manual_course_name")
        m_credit = st.number_input("Yerel Kredi", min_value=0, max_value=10, value=3, step=1, key="manual_course_credit")
        m_ects = st.number_input("AKTS Değeri", min_value=1, max_value=30, value=5, step=1, key="manual_course_ects")

        if st.button("Seçmeli Dersi Kaydet", use_container_width=True):
            if not m_code.strip(): st.warning("Lütfen ders kodunu girin.")
            elif not m_name.strip(): st.warning("Lütfen ders adını girin.")
            else:
                existing = pd.read_sql_query("SELECT id FROM courses WHERE user_id = ? AND code = ?", conn, params=(user_id, m_code.strip()))
                if not existing.empty:
                    st.warning("Bu ders zaten kayıtlı.")
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO courses (user_id, code, name, credit, ects, semester) VALUES (?, ?, ?, ?, ?, ?)", (user_id, m_code.strip(), m_name.strip(), m_credit, m_ects, 5))
                    conn.commit()
                    st.toast(f"✅ {m_code} seçmeli dersi eklendi!", icon="🎉")
                    time.sleep(0.3)
                    st.rerun()

    with tab3:
        st.subheader("Kayıtlı Dersleri Sil & Yönet")
        df_c = pd.read_sql_query("SELECT id, code AS 'Kodu', name AS 'Adı', credit AS 'Kredi', ects AS 'AKTS' FROM courses WHERE user_id = ? ORDER BY semester, code", conn, params=(user_id,))
        if not df_c.empty:
            for _, r in df_c.iterrows():
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"📘 **{r['Kodu']}** - {r['Adı']} ({r['Kredi']} Kredi / {r['AKTS']} AKTS)")
                with col_b:
                    if st.button("🗑️ Dersi Sil", key=f"del_course_{r['id']}", use_container_width=True):
                        course_id = int(r["id"])
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM exams WHERE course_id = ? AND user_id = ?", (course_id, user_id))
                        cursor.execute("DELETE FROM notes WHERE course_id = ? AND user_id = ?", (course_id, user_id))
                        cursor.execute("DELETE FROM courses WHERE id = ? AND user_id = ?", (course_id, user_id))
                        conn.commit()

                        keys_to_delete = [k for k in st.session_state.keys() if str(k).startswith("ex_")]
                        for key in keys_to_delete: del st.session_state[key]

                        st.toast(f"🗑️ {r['Kodu']} dersi başarıyla silindi!", icon="🗑️")
                        time.sleep(0.3)
                        st.rerun()
        else:
            st.info("Kayıtlı ders bulunmuyor.")

# =============================================================================
# 9. BAĞLANTI KAPATMA
# =============================================================================

try:
    conn.close()
except Exception:
    pass
