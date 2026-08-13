import streamlit as st
import pandas as pd
from datetime import datetime, date
import database as db

# -----------------------------------------------------------------------------
# 1. SAYFA KONFİGÜRASYONU & MOBİL UYUMLU PREMIUM CSS (GLASSMORPHISM)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="İYTE Makine | Akademik Yönetim Platformu",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    /* Global Temel Stiller */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Mobil Uyumlu Metrik Kartları */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        margin-bottom: 10px;
    }
    
    /* Yan Menü Profil Kartı */
    .profile-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(49, 46, 129, 0.3);
    }
    
    /* Gradient Başlıklar */
    .custom-header {
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
    }
    
    /* Mobil Ekran İyileştirmeleri (Responsive CSS) */
    @media (max-width: 768px) {
        .stApp { padding: 5px; }
        div[data-testid="stMetric"] { padding: 12px; }
        .custom-header { font-size: 24px !important; }
        .stButton>button { width: 100%; border-radius: 10px; }
    }
    
    /* Özel Durum Kartları */
    .trend-card-up {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Veritabanını Başlat
db.init_db()
conn = db.get_connection()

# -----------------------------------------------------------------------------
# 2. İYTE MAKİNE DERS HAVUZU
# -----------------------------------------------------------------------------
IYTE_ALL_COURSES = [
    # 1. Yarıyıl
    {"code": "CHEM121", "name": "GENEL KİMYA I", "credit": 3, "ects": 5, "sem": 1},
    {"code": "CHEM141", "name": "GENEL KİMYA LABORATUVARI I", "credit": 1, "ects": 2, "sem": 1},
    {"code": "ENG101", "name": "İNGİLİZCE OKUME VE YAZMA BECERİLERİ I", "credit": 3, "ects": 3, "sem": 1},
    {"code": "MATH101", "name": "ÖN MATEMATİK", "credit": 0, "ects": 2, "sem": 1},
    {"code": "MATH141", "name": "TEMEL ANALİZ I", "credit": 4, "ects": 5, "sem": 1},
    {"code": "ME101", "name": "MAKİNA MÜHENDİSLİĞİNE GİRİŞ", "credit": 2, "ects": 5, "sem": 1},
    {"code": "ME113", "name": "BİLGİSAYAR DESTEKLİ TEKNİK RESİM I", "credit": 3, "ects": 3, "sem": 1},
    {"code": "PHYS101", "name": "GENEL FİZİK I", "credit": 4, "ects": 5, "sem": 1},
    {"code": "PHYS111", "name": "GENEL FİZİK LAB. I", "credit": 1, "ects": 2, "sem": 1},
    {"code": "OHS 101", "name": "İş Sağlığı ve Güvenliği I", "credit": 1, "ects": 1, "sem": 1},
    
    # 2. Yarıyıl
    {"code": "CS106", "name": "TEMEL BİLGİSAYAR BİLİMİ VE PROGRAMLAMASI", "credit": 3, "ects": 5, "sem": 2},
    {"code": "ENG102", "name": "İNGİLİZCE OKUME VE YAZMA BECERİLERİ II", "credit": 3, "ects": 3, "sem": 2},
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

# Profil Verisi (Kişiselleştirilmiş İsim Yerine Genel Yapı)
cursor = conn.cursor()
cursor.execute("SELECT name, department, grade, current_gpa FROM profile WHERE id = 1")
prof_row = cursor.fetchone()
if not prof_row or prof_row[0] == "Furkan Aktaş":
    cursor.execute("UPDATE profile SET name='İYTE Öğrenci Paneli', department='Makine Mühendisliği', grade='Lisans' WHERE id=1")
    conn.commit()
    profile = {"name": "İYTE Öğrenci Paneli", "department": "Makine Mühendisliği", "grade": "Lisans", "current_gpa": 3.00}
else:
    profile = {"name": prof_row[0], "department": prof_row[1], "grade": prof_row[2], "current_gpa": prof_row[3]}

# -----------------------------------------------------------------------------
# 3. YAN MENÜ & PROFİL YAPILANDIRMASI
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="profile-card">
        <h3 style="margin:0; color:#f8fafc; font-size:18px;">🎓 {profile['name']}</h3>
        <p style="margin:4px 0 0 0; color:#a5b4fc; font-size:12px;">İYTE - {profile['department']}</p>
        <span style="background:#4f46e5; color:white; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold;">{profile['grade']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👤 Kullanıcı Profil Bilgileri"):
        u_name = st.text_input("Ad Soyad / Kullanıcı Adı", value=profile['name'])
        u_dept = st.text_input("Bölüm", value=profile['department'])
        u_grade = st.selectbox("Sınıf", ["1. Sınıf", "2. Sınıf", "3. Sınıf", "4. Sınıf", "Lisans"], index=2)
        u_gpa = st.number_input("Mevcut AGNO", min_value=0.0, max_value=4.0, value=profile['current_gpa'], step=0.01)
        if st.button("Profil Bilgilerini Kaydet"):
            cursor.execute("UPDATE profile SET name=?, department=?, grade=?, current_gpa=? WHERE id=1", (u_name, u_dept, u_grade, u_gpa))
            conn.commit()
            st.rerun()

    st.divider()
    menu = st.radio("Navigasyon", ["📈 Dönem & Sınav Not Takibi", "📊 Aylık Başarı Trendi", "📅 Sınav Takvimi & Geri Sayım", "📝 Ders Notları", "⚙️ Ders & Müfredat Yönetimi"])

# -----------------------------------------------------------------------------
# 4. MODÜLLER
# -----------------------------------------------------------------------------

# --- MODÜL 1: DÖNEM & SINAV NOT TAKİBİ ---
if menu == "📈 Dönem & Sınav Not Takibi":
    st.markdown("<h1 class='custom-header'>Akademik Performans & Not Takibi</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Genel AGNO", f"{profile['current_gpa']:.2f} / 4.00")
    
    tot_credits = pd.read_sql_query("SELECT SUM(credit) FROM courses", conn).iloc[0,0] or 0
    tot_ects = pd.read_sql_query("SELECT SUM(ects) FROM courses", conn).iloc[0,0] or 0
    c2.metric("Aktif Dönem Kredisi", f"{tot_credits} Kredi")
    c3.metric("Aktif Dönem AKTS", f"{tot_ects} AKTS")

    st.divider()
    courses_df = pd.read_sql_query("SELECT id, code, name, credit, ects FROM courses", conn)
    
    if not courses_df.empty:
        for _, c_row in courses_df.iterrows():
            with st.expander(f"📘 **{c_row['code']} - {c_row['name']}** ({c_row['credit']} Kredi / {c_row['ects']} AKTS)", expanded=True):
                exams_df = pd.read_sql_query(
                    "SELECT id, title, event_type, weight, score FROM exams WHERE course_id = ?", 
                    conn, params=(c_row['id'],)
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
                                cursor.execute("UPDATE exams SET score = ? WHERE id = ?", (new_s, ex['id']))
                                conn.commit()
                                st.success("Kaydedildi!")
                                st.rerun()
                                
                            if cd.button("🗑️ Sil", key=f"btn_del_ex_{ex['id']}"):
                                cursor.execute("DELETE FROM exams WHERE id = ?", (ex['id'],))
                                conn.commit()
                                st.warning("Silindi!")
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

# --- MODÜL 2: AYLIK BAŞARI TRENDİ ---
elif menu == "📊 Aylık Başarı Trendi":
    st.markdown("<h1 class='custom-header'>Aylık Başarı Eğrisi & Trend Analizi</h1>", unsafe_allow_html=True)
    
    query_monthly = '''
        SELECT strftime('%Y-%m', event_date) AS Ay, AVG(score) AS Ortalama, COUNT(score) AS SinavSayisi
        FROM exams
        WHERE score IS NOT NULL
        GROUP BY Ay
        ORDER BY Ay ASC
    '''
    df_trend = pd.read_sql_query(query_monthly, conn)
    
    if not df_trend.empty and len(df_trend) >= 1:
        st.subheader("📈 Aylık Not Gelişim Grafiği")
        st.line_chart(df_trend.set_index('Ay')['Ortalama'], use_container_width=True)
        
        if len(df_trend) >= 2:
            last_month = df_trend.iloc[-1]['Ortalama']
            prev_month = df_trend.iloc[-2]['Ortalama']
            diff = last_month - prev_month
            pct_change = (diff / prev_month) * 100 if prev_month > 0 else 0
            
            if diff >= 0:
                st.markdown(f"""
                <div class="trend-card-up">
                    <h4>🚀 Harika İlerleme!</h4>
                    <p>Bu ayki ortalamanız (<b>{last_month:.2f}</b>), geçen aya (<b>{prev_month:.2f}</b>) göre <b>%{pct_change:.1f} daha yüksek!</b> Performansınız yükselişte.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ Bu ayki ortalamanız geçen aya göre %{abs(pct_change):.1f} bir miktar düşüş gösterdi.")
        else:
            st.info(f"Geçerli ay ortalamanız: **{df_trend.iloc[0]['Ortalama']:.2f}**.")
    else:
        st.info("Aylık başarı eğrisi için sınav tarihlerini ve aldığınız notları girmelisiniz.")

# --- MODÜL 3: SINAV TAKVİMİ & GERİ SAYIM ---
elif menu == "📅 Sınav Takvimi & Geri Sayım":
    st.markdown("<h1 class='custom-header'>Sınav Takvimi & Geri Sayım</h1>", unsafe_allow_html=True)
    
    with st.expander("➕ Yeni Sınav / Ödev Ekle"):
        courses = pd.read_sql_query("SELECT id, code FROM courses", conn)
        if not courses.empty:
            c_dict = dict(zip(courses['code'], courses['id']))
            sel_c = st.selectbox("Ders", list(c_dict.keys()))
            title = st.text_input("Etkinlik Adı", placeholder="Vize 1, Quiz 2 vb.")
            e_type = st.selectbox("Tür", ["Vize", "Final", "Quiz", "Ödev / Rapor"])
            e_date = st.date_input("Tarih", min_value=date.today())
            weight = st.slider("Ağırlık Yüzdesi (%)", 1, 100, 30)
            
            if st.button("Takvime Ekle"):
                cursor.execute("INSERT INTO exams (course_id, title, event_type, event_date, weight) VALUES (?, ?, ?, ?, ?)",
                               (c_dict[sel_c], title, e_type, e_date, weight))
                conn.commit()
                st.success("Sınav eklendi!")
                st.rerun()

    df_e = pd.read_sql_query('''
        SELECT e.id, c.code AS Ders, e.title AS Etkinlik, e.event_type AS Tür, e.event_date AS Tarih, e.weight AS Agirlik, e.score AS Notu
        FROM exams e JOIN courses c ON e.course_id = c.id ORDER BY e.event_date ASC
    ''', conn)
    
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
                    cursor.execute("DELETE FROM exams WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.rerun()

# --- MODÜL 4: DERS NOTLARI ---
elif menu == "📝 Ders Notları":
    st.markdown("<h1 class='custom-header'>Ders Notları & Formül Defteri</h1>", unsafe_allow_html=True)
    courses = pd.read_sql_query("SELECT id, code, name FROM courses", conn)
    
    if not courses.empty:
        c_dict = dict(zip(courses['code'] + " - " + courses['name'], courses['id']))
        sel_str = st.selectbox("Ders Seçin", list(c_dict.keys()))
        sel_id = c_dict[sel_str]
        
        with st.expander("📝 Yeni Not Ekle", expanded=True):
            topic = st.text_input("Konu / Formül Başlığı")
            tag = st.selectbox("Etiket", ["Genel Not", "Vize Konusu", "Final Konusu", "Formül / Denklemler"])
            content = st.text_area("İçerik", height=120)
            
            if st.button("Notu Kaydet"):
                cursor.execute("INSERT INTO notes (course_id, topic, content, tag) VALUES (?, ?, ?, ?)", (sel_id, topic, content, tag))
                conn.commit()
                st.success("Not eklendi!")
                st.rerun()

        st.subheader("📌 Geçmiş Notlar")
        notes_df = pd.read_sql_query("SELECT id, topic, content, tag, created_at FROM notes WHERE course_id = ? ORDER BY created_at DESC", conn, params=(sel_id,))
        for _, n in notes_df.iterrows():
            with st.expander(f"📌 [{n['tag']}] {n['topic']} ({n['created_at']})"):
                st.markdown(n['content'])
                if st.button("🗑️ Notu Sil", key=f"del_note_{n['id']}"):
                    cursor.execute("DELETE FROM notes WHERE id = ?", (n['id'],))
                    conn.commit()
                    st.rerun()

# --- MODÜL 5: DERS & MÜFREDAT YÖNETİMİ ---
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
                for c in selected_to_add:
                    check_db = pd.read_sql_query("SELECT id FROM courses WHERE code = ?", conn, params=(c['code'],))
                    if check_db.empty:
                        cursor.execute("INSERT INTO courses (code, name, credit, ects, semester) VALUES (?, ?, ?, ?, ?)",
                                       (c['code'], c['name'], c['credit'], c['ects'], c['sem']))
                        count += 1
                conn.commit()
                st.success(f"{count} yeni ders eklendi!")
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
                cursor.execute("INSERT INTO courses (code, name, credit, ects, semester) VALUES (?, ?, ?, ?, 5)",
                               (m_code, m_name, m_credit, m_ects))
                conn.commit()
                st.success(f"{m_code} dersi eklendi!")
                st.rerun()

    with tab3:
        st.subheader("Kayıtlı Dersleri Sil & Yönet")
        df_c = pd.read_sql_query("SELECT id, code AS 'Kodu', name AS 'Adı', credit AS 'Kredi', ects AS 'AKTS' FROM courses", conn)
        
        if not df_c.empty:
            for _, r in df_c.iterrows():
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"📘 **{r['Kodu']}** - {r['Adı']} ({r['Kredi']} Kredi / {r['AKTS']} AKTS)")
                if col_b.button("🗑️ Dersi Sil", key=f"del_course_{r['id']}"):
                    cursor.execute("DELETE FROM courses WHERE id = ?", (r['id'],))
                    conn.commit()
                    st.warning(f"{r['Kodu']} silindi!")
                    st.rerun()
        else:
            st.info("Kayıtlı ders bulunmuyor.")