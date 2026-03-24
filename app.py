import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Altınyaldız Statik AI", layout="wide")

# 1. ŞİFRE EKRANI KONTROLÜ
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.markdown("### 🔒 Altınyaldız Statik Hesap Motoruna Giriş")
        st.text_input("Şifre:", type="password", key="pwd")
        if st.session_state.pwd == "CFO2026": # Şifreni buradan değiştirebilirsin
            st.session_state["password_correct"] = True
            st.rerun()
        elif st.session_state.pwd != "":
            st.error("Hatalı şifre, lütfen tekrar deneyin.")
        return False
    return True

if check_password():
    st.title("🏗️ Uzay Kafes Statik Optimizasyon Motoru")
    st.markdown("Girilen yüklere ve Altınyaldız boru kütüphanesine göre en ekonomik kesitleri iteratif olarak seçer.")

    # 2. RFP BORU KÜTÜPHANESİ (Sadece senin fabrikanın ürettiği borular)
    # Alan Hesabı: A = pi * (D - t) * t
    pipe_data = [
        {"Boru": "42.4x2.5", "D": 42.4, "t": 2.5, "Agirlik_kg_m": 2.46},
        {"Boru": "48.3x2.5", "D": 48.3, "t": 2.5, "Agirlik_kg_m": 2.82},
        {"Boru": "60.3x3.0", "D": 60.3, "t": 3.0, "Agirlik_kg_m": 4.24},
        {"Boru": "76.1x3.0", "D": 76.1, "t": 3.0, "Agirlik_kg_m": 5.41},
        {"Boru": "88.9x4.0", "D": 88.9, "t": 4.0, "Agirlik_kg_m": 8.37},
        {"Boru": "114.3x4.0", "D": 114.3, "t": 4.0, "Agirlik_kg_m": 10.88},
        {"Boru": "139.7x5.0", "D": 139.7, "t": 5.0, "Agirlik_kg_m": 16.60}
    ]
    df_pipes = pd.DataFrame(pipe_data)
    
    # Eksenel Çekme Kapasitesi Hesabı (S235 Çelik için Basitleştirilmiş - fy = 235 MPa)
    df_pipes["Alan_mm2"] = math.pi * (df_pipes["D"] - df_pipes["t"]) * df_pipes["t"]
    df_pipes["Kapasite_kN"] = (df_pipes["Alan_mm2"] * 235) / 1000

    # 3. KULLANICI GİRDİ PANELİ
    st.sidebar.header("Statik Parametreler")
    span_L = st.sidebar.number_input("Açıklık (L) - metre", min_value=10.0, value=30.0, step=1.0)
    load_Q = st.sidebar.number_input("Toplam Yük (Kar+Rüzgar+Zati) - kN/m2", min_value=0.5, value=1.5, step=0.1)
    depth_d = st.sidebar.number_input("Sistem Derinliği (h) - metre", min_value=1.0, value=2.0, step=0.1)

    st.write("---")
    
    # 4. STATİK ÇÖZÜM VE İTERASYON
    # Basitleştirilmiş Mak. Eksenel Kuvvet Yaklaşımı: N = (Q * L^2 / 8) / h
    max_moment = (load_Q * (span_L**2)) / 8
    max_force_kN = max_moment / depth_d
    
    st.subheader("📊 Analiz Sonuçları")
    st.info(f"Hesaplanan Maksimum Çubuk Kuvveti: **{max_force_kN:.2f} kN**")

    # Optimizasyon: Kuvveti taşıyabilen EN HAFİF boruyu bul
    uygun_borular = df_pipes[df_pipes["Kapasite_kN"] >= max_force_kN].sort_values(by="Agirlik_kg_m")
    
    if not uygun_borular.empty:
        optimum_boru = uygun_borular.iloc[0]
        st.success(f"✅ **Optimum Kesit Bulundu:** {optimum_boru['Boru']}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Seçilen Boru", optimum_boru['Boru'])
        col2.metric("Kapasite (kN)", f"{optimum_boru['Kapasite_kN']:.1f}")
        col3.metric("Birim Ağırlık", f"{optimum_boru['Agirlik_kg_m']} kg/m")
        
        # CFO Özeti
        st.markdown("### 💰 Finansal Özet")
        st.write(f"Sistem, {max_force_kN:.1f} kN kuvveti taşımak için tonajı minimize ederek {optimum_boru['Agirlik_kg_m']} kg/m ağırlığındaki **{optimum_boru['Boru']}** borusunu seçmiştir. Daha ağır bir kesit kullanılması israf olacaktır.")
    else:
        st.error("⚠️ Uyarı: Girdiğiniz yükler için mevcut boru kütüphanesinde yeterli kapasiteye sahip kesit bulunamadı! Daha büyük çaplı borular (örn: Ø159, Ø219) eklenmelidir.")
    
    with st.expander("Tüm Boru Kütüphanesi ve Kapasitelerini Gör"):
        st.dataframe(df_pipes[["Boru", "Agirlik_kg_m", "Kapasite_kN"]])
