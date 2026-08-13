import streamlit as st
import pandas as pd
from datetime import datetime, date
import database as db
import plotly.graph_objects as go
import time
import uuid

# -----------------------------------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU & MOBİL UYUMLU CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="İYTE Makine | Akademik Yönetim Platformu",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
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
    }
    .pomo-card {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    @media (max-width: 768px) {
        .stApp { padding: 5px; }
        div[data-testid="stMetric"] { padding: 12px; }
        .custom-header { font-size: 22px !important; }
        .stButton>button { width: 100%; border-radius: 10px; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. VERİTABANI İNİTİALİZASYONU VE OTURUM İZOLASYONU (USER_ID)
# -----------------------------------------------------------------------------
db.init_db()
conn = db.get_connection()

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = str(uuid.uuid4())

user_id = st.session_state['user_id']

# Kullanıcı Profilini Getir
prof_row = db.get_or_create_profile(user_id)
profile = {
    "name": prof_row[0],
    "department": prof_row[1],
    "grade": prof_row[2],
    "current_gpa": prof_row[3] if prof_row[3] is not None else 3.00,
    "current_credits": prof_row[4] if prof_row[4] is not None else 60
}

# -----------------------------------------------------------------------------
# 3. İYTE HARF NOTLARI VE DERS HAVUZU
# -----------------------------------------------------------------------------
HARF_KATSAYI = {
    "AA": 4.0, "BA": 3.5, "BB": 3.0, "CB": 2.5,
    "CC": 2.0, "DC": 1.5, "DD": 1.0, "FF": 0.0
}

HARF_ALT_SINIR = {
    "AA": 90, "BA": 85, "BB": 80, "CB": 75,
    "CC": 70, "DC": 65, "DD": 60
}

IYTE_ALL_COURSES = [
    # 1. Yarıyıl
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
    
    # 2. Yarıyıl
    {"code": "CS106", "name": "TEMEL BİLGİSAYAR BİLİMİ VE PROGRAMLAMASI", "credit": 3, "ects": 5, "sem": 2},
    {"code": "ENG102", "name": "İNGİLİZCE OKUMA VE YAZMA BECERİLERİ II", "credit": 3, "ects": 3, "sem": 2},
    {"code": "GCC101", "name": "KARİYER PLANLAMA VE GELİŞTİRME", "credit": 0, "ects": 2, "sem": 2},
    {"code": "MATH142", "name": "TEMEL ANALİZ II", "credit": 4, "ects": 6, "sem": 2},
    {"code": "ME114", "name": "BİLGİSAYAR DESTEKLİ TEKNİK RESİM II", "credit": 3, "ects": 4, "sem": 2},
    {"code": "ME150", "name": "MALZEME BİLİMİ VE MÜHENDİSLİĞİ I", "credit": 3, "ects": 4, "sem": 2},
    {"code": "PHYS102", "name": "GENEL FİZİK II", "credit": 4, "ects": 5, "sem": 2},
    {"code": "PHYS112", "name": "GENEL FİZİK LAB. II", "credit": 1, "ects": 2, "sem": 2},
    {"code": "OHS 102", "name": "İş Sağlığı ve Güvenliği II", "credit": 1, "ects": 1, "sem": 2},

    # 3. Yarıyıl
    {"code": "HIST201", "name": "ATATÜRK İLKELERİ VE İNKILAP TARİHİ I", "credit": 0, "ects": 2, "sem": 3},
    {"code": "TURK201", "name": "TÜRK DİLİ DERSLERİ I", "credit": 0, "ects": 2, "sem": 3},
    {"code": "ECON205", "name": "EKONOMİNİN PRENSİPLERİ", "credit": 3, "ects": 4, "sem": 3},
    {"code": "MATH255", "name": "DİFERANSİYEL DENKLEMLER", "credit": 4, "ects": 6, "sem": 3},
    {"code": "ME207", "name": "TERMODİNAMİK I", "credit": 3, "ects": 6, "sem": 3},
    {"code": "ME221", "name": "STATİK", "credit": 3, "ects": 5, "sem": 3},
    {"code": "ME251", "name": "MALZEME BİLİMİ VE MÜHENDİSLİĞİ II", "credit": 3, "ects": 5, "sem": 3},

    # 4. Yarıyıl
    {"code": "HIST202", "name": "ATATÜRK İLKELERİ VE İNKILAP TARİHİ II", "credit": 0, "ects": 2, "sem": 4},
    {"code": "TURK202", "name": "TÜRK DİLİ DERSLERİ II", "credit": 0, "ects": 2, "sem": 4},
    {"code": "EE210", "name": "ELEKTRİK VE ELEKTRONİK DEVRELERİNİN TEMELLERİ", "credit": 3, "ects": 4, "sem": 4},
    {"code": "ME208", "name": "TERMODİNAMİK II", "credit": 3, "ects": 6, "sem": 4},
    {"code": "ME222", "name": "DİNAMİK", "credit": 3, "ects": 5, "sem": 4},
    {"code": "ME224", "name": "CİSİMLERİN MUKAVEMETİ", "credit": 3, "ects": 5, "sem": 4},
    {"code": "ME242", "name": "MÜHENDİSLER İÇİN UYGULAMALI MATEMATİK", "credit": 4, "ects": 6, "sem": 4},

    # 5. Yarıyıl
    {"code": "ENG301", "name": "TEKNİK YAZIM VE İLETİŞİM", "credit": 3, "ects": 3, "sem": 5},
    {"code": "ME300", "name": "TALAŞLI İMALAT / METAL ŞEKİLLENDİRME STAJI", "credit": 0, "ects": 7, "sem": 5},
    {"code": "ME301", "name": "AKIŞKANLAR MEKANİĞİ I", "credit": 3, "ects": 5, "sem": 5},
    {"code": "ME311", "name": "MAKİNA ELEMANLARI I", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME323", "name": "ÜRETİM YÖNTEMLERİ", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME331", "name": "MAKİNA TEORİSİ I", "credit": 3, "ects": 4, "sem": 5},
    {"code": "ME343", "name": "MÜHENDİSLİKTE SAYISAL YÖNTEMLER", "credit": 3, "ects": 3, "sem": 5},

    # 6. Yarıyıl
    {"code": "ME302", "name": "AKIŞKANLAR MEKANİĞİ II", "credit": 3, "ects": 6, "sem": 6},
    {"code": "ME312", "name": "MAKİNA ELEMANLARI II", "credit": 3, "ects": 6, "sem": 6},
    {"code": "ME328", "name": "ÜRETİM MÜHENDİSLİĞİ", "credit": 3, "ects": 5, "sem": 6},
    {"code": "ME332", "name": "MAKİNA TEORİSİ II", "credit": 3, "ects": 5, "sem": 6},
    {"code": "ME340", "name": "ISI TRANSFERİ", "credit": 4, "ects": 5, "sem": 6},
    {"code": "ME352", "name": "SİSTEM ANALİZİ VE KONTROL", "credit": 4, "ects": 5, "sem": 6},

    # 7. & 8. Yarıyıl
    {"code": "ME400", "name": "ENDÜSTRİYEL ORGANİZASYON STAJI", "credit": 0, "ects": 9, "sem": 7},
    {"code": "ME401", "name": "MÜHENDİSLİK EKONOMİSİ VE TASARIM", "credit": 4, "ects": 6, "sem": 7},
    {"code": "ME409", "name": "MAKİNA MÜHENDİSLİĞİ LABORATUVARI", "credit": 3, "ects": 4, "sem": 7},
    {"code": "ME402", "name": "MÜHENDİSLİK TASARIM DERSLERİ", "credit": 4, "ects": 12, "sem": 8},
]

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
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 12px;">Rapor Oluşturma Tarihi: {date.today().strftime('%d.%m.%Y')}</p>
        </div>
        
        <div class="profile-info">
            <strong>Öğrenci / Kullanıcı:</strong> {profile_data['name']}<br>
            <strong>Bölüm / Akademik Düzey:</strong> {profile_data['department']} - {profile_data['grade']}<br>
            <strong>Girdiği Birikimli AGNO (CGPA):</strong> {profile_data['current_gpa']} / 4.00 (Tamamlanan Kredi: {profile_data['current_credits']})
        </div>

        <div class="section-title">1. Aktif Dönem Ders Listesi ve Kredi Yükü</div>
        {df_courses_summary.to_html(index=False, escape=False) if not df_courses_summary.empty else '<p>Kayıtlı ders bulunmamaktadır.</p>'}

        <div class="section-title">2. Değerlendirmeler & Sınav Not Transkripti</div>
        {df_exams_summary.to_html(index=False, escape=False) if not df_exams_summary.empty else '<p>Sınav kaydı bulunmamaktadır.</p>'}

        <div class="section-title">3. Önemli Ders Notları Defteri</div>
    """
    if not df_notes_summary.empty:
        for _, n in df_notes_summary.head(10).iterrows():
            html_content += f"""
            <div class="note-box">
                <strong>[{n['Ders']}] {n['Konu']}</strong> <span style="font-size:11px; color:#64748b;">({n['Tarih']})</span><br>
                <span>{n['İçerik']}</span>
            </div>
            """
    else:
        html_content += "<p>Kayıtlı ders notu yok.</p>"
        
    html_content += """
    </body>
    </html>
    """
    return html_content

# -----------------------------------------------------------------------------
# 4. YAN MENÜ & BİLGİLERİN SAKLANMASI
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="profile-card">
        <h3 style="margin:0; color:#f8fafc; font-size:18px;">🎓 {profile['name']}</h3>
        <p style="margin:4px 0 0 0; color:#a5b4fc; font-size:12px;">İYTE - {profile['department']}</p>
        <span style="background:#4f46e5; color:white; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold;">{profile['grade']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👤 Kullanıcı Profil Bilgilerini Değiştir"):
        u_name = st.text_input("Ad Soyad / Kullanıcı Adı", value=profile['name'])
        u_dept = st.text_input("Bölüm", value=profile['department'])
        u_grade = st.selectbox("Sınıf", ["1. Sınıf", "2. Sınıf", "3. Sınıf", "4. Sınıf", "Lisans"], index=2)
        u_gpa = st.number_input("Geçmiş AGNO (CGPA)", min_value=0.0, max_value=4.0, value=float(profile['current_gpa']), step=0.01)
        u_credits = st.number_input("Geçmiş Tamamlanan Kredi", min_value=0, max_value=250, value=int(profile['current_credits']), step=1)
        
        if st.button("💾 Bilgilerimi Kalıcı Kaydet"):
            db.update_profile(user_id, u_name, u_dept, u_grade, u_gpa, u_credits)
            st.toast("✅ Profil bilgileriniz başarıyla kaydedildi!", icon="🎉")
            time.sleep(0.8)
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

# Akıllı Uyarı Engine
df_alert = pd.read_sql_query('''
    SELECT c.code, e.title, e.event_date 
    FROM exams e JOIN courses c ON e.course_id = c.id 
    WHERE e.user_id = ? AND e.event_date >= DATE('now') 
    ORDER BY e.event_date ASC LIMIT 1
''', conn, params=(user_id,))

if not df_alert.empty and menu not in ["⏱️ Pomodoro Çalışma Sayacı", "🖨️ PDF / HTML Rapor Al"]:
    ex_date = datetime.strptime(df_alert.iloc[0]['event_date'], "%Y-%m-%d").date()
    days_left = (ex_date - date.today()).days
    st.markdown(f"""
    <div class="alert-card">
        🚨 <b>YAKLAŞAN AKADEMİK ETKİNLİK UYARISI:</b> <b>{df_alert.iloc[0]['code']} - {df_alert.iloc[0]['title']}</b> sınavına 
        <b>{days_left} gün</b> kaldı! Tarih: <i>{df_alert.iloc[0]['event_date']}</i>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. DÖNEM & GENEL NOT ORTALAMASI BİRLEŞİK HESAPLAMA METODU (TEK VİZE DAHİL BİLE CANLI DİNAMİK)
# -----------------------------------------------------------------------------
def calculate_combined_gpa():
    courses_df = pd.read_sql_query("SELECT id, credit, ects FROM courses WHERE user_id = ?", conn, params=(user_id,))
    
    if courses_df.empty:
        return 0.0, profile['current_gpa'], 0, 0
        
    total_term_credits = courses_df['credit'].sum()
    total_term_ects = courses_df['ects'].sum()
    
    evaluated_term_credits = 0
    term_weighted_points = 0
    
    for _, c_row in courses_df.iterrows():
        c_credit = c_row['credit']
        # En az bir notu girilmiş (score IS NOT NULL) sınavları çekiyoruz
        exams_df = pd.read_sql_query(
            "SELECT weight, score FROM exams WHERE course_id = ? AND user_id = ? AND score IS NOT NULL", 
            conn, params=(c_row['id'], user_id)
        )
        
        if not exams_df.empty:
            tot_w = exams_df['weight'].sum()
            if tot_w > 0:
                w_sum = (exams_df['score'] * exams_df['weight']).sum()
                course_avg = w_sum / tot_w # O ana kadar girilmiş vizelerin kendi içindeki ağırlıklı ortalaması
                
                # İYTE Harf Notu Karşılığı
                if course_avg >= 90: letter_coeff = 4.0
                elif course_avg >= 85: letter_coeff = 3.5
                elif course_avg >= 80: letter_coeff = 3.0
                elif course_avg >= 75: letter_coeff = 2.5
                elif course_avg >= 70: letter_coeff = 2.0
                elif course_avg >= 65: letter_coeff = 1.5
                elif course_avg >= 60: letter_coeff = 1.0
                else: letter_coeff = 0.0
                
                evaluated_term_credits += c_credit
                term_weighted_points += c_credit * letter_coeff

    term_gpa = (term_weighted_points / evaluated_term_credits) if evaluated_term_credits > 0 else 0.0
    
    prev_points = profile['current_gpa'] * profile['current_credits']
    tot_accumulated_credits = profile['current_credits'] + evaluated_term_credits
    tot_accumulated_points = prev_points + term_weighted_points
    
    new_combined_cgpa = (tot_accumulated_points / tot_accumulated_credits) if tot_accumulated_credits > 0 else profile['current_gpa']
    
    return term_gpa, new_combined_cgpa, total_term_credits, total_term_ects

# -----------------------------------------------------------------------------
# 6. MODÜLLER
# -----------------------------------------------------------------------------

# --- MODÜL 1: DÖNEM & SINAV NOT TAKİBİ ---
if menu == "📈 Dönem & Sınav Not Takibi":
    st.markdown("<h1 class='custom-header'>Akademik Performans & Not Takibi</h1>", unsafe_allow_html=True)
    
    term_gpa, combined_cgpa, total_term_credits, total_term_ects = calculate_combined_gpa()
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Geçmiş Birikimli AGNO", f"{profile['current_gpa']:.2f}")
    c2.metric("Güncel Dönem Ortalaması (GPA)", f"{term_gpa:.2f}")
    c3.metric("DÖNEM SONU BEKLENEN AGNO", f"{combined_cgpa:.2f}", delta=f"{combined_cgpa - profile['current_gpa']:+.2f}")
    c4.metric("Aktif Dönem Kredisi", f"{total_term_credits} Kredi")
    c5.metric("Aktif Dönem AKTS", f"{total_term_ects} AKTS")

    st.divider()
    courses_df = pd.read_sql_query("SELECT id, code, name, credit, ects FROM courses WHERE user_id = ?", conn, params=(user_id,))
    
    if not courses_df.empty:
        for _, c_row in courses_df.iterrows():
            with st.expander(f"📘 **{c_row['code']} - {c_row['name']}** ({c_row['credit']} Kredi / {c_row['ects']} AKTS)", expanded=True):
                exams_df = pd.read_sql_query(
                    "SELECT id, title, event_type, weight, score FROM exams WHERE course_id = ? AND user_id = ?", 
                    conn, params=(c_row['id'], user_id)
                )
                
                col_e1, col_e2 = st.columns([2, 1])
                
                with col_e1:
                    if not exams_df.empty:
                        for _, ex in exams_df.iterrows():
                            ca, cb, cc, cd = st.columns([2, 1, 1, 1])
                            ca.write(f"• **{ex['title']}** (%{ex['weight']})")
                            
                            curr_s = ex['score'] if ex['score'] is not None else 0.0
                            new_s = cb.number_input("Not", min_value=0.0, max_value=100.0, value=float(curr_s), key=f"ex_{ex['id']}")
                            
                            if cc.button("Kaydet", key=f"btn_s_{ex['id']}"):
                                cursor = conn.cursor()
                                cursor.execute("UPDATE exams SET score = ? WHERE id = ? AND user_id = ?", (new_s, ex['id'], user_id))
                                conn.commit()
                                st.toast(f"✅ {ex['title']} notu kaydedildi!", icon="💾")
                                time.sleep(0.5)
                                st.rerun()
                                
                            if cd.button("🗑️ Sil", key=f"btn_del_ex_{ex['id']}"):
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (ex['id'], user_id))
                                conn.commit()
                                st.toast("🗑️ Sınav silindi!", icon="⚠️")
                                time.sleep(0.5)
                                st.rerun()
                    else:
                        st.info("Bu ders için henüz sınav eklenmedi.")
                        
                with col_e2:
                    if not exams_df.empty:
                        completed = exams_df[exams_df['score'].notnull()]
                        if not completed.empty:
                            tot_w = completed['weight'].sum()
                            w_sum = (completed['score'] * completed['weight']).sum()
                            c_avg = w_sum / tot_w if tot_w > 0 else 0
                            
                            st.markdown(f"**Ağırlıklı Ortalama (%{tot_w}):**")
                            st.subheader(f"{c_avg:.2f} / 100")
                            st.caption(f"Tahmini Harf Notu: **{calculate_iyte_letter(c_avg)}**")
                        else:
                            st.write("Girilmiş sınav notu yok.")
    else:
        st.info("Henüz eklenmiş bir dersiniz yok. '⚙️ Ders & Müfredat Yönetimi' sekmesinden derslerinizi ekleyebilirsiniz.")

# --- MODÜL 2: GEREKLİ FİNAL NOTU HESAPLAYICI ---
elif menu == "🎯 Gerekli Final Notu Hesaplayıcı":
    st.markdown("<h1 class='custom-header'>Hedef Harf Notu İçin Gerekli Final Notu</h1>", unsafe_allow_html=True)
    st.caption("Girdiğiniz vize/quiz notlarına göre istediğiniz harf notunu alabilmek için Final sınavından kaç almanız gerektiğini hesaplar.")
    
    courses_df = pd.read_sql_query("SELECT id, code, name FROM courses WHERE user_id = ?", conn, params=(user_id,))
    
    if not courses_df.empty:
        for _, c_row in courses_df.iterrows():
            with st.expander(f"🎯 **{c_row['code']} - {c_row['name']}**", expanded=True):
                exams_df = pd.read_sql_query("SELECT title, weight, score FROM exams WHERE course_id = ? AND user_id = ?", conn, params=(c_row['id'], user_id))
                
                if not exams_df.empty:
                    completed_exams = exams_df[exams_df['score'].notnull()]
                    if not completed_exams.empty:
                        tot_w = completed_exams['weight'].sum()
                        current_weighted_sum = (completed_exams['score'] * completed_exams['weight']).sum()
                        rem_weight = 100 - tot_w
                        
                        if rem_weight > 0:
                            st.write(f"Mevcut Tamamlanan Ağırlık: **%{tot_w}** | Kalan Final Ağırlığı: **%{rem_weight}**")
                            
                            target_letter = st.selectbox("Hedeflediğiniz Harf Notunu Seçin", list(HARF_ALT_SINIR.keys()), index=4, key=f"target_l_{c_row['id']}")
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

# --- MODÜL 3: DİNAMİK AGNO / GANO (CGPA) SİMÜLATÖRÜ ---
elif menu == "🎯 Dinamik AGNO / GANO Simülatörü":
    st.markdown("<h1 class='custom-header'>Dinamik AGNO / GANO (CGPA) Hesaplayıcı</h1>", unsafe_allow_html=True)
    st.caption("Şimdiye kadarki birikimli durumunuzu girin; ardından dönem derslerinizin harf notlarını seçerek YENİ GANO'nuzu ve Dönem Ortalamanızı canlı izleyin.")
    
    col_prev1, col_prev2, col_prev3 = st.columns(3)
    prev_gpa = col_prev1.number_input("Geçmiş Birikimli AGNO (CGPA)", min_value=0.0, max_value=4.0, value=float(profile['current_gpa']), step=0.01)
    prev_credits = col_prev2.number_input("Tamamlanan Toplam Kredi", min_value=0, max_value=200, value=int(profile['current_credits']), step=1)
    
    prev_points = prev_gpa * prev_credits
    col_prev3.metric("Önceki Toplam Kalite Puanı", f"{prev_points:.1f} Puan")
    
    st.divider()
    st.subheader("📝 Aktif Dönem Tahmini Harf Notları")
    
    courses_df = pd.read_sql_query("SELECT id, code, name, credit, ects FROM courses WHERE user_id = ?", conn, params=(user_id,))
    
    if not courses_df.empty:
        term_credits = 0
        term_weighted_points = 0
        
        col_c1, col_c2 = st.columns([2, 1])
        
        with col_c1:
            for _, c_row in courses_df.iterrows():
                cc1, cc2, cc3 = st.columns([1, 2, 1])
                cc1.write(f"**{c_row['code']}**")
                cc2.write(f"{c_row['name']} *({c_row['credit']} Kredi)*")
                
                selected_letter = cc3.selectbox(
                    f"Not", 
                    list(HARF_KATSAYI.keys()), 
                    index=0, 
                    key=f"letter_sim_{c_row['id']}"
                )
                
                c_credit = c_row['credit']
                term_credits += c_credit
                term_weighted_points += c_credit * HARF_KATSAYI[selected_letter]
        
        term_gpa = (term_weighted_points / term_credits) if term_credits > 0 else 0.0
        
        total_accumulated_credits = prev_credits + term_credits
        total_accumulated_points = prev_points + term_weighted_points
        new_cgpa = (total_accumulated_points / total_accumulated_credits) if total_accumulated_credits > 0 else 0.0
        cgpa_diff = new_cgpa - prev_gpa

        with col_c2:
            st.markdown("### 📊 Canlı Sonuçlar")
            st.metric("Dönem Ortalaması (SPA / GPA)", f"{term_gpa:.2f} / 4.00")
            st.metric("YENİ BİRİKİMLİ AGNO (CGPA)", f"{new_cgpa:.2f}", delta=f"{cgpa_diff:+.2f} Değişim")
            
            st.info(f"""
            **Özet Tablo:**
            * **Dönem Kredisi:** {term_credits} Kredi
            * **Dönem Kalite Puanı:** {term_weighted_points:.1f} Puan
            * **Yeni Toplam Kredi:** {total_accumulated_credits} Kredi
            """)
    else:
        st.info("Simülasyon yapmak için öncelikle '⚙️ Ders & Müfredat Yönetimi' sekmesinden bu dönemin derslerini seçip ekleyin.")

# --- MODÜL 4: POMODORO ÇALIŞMA SAYACI ---
elif menu == "⏱️ Pomodoro Çalışma Sayacı":
    st.markdown("<h1 class='custom-header'>Ders Odaklanma & Pomodoro Kronometresi</h1>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        pomo_minutes = st.number_input("Çalışma Süresi (Dakika)", min_value=1, max_value=120, value=25)
        if st.button("🚀 Çalışmayı Başlat"):
            st.session_state['pomo_run'] = True
            st.session_state['pomo_seconds'] = pomo_minutes * 60

    with col_p2:
        if st.session_state.get('pomo_run', False):
            timer_placeholder = st.empty()
            while st.session_state['pomo_seconds'] > 0 and st.session_state.get('pomo_run', False):
                mins, secs = divmod(st.session_state['pomo_seconds'], 60)
                timer_str = f"{mins:02d}:{secs:02d}"
                timer_placeholder.markdown(f"""
                <div class="pomo-card">
                    <h1 style="font-size: 64px; color: #38bdf8; margin:0;">{timer_str}</h1>
                    <p style="color:#a5b4fc;">Odaklanma Modu Aktif - İyi Çalışmalar!</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.session_state['pomo_seconds'] -= 1
                
            if st.session_state['pomo_seconds'] == 0:
                st.balloons()
                st.success("🎉 Harika! Çalışma seansı tamamlandı. Şimdi mola verebilirsin!")
                st.session_state['pomo_run'] = False
        else:
            st.markdown("""
            <div class="pomo-card">
                <h2 style="color: #818cf8; margin:0;">25:00</h2>
                <p style="color:#cbd5e1;">Başlamak için soldaki butona basın.</p>
            </div>
            """, unsafe_allow_html=True)

# --- MODÜL 5: AYLIK BAŞARI TRENDİ ---
elif menu == "📊 Aylık Başarı Trendi":
    st.markdown("<h1 class='custom-header'>Aylık Başarı Eğrisi & Trend Analizi</h1>", unsafe_allow_html=True)
    
    query_monthly = '''
        SELECT strftime('%Y-%m', event_date) AS Ay, AVG(score) AS Ortalama, COUNT(score) AS SinavSayisi
        FROM exams
        WHERE user_id = ? AND score IS NOT NULL
        GROUP BY Ay
        ORDER BY Ay ASC
    '''
    df_trend = pd.read_sql_query(query_monthly, conn, params=(user_id,))
    
    if not df_trend.empty and len(df_trend) >= 1:
        st.subheader("📈 Pro Seviye Aylık Not Gelişim Grafiği")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend['Ay'],
            y=df_trend['Ortalama'],
            mode='lines+markers',
            name='Aylık Ortalama',
            line=dict(color='#38bdf8', width=4, shape='spline'),
            marker=dict(size=10, color='#818cf8', line=dict(color='#38bdf8', width=2)),
            hovertemplate='<b>Ay:</b> %{x}<br><b>Ortalama Not:</b> %{y:.2f} Puan<extra></extra>'
        ))

        fig.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.6)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            font=dict(color='#f8fafc', family='Inter, sans-serif'),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.08)', title='Dönem / Ay'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.08)', title='Ağırlıklı Sınav Ortalaması (0-100)', range=[0, 105]),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aylık başarı eğrisi için sınav tarihlerini ve aldığınız notları girmelisiniz.")

# --- MODÜL 6: SINAV TAKVİMİ & GERİ SAYIM ---
elif menu == "📅 Sınav Takvimi & Geri Sayım":
    st.markdown("<h1 class='custom-header'>Sınav Takvimi & Geri Sayım</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ Yeni Sınav / Ödev Ekle"):
        courses = pd.read_sql_query("SELECT id, code FROM courses WHERE user_id = ?", conn, params=(user_id,))
        if not courses.empty:
            c_dict = dict(zip(courses['code'], courses['id']))
            sel_c = st.selectbox("Ders", list(c_dict.keys()))
            title = st.text_input("Etkinlik Adı", placeholder="Vize 1, Quiz 2 vb.")
            e_type = st.selectbox("Tür", ["Vize", "Final", "Quiz", "Ödev / Rapor"])
            e_date = st.date_input("Tarih", min_value=date.today())
            weight = st.slider("Ağırlık Yüzdesi (%)", 1, 100, 30)
            
            if st.button("Takvime Ekle"):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO exams (user_id, course_id, title, event_type, event_date, weight) VALUES (?, ?, ?, ?, ?, ?)",
                               (user_id, c_dict[sel_c], title, e_type, e_date, weight))
                conn.commit()
                st.toast(f"✅ {title} sınavı takvime eklendi!", icon="📅")
                time.sleep(0.5)
                st.rerun()

    df_e = pd.read_sql_query('''
        SELECT e.id, c.code AS Ders, e.title AS Etkinlik, e.event_type AS Tür, e.event_date AS Tarih, e.weight AS Agirlik, e.score AS Notu
        FROM exams e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ? ORDER BY e.event_date ASC
    ''', conn, params=(user_id,))
    
    if not df_e.empty:
        st.subheader("⏳ Yaklaşan Etkinlikler")
        today = date.today()
        for _, r in df_e.iterrows():
            ex_dt = datetime.strptime(r['Tarih'], "%Y-%m-%d").date()
            d_left = (ex_dt - today).days
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 **{r['Ders']} - {r['Etkinlik']}** ({r['Tür']}) | Tarih: **{r['Tarih']}** | Kalan: **{d_left} Gün** | Not: **{r['Notu'] if r['Notu'] is not None else 'Girilmedi'}**")
            with col2:
                if st.button("🗑️ Sil", key=f"del_ex_main_{r['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM exams WHERE id = ? AND user_id = ?", (r['id'], user_id))
                    conn.commit()
                    st.toast("🗑️ Sınav silindi!", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

# --- MODÜL 7: DERS NOTLARI ---
elif menu == "📝 Ders Notları":
    st.markdown("<h1 class='custom-header'>Ders Notları & Formül Defteri</h1>", unsafe_allow_html=True)
    courses = pd.read_sql_query("SELECT id, code, name FROM courses WHERE user_id = ?", conn, params=(user_id,))
    
    if not courses.empty:
        c_dict = dict(zip(courses['code'] + " - " + courses['name'], courses['id']))
        sel_str = st.selectbox("Ders Seçin", list(c_dict.keys()))
        sel_id = c_dict[sel_str]
        
        with st.expander("📝 Yeni Not Ekle", expanded=True):
            topic = st.text_input("Konu / Formül Başlığı")
            tag = st.selectbox("Etiket", ["Genel Not", "Vize Konusu", "Final Konusu", "Formül / Denklemler"])
            content = st.text_area("İçerik", height=120)
            
            if st.button("Notu Kaydet"):
                cursor = conn.cursor()
                cursor.execute("INSERT INTO notes (user_id, course_id, topic, content, tag) VALUES (?, ?, ?, ?, ?)", (user_id, sel_id, topic, content, tag))
                conn.commit()
                st.toast("📝 Ders notu başarıyla eklendi!", icon="✅")
                time.sleep(0.5)
                st.rerun()

        st.subheader("📌 Geçmiş Notlar")
        notes_df = pd.read_sql_query("SELECT id, topic, content, tag, created_at FROM notes WHERE course_id = ? AND user_id = ? ORDER BY created_at DESC", conn, params=(sel_id, user_id))
        for _, n in notes_df.iterrows():
            with st.expander(f"📌 [{n['tag']}] {n['topic']} ({n['created_at']})"):
                st.markdown(n['content'])
                if st.button("🗑️ Notu Sil", key=f"del_note_{n['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (n['id'], user_id))
                    conn.commit()
                    st.toast("🗑️ Ders notu silindi!", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

# --- MODÜL 8: PDF / HTML RAPOR AL ---
elif menu == "🖨️ PDF / HTML Rapor Al":
    st.markdown("<h1 class='custom-header'>Akademik Durum Raporu (PDF / Baskı)</h1>", unsafe_allow_html=True)
    st.write("Derslerinizi, sınav notlarınızı ve ders notlarınızı tam Türkçe karakter desteğiyle raporlandırıp çıktı alın.")
    
    df_c_exp = pd.read_sql_query("SELECT code AS 'Ders Kodu', name AS 'Ders Adı', credit AS 'Yerel Kredi', ects AS 'AKTS' FROM courses WHERE user_id = ?", conn, params=(user_id,))
    df_e_exp = pd.read_sql_query('''
        SELECT c.code AS 'Ders', e.title AS 'Etkinlik', e.event_type AS 'Tür', e.event_date AS 'Tarih', e.weight AS 'Ağırlık (%)', 
               IFNULL(e.score, 'Girilmedi') AS 'Aldığı Not'
        FROM exams e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ? ORDER BY e.event_date ASC
    ''', conn, params=(user_id,))
    df_n_exp = pd.read_sql_query('''
        SELECT c.code AS 'Ders', n.topic AS 'Konu', n.content AS 'İçerik', n.created_at AS 'Tarih'
        FROM notes n JOIN courses c ON n.course_id = c.id WHERE n.user_id = ? ORDER BY n.created_at DESC
    ''', conn, params=(user_id,))
    
    html_code = generate_html_report(profile, df_c_exp, df_e_exp, df_n_exp)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📄 Rapor Belgesini İndir (.html / Baskıya Hazır)",
            data=html_code,
            file_name=f"IYTE_Akademik_Rapor_{date.today()}.html",
            mime="text/html"
        )
    with col_d2:
        st.info("💡 **PDF Olarak Kaydetme İpucu:** İndirdiğiniz dosyaya tıklayıp tarayıcıda açtıktan sonra `Ctrl + P` diyerek 'PDF Olarak Kaydet' seçeneğiyle %100 düzgün Türkçe karakterli PDF elde edebilirsiniz!")

# --- MODÜL 9: DERS & MÜFREDAT YÖNETİMİ ---
elif menu == "⚙️ Ders & Müfredat Yönetimi":
    st.markdown("<h1 class='custom-header'>Ders & Müfredat Yönetimi</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 İYTE Ders Havuzundan Seç", "➕ Özel / Seçmeli Ders Ekle", "🗑️ Kayıtlı Dersleri Yönet & Sil"])
    
    with tab1:
        st.subheader("İYTE Makine Mühendisliği Ders Havuzu")
        st.caption("İstediğin yarıyıllardan almak istediğin dersleri tikleyerek tek tek ekleyebilirsin.")
        
        sem_filter = st.multiselect("Yarıyıla Göre Filtrele (Tümü Görmek İçin Boş Bırakın)", 
                                   [1, 2, 3, 4, 5, 6, 7, 8], 
                                   default=[5])
        
        filtered_courses = [c for c in IYTE_ALL_COURSES if c["sem"] in sem_filter] if sem_filter else IYTE_ALL_COURSES
        
        selected_to_add = []
        for item in filtered_courses:
            chk = st.checkbox(f"**{item['code']}** - {item['name']} *({item['credit']} Kredi / {item['ects']} AKTS)*", key=f"chk_{item['code']}")
            if chk:
                selected_to_add.append(item)
                
        if st.button("✅ Seçilen Dersleri Sayfama Ekle"):
            if selected_to_add:
                count = 0
                cursor = conn.cursor()
                for c in selected_to_add:
                    check_db = pd.read_sql_query("SELECT id FROM courses WHERE code = ? AND user_id = ?", conn, params=(c['code'], user_id))
                    if check_db.empty:
                        cursor.execute("INSERT INTO courses (user_id, code, name, credit, ects, semester) VALUES (?, ?, ?, ?, ?, ?)",
                                       (user_id, c['code'], c['name'], c['credit'], c['ects'], c['sem']))
                        count += 1
                conn.commit()
                st.toast(f"🎉 {count} yeni ders sayfanıza eklendi!", icon="✅")
                time.sleep(0.8)
                st.rerun()
            else:
                st.warning("Lütfen eklemek istediğiniz dersleri işaretleyin.")

    with tab2:
        st.subheader("Manuel / Seçmeli Ders Ekleme")
        m_code = st.text_input("Ders Kodu", placeholder="Örn: ME 451")
        m_name = st.text_input("Ders Adı", placeholder="Örn: Isıl Sistemler Tasarımı")
        m_credit = st.number_input("Yerel Kredi", min_value=0, max_value=10, value=3)
        m_ects = st.number_input("AKTS Değeri", min_value=1, max_value=30, value=5)
        
        if st.button("Seçmeli Dersi Kaydet"):
            if m_code and m_name:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO courses (user_id, code, name, credit, ects, semester) VALUES (?, ?, ?, ?, ?, 5)",
                               (user_id, m_code, m_name, m_credit, m_ects))
                conn.commit()
                st.toast(f"✅ {m_code} seçmeli dersi eklendi!", icon="🎉")
                time.sleep(0.8)
                st.rerun()

    with tab3:
        st.subheader("Kayıtlı Dersleri Sil & Yönet")
        df_c = pd.read_sql_query("SELECT id, code AS 'Kodu', name AS 'Adı', credit AS 'Kredi', ects AS 'AKTS' FROM courses WHERE user_id = ?", conn, params=(user_id,))
        
        if not df_c.empty:
            for _, r in df_c.iterrows():
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"📘 **{r['Kodu']}** - {r['Adı']} ({r['Kredi']} Kredi / {r['AKTS']} AKTS)")
                if col_b.button("🗑️ Dersi Sil", key=f"del_course_{r['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM courses WHERE id = ? AND user_id = ?", (r['id'], user_id))
                    conn.commit()
                    st.toast(f"🗑️ {r['Kodu']} dersi başarıyla silindi!", icon="🗑️")
                    time.sleep(0.8)
                    st.rerun()
        else:
            st.info("Kayıtlı ders bulunmuyor.")