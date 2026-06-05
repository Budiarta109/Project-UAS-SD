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
