import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

st.set_page_config(page_title="Altınyaldız AI Statik", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.markdown("### 🔒 Altınyaldız Otonom Hesap Motoruna Giriş")
        st.text_input("Şifre:", type="password", key="pwd")
        if st.session_state.pwd == "CFO2026":
            st.session_state["password_correct"] = True
            st.rerun()
        elif st.session_state.pwd != "":
            st.error("Hatalı şifre, lütfen tekrar deneyin.")
        return False
    return True

if check_password():
    st.title("🏗️ Altınyaldız Uluslararası Uzay Sistem A.Ş.")
    st.markdown("### Otonom Statik, Zonal Maliyet ve İş Emri Motoru")
    st.markdown("Algoritma üretim hızını düşürmeden çelik tonajını minimize etmek için çatıyı **3 Farklı Gerilme Bölgesine (Zonal)** ayırır.")

    # 1. BORU KÜTÜPHANESİ
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

    # 2. GİRDİ PANELİ
    st.sidebar.header("📐 Geometri & Yükler")
    cati_formu = st.sidebar.selectbox("Çatı Formu", ["Düz / Beşik", "Tonoz", "Kubbe"])
    span_L = st.sidebar.number_input("Açıklık (X Eksen) - m", min_value=10.0, value=30.0, step=1.0)
    width_W = st.sidebar.number_input("Genişlik (Y Eksen) - m", min_value=10.0, value=30.0, step=1.0)
    depth_d = st.sidebar.number_input("Sistem Derinliği (h) - m", min_value=1.0, value=2.0, step=0.1)
    
    if cati_formu == "Düz / Beşik":
        roof_slope = st.sidebar.number_input("Çatı Eğimi (%)", min_value=0.0, value=5.0, step=1.0)
        arch_rise = 0.0
    else:
        arch_rise = st.sidebar.number_input(f"{cati_formu} Yüksekliği - m", min_value=1.0, value=5.0, step=0.5)
        roof_slope = 0.0
        
    load_Q = st.sidebar.number_input("Toplam Yük - kN/m2", min_value=0.5, value=1.5, step=0.1)

    st.sidebar.markdown("---")
    st.sidebar.header("💰 Finansal Parametreler")
    price_steel = st.sidebar.number_input("Boru/Çelik ($/kg)", min_value=0.5, value=1.20, step=0.1)
    price_kure = st.sidebar.number_input("Küre ($/adet)", min_value=5.0, value=18.50, step=0.5)
    price_labor = st.sidebar.number_input("Otomasyon Kaynak ($/çubuk)", min_value=1.0, value=4.50, step=0.5)

    # 3. ZONAL İTERASYON MOTORU
    best_modul, min_weight_per_m2 = None, float('inf')
    best_z1, best_z2, best_z3 = None, None, None
    best_length = 0
    
    test_modules = [x / 10.0 for x in range(15, 36)] 
    
    def get_optimum_pipe(force, length_mm):
        for idx, r in df_pipes.iterrows():
            Ncr = (math.pi**2 * 200000 * r["I_mm4"]) / (length_mm**2) / 1000
            if min(r["Akma_Kapasitesi_kN"], Ncr / 1.5) >= force:
                return r
        return df_pipes.iloc[-1] 
    
    for a in test_modules:
        max_moment = (load_Q * (span_L**2)) / 8
        max_force = max_moment / depth_d
        cubuk_boyu_mm = math.sqrt((a/2)**2 + (a/2)**2 + depth_d**2) * 1000
        
        pipe_z1 = get_optimum_pipe(max_force, cubuk_boyu_mm)          
        pipe_z2 = get_optimum_pipe(max_force * 0.65, cubuk_boyu_mm)   
        pipe_z3 = get_optimum_pipe(max_force * 0.35, cubuk_boyu_mm)   
        
        avg_kg_m = (pipe_z1["Agirlik_kg_m"] * 0.30) + (pipe_z2["Agirlik_kg_m"] * 0.40) + (pipe_z3["Agirlik_kg_m"] * 0.30)
        avg_konik = (pipe_z1["Konik_kg"] * 0.30) + (pipe_z2["Konik_kg"] * 0.40) + (pipe_z3["Konik_kg"] * 0.30)
        
        boru_uzunluk_m2 = (4/a) + (4 * (cubuk_boyu_mm/1000) / (a**2))
        toplam_agirlik_indeksi = (boru_uzunluk_m2 * avg_kg_m) + ((4 / (a**2)) * avg_konik)
        
        if toplam_agirlik_indeksi < min_weight_per_m2:
            min_weight_per_m2 = toplam_agirlik_indeksi
            best_modul, best_length = a, cubuk_boyu_mm
            best_z1, best_z2, best_z3 = pipe_z1, pipe_z2, pipe_z3

    # 4. SONUÇ VE İŞ EMRİ
    if best_z1 is not None:
        Nx = max(1, int(span_L / best_modul))
        Ny = max(1, int(width_W / best_modul))
        grid_L = Nx * best_modul # EKSİK OLAN VE HATAYA SEBEP OLAN DEĞİŞKEN EKLENDİ
        
        bottom_nodes_count = (Nx + 1) * (Ny + 1)
        top_nodes_count = Nx * Ny
        total_kure_count = bottom_nodes_count + top_nodes_count
        
        bottom_chords_count = Nx * (Ny + 1) + Ny * (Nx + 1)
        top_chords_count = max(0, (Nx - 1) * Ny) + max(0, (Ny - 1) * Nx)
        diagonal_chords_count = 4 * Nx * Ny
        total_chords_count = bottom_chords_count + top_chords_count + diagonal_chords_count
        
        z1_count = int(total_chords_count * 0.30)
        z2_count = int(total_chords_count * 0.40)
        z3_count = total_chords_count - z1_count - z2_count
        
        horizontal_length_m = (bottom_chords_count + top_chords_count) * best_modul
        diagonal_length_m = diagonal_chords_count * (best_length / 1000.0)
        total_len_m = horizontal_length_m + diagonal_length_m
        
        weight_z1 = (total_len_m * 0.30 * best_z1["Agirlik_kg_m"]) + (z1_count * 2 * best_z1["Konik_kg"])
        weight_z2 = (total_len_m * 0.40 * best_z2["Agirlik_kg_m"]) + (z2_count * 2 * best_z2["Konik_kg"])
        weight_z3 = (total_len_m * 0.30 * best_z3["Agirlik_kg_m"]) + (z3_count * 2 * best_z3["Konik_kg"])
        total_steel_weight_kg = weight_z1 + weight_z2 + weight_z3
        
        total_standoff_length_m = sum([0.20 + (min((i * best_modul + best_modul/2), grid_L - (i * best_modul + best_modul/2)) * (roof_slope / 100.0)) if cati_formu == "Düz / Beşik" else 0.20 for i in range(Nx) for j in range(Ny)])
        total_secondary_steel_kg = (total_standoff_length_m * 5.0) + ((top_nodes_count * best_modul) * 5.0)
        
        total_project_cost = (total_steel_weight_kg * price_steel) + (total_secondary_steel_kg * price_steel) + (total_kure_count * price_kure) + (total_chords_count * price_labor)
        
        col_grafik, col_hesap = st.columns([1.5, 1])
        
        with col_hesap:
            st.subheader("🏆 Zonal Optimizasyon Sonucu")
            st.success(f"İdeal Modül Boyu: **{best_modul} metre**")
            
            st.markdown("#### 🏭 Fabrika Üretim Grupları")
            z_df = pd.DataFrame({
                "Bölge (Zon)": ["Zon 1 (Ağır)", "Zon 2 (Orta)", "Zon 3 (Hafif)"],
                "Boru Tipi": [best_z1['Boru'], best_z2['Boru'], best_z3['Boru']],
                "Kullanım": ["%30", "%40", "%30"]
            })
            st.table(z_df.set_index("Bölge (Zon)"))
            
            st.markdown("### 📊 Proje Metrajı ve Maliyet")
            metraj_df = pd.DataFrame({
                "Kalem": ["Uzay Kafes Çeliği (Zonal)", "Dikme/Aşık Çeliği", "Toplam Küre", "Kaynak İşlemi"],
                "Miktar": [f"{total_steel_weight_kg/1000:.1f} Ton", f"{total_secondary_steel_kg/1000:.1f} Ton", f"{total_kure_count} Adet", f"{total_chords_count} Adet"],
                "Tutar": [f"${(total_steel_weight_kg * price_steel):,.0f}", f"${(total_secondary_steel_kg * price_steel):,.0f}", f"${(total_kure_count * price_kure):,.0f}", f"${(total_chords_count * price_labor):,.0f}"]
            })
            st.table(metraj_df.set_index("Kalem"))
            st.info(f"💰 **Toplam Tahmini Bütçe: ${total_project_cost:,.0f}**")
            
            st.markdown("### 📥 Otomasyon İş Emri")
            wo_data = []
            for _ in range(z1_count): wo_data.append({"Bölge": "Zon 1 (Merkez)", "Parça": "Çubuk", "Boy (mm)": int(best_length), "Boru": best_z1['Boru'], "Konik": best_z1['Konik'], "Civata": best_z1['Civata']})
            for _ in range(z2_count): wo_data.append({"Bölge": "Zon 2 (Geçiş)", "Parça": "Çubuk", "Boy (mm)": int(best_length), "Boru": best_z2['Boru'], "Konik": best_z2['Konik'], "Civata": best_z2['Civata']})
            for _ in range(z3_count): wo_data.append({"Bölge": "Zon 3 (Kenar)", "Parça": "Çubuk", "Boy (mm)": int(best_length), "Boru": best_z3['Boru'], "Konik": best_z3['Konik'], "Civata": best_z3['Civata']})
            
            csv = pd.DataFrame(wo_data).to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 İmalat İş Emrini İndir (CSV)", data=csv, file_name=f'Altinyaldiz_Zonal_{span_L}x{width_W}.csv', mime='text/csv', use_container_width=True)

        with col_grafik:
            st.subheader(f"🧊 {cati_formu} ({span_L}m x {width_W}m)")
            
            node_x, node_y, node_z, purlin_nodes = [], [], [], {}
            bottom_nodes, top_nodes = {}, {}
            
            def get_z_offset(x, y):
                if cati_formu == "Düz / Beşik": return 0
                elif cati_formu == "Tonoz": return arch_rise * math.sin(math.pi * x / span_L)
                elif cati_formu == "Kubbe": return arch_rise * math.sin(math.pi * x / span_L) * math.sin(math.pi * y / width_W)

            for i in range(Nx + 1):
                for j in range(Ny + 1):
                    bottom_nodes[(i, j)] = len(node_x)
                    nx, ny = i * best_modul, j * best_modul
                    node_x.append(nx); node_y.append(ny); node_z.append(get_z_offset(nx, ny))
                    
            for i in range(Nx):
                for j in range(Ny):
                    top_nodes[(i, j)] = len(node_x)
                    tx, ty = i * best_modul + best_modul/2, j * best_modul + best_modul/2
                    tz = depth_d + get_z_offset(tx, ty)
                    node_x.append(tx); node_y.append(ty); node_z.append(tz)
                    standoff_h = 0.20 + (min(tx, grid_L - tx) * (roof_slope / 100.0)) if cati_formu == "Düz / Beşik" else 0.20
                    purlin_nodes[(i, j)] = (tx, ty, tz + standoff_h)
                    
            line_x, line_y, line_z, p_line_x, p_line_y, p_line_z, s_line_x, s_line_y, s_line_z = [], [], [], [], [], [], [], [], []
            def add_line(n1, n2, lst_x, lst_y, lst_z):
                lst_x.extend([node_x[n1], node_x[n2], None]); lst_y.extend([node_y[n1], node_y[n2], None]); lst_z.extend([node_z[n1], node_z[n2], None])
                
            for i in range(Nx + 1):
                for j in range(Ny + 1):
                    if i < Nx: add_line(bottom_nodes[(i, j)], bottom_nodes[(i+1, j)], line_x, line_y, line_z)
                    if j < Ny: add_line(bottom_nodes[(i, j)], bottom_nodes[(i, j+1)], line_x, line_y, line_z)
            for i in range(Nx):
                for j in range(Ny):
                    if i < Nx - 1: add_line(top_nodes[(i, j)], top_nodes[(i+1, j)], line_x, line_y, line_z)
                    if j < Ny - 1: add_line(top_nodes[(i, j)], top_nodes[(i, j+1)], line_x, line_y, line_z)
                    
                    curr_node_idx = top_nodes[(i, j)]
                    ctx, cty, ctz = node_x[curr_node_idx], node_y[curr_node_idx], node_z[curr_node_idx]
                    px1, py1, pz1 = purlin_nodes[(i, j)]
                    s_line_x.extend([ctx, px1, None]); s_line_y.extend([cty, py1, None]); s_line_z.extend([ctz, pz1, None])
                    if j < Ny - 1:
                        px2, py2, pz2 = purlin_nodes[(i, j+1)]
                        p_line_x.extend([px1, px2, None]); p_line_y.extend([py1, py2, None]); p_line_z.extend([pz1, pz2, None])
                        
            for i in range(Nx):
                for j in range(Ny):
                    tn = top_nodes[(i, j)]
                    add_line(tn, bottom_nodes[(i, j)], line_x, line_y, line_z); add_line(tn, bottom_nodes[(i+1, j)], line_x, line_y, line_z)
                    add_line(tn, bottom_nodes[(i, j+1)], line_x, line_y, line_z); add_line(tn, bottom_nodes[(i+1, j+1)], line_x, line_y, line_z)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(x=line_x, y=line_y, z=line_z, mode='lines', line=dict(color='#1f77b4', width=2), name='Uzay Kafes'))
            fig.add_trace(go.Scatter3d(x=s_line_x, y=s_line_y, z=s_line_z, mode='lines', line=dict(color='#ff7f0e', width=3), name='Dikme'))
            fig.add_trace(go.Scatter3d(x=p_line_x, y=p_line_y, z=p_line_z, mode='lines', line=dict(color='#2ca02c', width=4), name='Aşık'))
            fig.add_trace(go.Scatter3d(x=node_x, y=node_y, z=node_z, mode='markers', marker=dict(size=3, color='#d62728'), name='Küre'))
            fig.update_layout(scene=dict(aspectmode='data', xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), margin=dict(l=0, r=0, b=0, t=0), height=500, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Girdiğiniz değerler için kütüphanede uygun çözüm bulunamadı.")
