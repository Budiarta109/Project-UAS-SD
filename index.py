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