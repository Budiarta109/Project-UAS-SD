import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from pyvis.network import Network
import streamlit.components.v1 as components
import requests
import os

# --- 1. CONFIG HALAMAN FRONTEND ---
st.set_page_config(page_title="Enterprise AI-GraphDB Kost", layout="wide", page_icon="🏢")

# --- 2. BACKEND API & MACHINE LEARNING LAYER (FastAPI Simulative Layer) ---
# Di lingkungan produksi, bagian ini dipisahkan ke repositori/server sendiri (misal: Docker/Render)
class BackendAPIEngine:
    def __init__(self):
        # Simulasi Database Multi-User & Graph
        if 'db_users' not in st.session_state:
            st.session_state.db_users = {"admin": "admin123", "user1": "pass123"}
        if 'db_kosts' not in st.session_state:
            # Data awal berskala besar untuk kebutuhan Machine Learning
            st.session_state.db_kosts = pd.DataFrame([
                {"id": "Kost_01", "nama": "Kost Orange", "harga": 800000, "fasilitas": "Wifi", "lat": -8.65, "lon": 115.21},
                {"id": "Kost_02", "nama": "Kost Green VIP", "harga": 1500000, "fasilitas": "AC & Wifi", "lat": -8.67, "lon": 115.22},
                {"id": "Kost_03", "nama": "Kost Lavender", "harga": 950000, "fasilitas": "AC & Wifi", "lat": -8.64, "lon": 115.20},
                {"id": "Kost_04", "nama": "Kost Berkah", "harga": 700000, "fasilitas": "AC", "lat": -8.66, "lon": 115.19},
                {"id": "Kost_05", "nama": "Kost Sunset View", "harga": 2200000, "fasilitas": "AC & Wifi", "lat": -8.68, "lon": 115.23},
                {"id": "Kost_06", "nama": "Kost Melati", "harga": 600000, "fasilitas": "Wifi", "lat": -8.63, "lon": 115.18}
            ])

    def login_user(self, username, password):
        """API Endpoint: Autentikasi Multi-User"""
        users = st.session_state.db_users
        if username in users and users[username] == password:
            return {"status": "success", "token": f"mock-jwt-token-for-{username}", "role": "authenticated"}
        return {"status": "error", "message": "Kredensial salah"}

    def register_user(self, username, password):
        """API Endpoint: Registrasi User Baru"""
        if username in st.session_state.db_users:
            return {"status": "error", "message": "Username sudah terdaftar"}
        st.session_state.db_users[username] = password
        return {"status": "success"}

    def get_kost_data(self):
        """API Endpoint: Ambil Data Real-time"""
        return st.session_state.db_kosts

    def add_kost_node(self, item):
        """API Endpoint: POST New Node Data"""
        df = st.session_state.db_kosts
        if item["id"] in df["id"].values:
            return {"status": "error", "message": "ID Node sudah ada"}
        st.session_state.db_kosts = pd.concat([df, pd.DataFrame([item])], ignore_index=True)
        return {"status": "success"}

    def run_ml_clustering(self):
        """API Endpoint: ML Engine (K-Means Clustering untuk segmentasi cerdas AI)"""
        df = st.session_state.db_kosts.copy()
        if len(df) >= 3:
            # Ekstrak fitur numerik untuk clustering: Harga dan koordinat lokasi proxy
            features = df[['harga', 'lat', 'lon']].values
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df['cluster_ai'] = kmeans.fit_predict(features)
        else:
            df['cluster_ai'] = 0
        return df
        
        # Inisialisasi API Engine ke runtime memory
api = BackendAPIEngine()

# --- 3. SESSION STATE FRONTEND MANAGEMENT ---
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- 4. INTERFACE 1: MULTI-USER AUTHENTICATION (GATEWAY) ---
if st.session_state.auth_token is None:
    st.markdown("# 🔐 Gateway Masuk Sistem")
    st.markdown("### Smart DSS Kost - Enterprise Multi-User Platform")
    
    tab_login, tab_reg = st.tabs(["🔑 Login Pengguna", "📝 Daftar Akun Baru"])
    
    with tab_login:
        log_user = st.text_input("Username", key="log_u")
        log_pass = st.text_input("Password", type="password", key="log_p")
        if st.button("Masuk Ke Sistem", use_container_width=True):
            res = api.login_user(log_user, log_pass)
            if res["status"] == "success":
                st.session_state.auth_token = res["token"]
                st.session_state.current_user = log_user
                st.toast(f"Selamat datang kembali, {log_user}! 👋")
                st.rerun()
            else:
                st.error(res["message"])
                
    with tab_reg:
        reg_user = st.text_input("Username Baru", key="reg_u")
        reg_pass = st.text_input("Password Baru", type="password", key="reg_p")
        if st.button("Buat Akun", use_container_width=True):
            res = api.register_user(reg_user, reg_pass)
            if res["status"] == "success":
                st.success("Akun berhasil dibuat! Silakan login di tab sebelah.")
            else:
                st.error(res["message"])
    st.stop()

# --- 5. HALAMAN UTAMA APLIKASI (JIKA SUDAH AUTHENTICATED) ---
# Top Bar & Logout
col_title, col_user = st.columns([5, 1])
with col_title:
    st.markdown(f"# 🏠 AI Graph-DSS Ecosystem")
    st.markdown(f"##### *Sistem Enterprise Berbasis API, Real-time Graph Visualizer, & Machine Learning Clustering*")
with col_user:
    st.write("")
    st.markdown(f"👤 **{st.session_state.current_user.upper()}**")
    if st.button("🚪 Keluar", use_container_width=True):
        st.session_state.auth_token = None
        st.session_state.current_user = None
        st.rerun()

st.markdown("---")

# --- 6. SIDEBAR CONTROLLER (INTEGRASI API POST) ---
with st.sidebar:
    st.markdown("## ⚙️ REST API Controller")
    
    with st.expander("🎯 Parameter Target Pencarian", expanded=True):
        user_budget = st.number_input("Budget Maksimal (Rp)", value=1500000, step=50000)
        user_fasilitas = st.selectbox("Fasilitas Wajib", ["Wifi", "AC", "AC & Wifi"])
        prio_harga = st.slider("Bobot Prioritas Harga", 0.0, 1.0, 0.5)
        prio_fas = st.slider("Bobot Prioritas Fasilitas", 0.0, 1.0, 0.5)
    
    with st.expander("➕ API POST: Tambah Node Kost (Multi-user)", expanded=False):
        new_id = st.text_input("ID Kamar (Unique)")
        new_nama = st.text_input("Nama Properti")
        new_harga = st.number_input("Harga Sewa", min_value=100000, value=900000, step=50000)
        new_fas = st.selectbox("Fasilitas Kamar", ["Wifi", "AC", "AC & Wifi"])
        
        if st.button("Kirim Data via API", use_container_width=True):
            if new_id and new_nama:
                # Simulasi koordinat acak di sekitar Bali untuk peta spasial ML
                payload = {
                    "id": new_id, "nama": new_nama, "harga": new_harga, "fasilitas": new_fas,
                    "lat": -8.65 + np.random.uniform(-0.03, 0.03), "lon": 115.21 + np.random.uniform(-0.03, 0.03)
                }
                res = api.add_kost_node(payload)
                if res["status"] == "success":
                    st.success(f"💾 Terkirim! Data synced ke server.")
                    st.rerun()
                else:
                    st.error(res["message"])
                    
# --- 7. JALANKAN MACHINE LEARNING ENGINE ---
# Mendapatkan data terklasterisasi secara real-time dari database
ml_df = api.run_ml_clustering()

# --- 8. REAL-TIME INTERACTIVE VISUALIZATION LAYER (PyVis Engine) ---
st.markdown("### 🖼️ Real-time Interactive Graph Database Visualizer")
st.caption("💡 Petunjuk: Node graf di bawah ini interaktif! Anda dapat mengklik, menggeser, zoom-in/out, dan mengurai struktur relasi secara langsung.")

# Inisialisasi Graf Interaktif PyVis
kost_net = Network(height="400px", width="100%", bgcolor="#1e293b", font_color="#ffffff", directed=True)

# Generate Skema Warna Berdasarkan Klaster Machine Learning
# Cluster 0 = Ekonomis, Cluster 1 = Premium, Cluster 2 = Luxury
cluster_colors = {0: "#10b981", 1: "#3b82f6", 2: "#a855f7"}

# Tambahkan Node Akar
kost_net.add_node("Root", label="Pencarian Utama", color="#ef4444", size=25, shape="hexagon")

# Tambahkan Sub-Kriteria Kategori Cluster AI hasil Machine Learning
kost_net.add_node("C0", label="AI Cluster: Ekonomis", color="#10b981", size=20, shape="ellipse")
kost_net.add_node("C1", label="AI Cluster: Menengah", color="#3b82f6", size=20, shape="ellipse")
kost_net.add_node("C2", label="AI Cluster: Premium", color="#a855f7", size=20, shape="ellipse")

kost_net.add_edge("Root", "C0", title="Klasifikasi AI")
kost_net.add_edge("Root", "C1", title="Klasifikasi AI")
kost_net.add_edge("Root", "C2", title="Klasifikasi AI")

# Bangun Node Data Kost Secara Dinamis dari Database Real-time
for _, row in ml_df.iterrows():
    cluster_id = row['cluster_ai']
    color_node = cluster_colors.get(cluster_id, "#64748b")
    
    # Keterangan pop-up detail saat kursor melayang (hovering) di atas node
    hover_info = f"Nama: {row['nama']}<br>Harga: Rp {row['harga']:,}<br>Fasilitas: {row['fasilitas']}"
    
    kost_net.add_node(
        row['id'], 
        label=f"{row['nama']}\n(Rp {row['harga']//1000}k)", 
        title=hover_info, 
        color=color_node, 
        size=15
    )
    # Hubungkan node kamar kos ke cluster kriteria yang diciptakan oleh Machine Learning
    parent_cluster = f"C{cluster_id}"
    kost_net.add_edge(parent_cluster, row['id'], title="TERMASUK")

# Simpan graf ke HTML internal agar bisa dirender secara dinamis oleh Streamlit Components
try:
    kost_net.save_graph("interactive_graph.html")
    HtmlFile = open("interactive_graph.html", 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=420)
except Exception as e:
    st.error("Gagal memuat visualisasi graf interaktif.")

# --- 9. RANGKING & DECSION ENGINE ---
st.markdown("---")
st.markdown("### 🔮 Rekomendasi Pintar Hasil Analisis Server")

# Filter data berdasarkan kriteria input user (Screening)
filtered_df = ml_df[ml_df['harga'] <= user_budget].copy()

if not filtered_df.empty:
    # Proses AI Scoring (Simple Additive Weighting)
    min_harga = filtered_df['harga'].min()
    
    scores = []
    for _, r in filtered_df.iterrows():
        # Hitung skor harga (cost metric)
        s_harga = min_harga / r['harga']
        # Hitung skor fasilitas (benefit metric)
        s_fas = 1.0 if r['fasilitas'] == user_fasilitas else (0.6 if user_fasilitas in r['fasilitas'] else 0.1)
        
        # Kalkulasi bobot akhir
        total_score = (s_harga * prio_harga) + (s_fas * prio_fas)
        scores.append(round(total_score * 100, 2))
        
    filtered_df['ai_match_score'] = scores
    filtered_df = filtered_df.sort_values(by="ai_match_score", ascending=False)
    
    # Tampilan Output Terbagi Menjadi 2 Kolom (Hasil Skor & Cluster Data)
    col_rec, col_ml_info = st.columns([3, 2])
    
    with col_rec:
        st.markdown("##### 💡 Peringkat Alternatif Terbaik")
        for idx, row in filtered_df.reset_index().iterrows():
            badge_color = "#10b981" if idx == 0 else "#3b82f6"
            st.markdown(
                f"""
                <div style="background-color:#1e293b; padding:15px; border-left:6px solid {badge_color}; border-radius:8px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0; color:#f8fafc;">{row['nama']} (ID: {row['id']})</h4>
                        <span style="background-color:{badge_color}; color:white; padding:2px 8px; border-radius:10px; font-size:12px;">Peringkat {idx+1}</span>
                    </div>
                    <p style="margin:5px 0; font-size:14px; color:#94a3b8;">
                        Harga: <b>Rp {row['harga']:,}/bulan</b> | Fasilitas: <b>{row['fasilitas']}</b>
                    </p>
                    <div style="color:#f59e0b; font-size:13px; font-weight:bold;">
                        🤖 AI Match Score: {row['ai_match_score']}% | Kelompok AI Cluster: {row['cluster_ai']}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            
    with col_ml_info:
        st.markdown("##### 🤖 Statistik Segmentasi Machine Learning")
        st.dataframe(
            ml_df[['id', 'nama', 'harga', 'cluster_ai']].rename(
                columns={"cluster_ai": "Label Cluster AI (K-Means)"}
            ),
            use_container_width=True,
            hide_index=True
        )
        st.caption("K-Means mengelompokkan data kos secara otomatis ke dalam 3 zona ekonomi berdasarkan dinamika harga pasar terupdate.")
else:
    st.warning("Tidak ditemukan alternatif properti yang memenuhi kriteria budget Anda.")
