import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

st.set_page_config(page_title="Altınyaldız Statik AI", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.markdown("### 🔒 Altınyaldız Statik Hesap Motoruna Giriş")
        st.text_input("Şifre:", type="password", key="pwd")
        if st.session_state.pwd == "CFO2026":
            st.session_state["password_correct"] = True
            st.rerun()
        elif st.session_state.pwd != "":
            st.error("Hatalı şifre, lütfen tekrar deneyin.")
        return False
    return True

if check_password():
    st.title("🏗️ Otonom Modül, Kesit ve Maliyet Optimizasyonu")
    st.markdown("Algoritma en düşük ağırlığı bulur, 3D dijital ikizi çizer ve anlık proje bütçesini hesaplar.")

    # 1. BORU VE KONİK KÜTÜPHANESİ
    pipe_data = [
        {"Boru": "42.4x2.5", "D": 42.4, "t": 2.5, "Agirlik_kg_m": 2.46, "Konik": "42.4 Konik", "Civata": "M12", "Konik_kg": 0.13},
        {"Boru": "48.3x2.5", "D": 48.3, "t": 2.5, "Agirlik_kg_m": 2.82, "Konik": "48.3 Konik", "Civata": "M12", "Konik_kg": 0.18},
        {"Boru": "60.3x3.0", "D": 60.3, "t": 3.0, "Agirlik_kg_m": 4.24, "Konik": "60.3 Konik", "Civata": "M16", "Konik_kg": 0.31},
        {"Boru": "76.1x3.0", "D": 76.1, "t": 3.0, "Agirlik_kg_m": 5.41, "Konik": "76.1 Konik", "Civata": "M20", "Konik_kg": 0.53},
        {"Boru": "88.9x4.0", "D": 88.9, "t": 4.0, "Agirlik_kg_m": 8.37, "Konik": "88.9 Konik", "Civata": "M24", "Konik_kg": 0.75},
        {"Boru": "114.3x4.0", "D": 114.3, "t": 4.0, "Agirlik_kg_m": 10.88, "Konik": "114.3 Konik", "Civata": "M30", "Konik_kg": 1.88},
        {"Boru": "139.7x5.0", "D": 139.7, "t": 5.0, "Agirlik_kg_m": 16.60, "Konik": "139.7 Konik", "Civata": "M36", "Konik_kg": 2.95}
    ]
    df_pipes = pd.DataFrame(pipe_data)
    
    df_pipes["Alan_mm2"] = math.pi * (df_pipes["D"] - df_pipes["t"]) * df_pipes["t"]
    df_pipes["I_mm4"] = (math.pi * (df_pipes["D"]**4 - (df_pipes["D"] - 2*df_pipes["t"])**4)) / 64
    df_pipes["Akma_Kapasitesi_kN"] = (df_pipes["Alan_mm2"] * 235) / 1000

    # 2. GİRDİ PANELİ (STATİK VE FİNANS)
    st.sidebar.header("📐 Geometri & Yükler")
    span_L = st.sidebar.number_input("Açıklık/Boy (L) - metre", min_value=10.0, value=30.0, step=1.0)
    width_W = st.sidebar.number_input("Genişlik (W) - metre", min_value=10.0, value=20.0, step=1.0) # YENİ GİRDİ
    depth_d = st.sidebar.number_input("Sistem Derinliği (h) - metre", min_value=1.0, value=2.0, step=0.1)
    load_Q = st.sidebar.number_input("Toplam Yük - kN/m2", min_value=0.5, value=1.5, step=0.1)

    st.sidebar.markdown("---")
    st.sidebar.header("💰 Finansal Parametreler")
    price_steel = st.sidebar.number_input("Boru/Çelik ($/kg)", min_value=0.5, value=1.20, step=0.1)
    price_mulu = st.sidebar.number_input("Mulu ($/adet)", min_value=5.0, value=18.50, step=0.5)
    price_labor = st.sidebar.number_input("Otomasyon Kaynak ($/çubuk)", min_value=1.0, value=4.50, step=0.5)

    st.write("---")
    
    # 3. İTERASYON MOTORU
    best_modul = None
    min_weight_per_m2 = float('inf')
    best_pipe = None
    best_force = 0
    best_length = 0
    
    test_modules = [x / 10.0 for x in range(15, 36)] 
    
    for a in test_modules:
        max_moment = (load_Q * (span_L**2)) / 8 # Moment hesabı açıklığa (L) göre yapılır
        force_kN = max_moment / depth_d
        cubuk_boyu_mm = math.sqrt((a/2)**2 + (a/2)**2 + depth_d**2) * 1000
        
        secilen_boru = None
        for index, row in df_pipes.iterrows():
            N_cr = (math.pi**2 * 200000 * row["I_mm4"]) / (cubuk_boyu_mm**2) / 1000
            Guvenli_Kapasite = min(row["Akma_Kapasitesi_kN"], N_cr / 1.5)
            if Guvenli_Kapasite >= force_kN:
                secilen_boru = row
                break
                
        if secilen_boru is not None:
            boru_uzunluk_m2 = (4/a) + (4 * (cubuk_boyu_mm/1000) / (a**2))
            toplam_boru_kg = boru_uzunluk_m2 * secilen_boru["Agirlik_kg_m"]
            toplam_konik_kg = (4 / (a**2)) * secilen_boru["Konik_kg"] 
            toplam_agirlik_indeksi = toplam_boru_kg + toplam_konik_kg
            
            if toplam_agirlik_indeksi < min_weight_per_m2:
                min_weight_per_m2 = toplam_agirlik_indeksi
                best_modul = a
                best_pipe = secilen_boru
                best_force = force_kN
                best_length = cubuk_boyu_mm

    # 4. SONUÇ, METRAJ VE ÇİZİM
    if best_pipe is not None:
        
        # GERÇEK METRAJ HESABI (DİKDÖRTGEN ÇATI İÇİN GÜNCELLENDİ)
        Nx = max(1, int(span_L / best_modul)) # Boy yönündeki modül sayısı
        Ny = max(1, int(width_W / best_modul)) # En yönündeki modül sayısı
        
        bottom_nodes_count = (Nx + 1) * (Ny + 1)
        top_nodes_count = Nx * Ny
        total_mulu_count = bottom_nodes_count + top_nodes_count
        
        bottom_chords_count = Nx * (Ny + 1) + Ny * (Nx + 1)
        top_chords_count = max(0, (Nx - 1) * Ny) + max(0, (Ny - 1) * Nx)
        diagonal_chords_count = 4 * Nx * Ny
        total_chords_count = bottom_chords_count + top_chords_count + diagonal_chords_count
        
        horizontal_length_m = (bottom_chords_count + top_chords_count) * best_modul
        diagonal_length_m = diagonal_chords_count * (best_length / 1000.0)
        total_pipe_length_m = horizontal_length_m + diagonal_length_m
        
        # Uzay Kafes Çelik Tonajı
        total_pipe_weight_kg = total_pipe_length_m * best_pipe["Agirlik_kg_m"]
        total_conic_weight_kg = (total_chords_count * 2) * best_pipe["Konik_kg"]
        total_steel_weight_kg = total_pipe_weight_kg + total_conic_weight_kg
        
        # Aşık (Purlin) Hesabı
        purlin_length_m = top_nodes_count * best_modul # Basitleştirilmiş aşık metrajı (Y ekseni boyunca)
        purlin_weight_kg_m = 5.0 # Yaklaşık 5 kg/m'lik bir kutu profil varsayımı
        total_purlin_weight_kg = purlin_length_m * purlin_weight_kg_m
        
        # MALİYET HESABI
        cost_steel = total_steel_weight_kg * price_steel
        cost_purlin = total_purlin_weight_kg * price_steel # Aşıklar da çelik fiyatından hesaplanıyor
        cost_mulu = total_mulu_count * price_mulu
        cost_labor = total_chords_count * price_labor
        total_project_cost = cost_steel + cost_purlin + cost_mulu + cost_labor
        
        col_grafik, col_hesap = st.columns([1.5, 1])
        
        with col_hesap:
            st.subheader("🏆 Optimize Edilmiş Sistem")
            st.success(f"En Ekonomik Modül Boyu: **{best_modul} metre**")
            
            c1, c2 = st.columns(2)
            c1.metric("Optimum Boru", best_pipe['Boru'])
            c2.metric("Uygun Cıvata", best_pipe['Civata'])
            
            # CANLI MALİYET PANELİ
            st.markdown("### 📊 Proje Metrajı ve Maliyet")
            metraj_df = pd.DataFrame({
                "Kalem": ["Uzay Kafes Çeliği", "Aşık Çeliği (Purlins)", "Mulu (Küre)", "Kaynak/İmalat"],
                "Miktar": [f"{total_steel_weight_kg/1000:.1f} Ton", f"{total_purlin_weight_kg/1000:.1f} Ton", f"{total_mulu_count} Adet", f"{total_chords_count} Adet"],
                "Tutar": [f"${cost_steel:,.0f}", f"${cost_purlin:,.0f}", f"${cost_mulu:,.0f}", f"${cost_labor:,.0f}"]
            })
            st.table(metraj_df.set_index("Kalem"))
            
            st.info(f"💰 **Toplam Tahmini Üretim Maliyeti: ${total_project_cost:,.0f}**")

        with col_grafik:
            st.subheader(f"🧊 Dijital İkiz ({span_L}m x {width_W}m)")
            
            node_x, node_y, node_z = [], [], []
            bottom_nodes, top_nodes = {}, {}
            
            # Alt Noktalar
            for i in range(Nx + 1):
                for j in range(Ny + 1):
                    bottom_nodes[(i, j)] = len(node_x)
                    node_x.append(i * best_modul)
                    node_y.append(j * best_modul)
                    node_z.append(0)
                    
            # Üst Noktalar
            for i in range(Nx):
                for j in range(Ny):
                    top_nodes[(i, j)] = len(node_x)
                    node_x.append(i * best_modul + best_modul/2)
                    node_y.append(j * best_modul + best_modul/2)
                    node_z.append(depth_d)
                    
            line_x, line_y, line_z = [], [], []
            purlin_x, purlin_y, purlin_z = [], [], [] # Aşıklar için yeni liste
            
            def add_line(n1, n2, is_purlin=False):
                if is_purlin:
                    purlin_x.extend([node_x[n1], node_x[n2], None])
                    purlin_y.extend([node_y[n1], node_y[n2], None])
                    purlin_z.extend([node_z[n1], node_z[n2], None])
                else:
                    line_x.extend([node_x[n1], node_x[n2], None])
                    line_y.extend([node_y[n1], node_y[n2], None])
                    line_z.extend([node_z[n1], node_z[n2], None])
                
            for i in range(Nx + 1):
                for j in range(Ny + 1):
                    if i < Nx: add_line(bottom_nodes[(i, j)], bottom_nodes[(i+1, j)])
                    if j < Ny: add_line(bottom_nodes[(i, j)], bottom_nodes[(i, j+1)])
            for i in range(Nx):
                for j in range(Ny):
                    if i < Nx - 1: add_line(top_nodes[(i, j)], top_nodes[(i+1, j)])
                    if j < Ny - 1: add_line(top_nodes[(i, j)], top_nodes[(i, j+1)])
                    # Y ekseni boyunca AŞIK (Purlin) Çizimi (Sadece üst düğümlerden geçer)
                    if j < Ny - 1: add_line(top_nodes[(i, j)], top_nodes[(i, j+1)], is_purlin=True)
                    
            for i in range(Nx):
                for j in range(Ny):
                    tn = top_nodes[(i, j)]
                    add_line(tn, bottom_nodes[(i, j)])
                    add_line(tn, bottom_nodes[(i+1, j)])
                    add_line(tn, bottom_nodes[(i, j+1)])
                    add_line(tn, bottom_nodes[(i+1, j+1)])
            
            fig = go.Figure()
            # Uzay Kafes Boruları (Mavi)
            fig.add_trace(go.Scatter3d(
                x=line_x, y=line_y, z=line_z,
                mode='lines', line=dict(color='#1f77b4', width=2), name='Boru'
            ))
            # Aşıklar - Purlins (Yeşil)
            fig.add_trace(go.Scatter3d(
                x=purlin_x, y=purlin_y, z=purlin_z,
                mode='lines', line=dict(color='#2ca02c', width=4), name='Aşık'
            ))
            # Mulular (Kırmızı)
            fig.add_trace(go.Scatter3d(
                x=node_x, y=node_y, z=node_z,
                mode='markers', marker=dict(size=3, color='#d62728'), name='Mulu'
            ))
            fig.update_layout(
                scene=dict(aspectmode='data', xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), 
                margin=dict(l=0, r=0, b=0, t=0), height=500, showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Girdiğiniz değerler için kütüphanede uygun çözüm bulunamadı.")
