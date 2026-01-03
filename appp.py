import streamlit as st

# ======================================================
# BASIC CONFIG
# ======================================================
st.set_page_config(
    page_title="Lab Concentration Calculator",
    layout="wide"
)

st.title("🔬 Laboratory Concentration Calculator")
st.caption("Molarity • Normality • PPM • Mass • Dilution")

# ======================================================
# SIDEBAR NOTE (IMPORTANT CONCEPT)
# ======================================================
# Streamlit hanya memiliki SATU sidebar.
# "Dua sidebar" di sini disimulasikan dengan:
# 1. Sidebar utama (Insight)
# 2. Sidebar section kedua menggunakan expander

# ======================================================
# SIDEBAR 1 — INSIGHT (TEXT ONLY)
# ======================================================
st.sidebar.header("📘 Insight")
st.sidebar.markdown(
    """
    🔹 Lorem ipsum dolor sit amet, consectetur adipiscing elit.  
    🔹 Laboratorium kimia membutuhkan perhitungan yang presisi.  
    🔹 Kesalahan satuan dapat menyebabkan kesalahan eksperimen.  
    🔹 Gunakan kalkulator ini untuk membantu pekerjaan rutin di lab.  
    🔹 Always double-check your calculations.
    """
)

st.sidebar.divider()

# ======================================================
# SIDEBAR 2 — KALKULATOR (USING EXPANDER)
# ======================================================
with st.sidebar.expander("🧮 Kalkulator", expanded=True):
    menu = st.radio(
        "Pilih jenis kalkulator",
        (
            "Massa → Konsentrasi",
            "Konsentrasi → Massa",
            "Pengenceran Larutan"
        )
    )

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def volume_to_liter(v, unit):
    if unit == "L":
        return v
    if unit == "mL":
        return v / 1000
    if unit == "µL":
        return v / 1_000_000

# ======================================================
# MAIN PAGE CONTENT
# ======================================================

# ------------------------------------------------------
# 1. MASS → CONCENTRATION
# ------------------------------------------------------
if menu == "Massa → Konsentrasi":
    st.header("⚗️ Hitung Konsentrasi dari Massa")

    col1, col2 = st.columns(2)

    with col1:
        mass = st.number_input("Massa zat (g)", min_value=0.0, value=1.0)
        molar_mass = st.number_input("Mr / Molar mass (g/mol)", min_value=0.0, value=58.44)
        n_equiv = st.number_input("Jumlah ekivalen (n)", min_value=1.0, value=1.0)

    with col2:
        volume = st.number_input("Volume larutan", min_value=0.0, value=100.0)
        volume_unit = st.selectbox("Satuan volume", ["mL", "L", "µL"])

    V_L = volume_to_liter(volume, volume_unit)

    if V_L > 0 and molar_mass > 0:
        mol = mass / molar_mass
        M = mol / V_L
        N = M * n_equiv
        ppm = (mass * 1000) / V_L

        st.subheader("📊 Hasil Perhitungan")
        st.metric("Molaritas (M)", f"{M:.6g}")
        st.metric("Normalitas (N)", f"{N:.6g}")
        st.metric("PPM (mg/L)", f"{ppm:.6g}")

# ------------------------------------------------------
# 2. CONCENTRATION → MASS
# ------------------------------------------------------
elif menu == "Konsentrasi → Massa":
    st.header("⚖️ Hitung Massa dari Konsentrasi")

    col1, col2 = st.columns(2)

    with col1:
        concentration = st.number_input("Nilai konsentrasi", min_value=0.0, value=0.1)
        unit = st.selectbox("Satuan konsentrasi", ["M", "N", "ppm"])
        molar_mass = st.number_input("Mr / Molar mass (g/mol)", min_value=0.0, value=58.44)
        n_equiv = st.number_input("Jumlah ekivalen (n)", min_value=1.0, value=1.0)

    with col2:
        volume = st.number_input("Volume larutan", min_value=0.0, value=250.0)
        volume_unit = st.selectbox("Satuan volume", ["mL", "L", "µL"], key="vol2")

    V_L = volume_to_liter(volume, volume_unit)

    if V_L > 0:
        if unit == "M":
            mass = concentration * V_L * molar_mass
        elif unit == "N":
            mass = (concentration / n_equiv) * V_L * molar_mass
        else:  # ppm
            mass = concentration * V_L / 1000

        st.subheader("📊 Hasil Perhitungan")
        st.metric("Massa yang harus ditimbang (g)", f"{mass:.6g}")

# ------------------------------------------------------
# 3. DILUTION
# ------------------------------------------------------
elif menu == "Pengenceran Larutan":
    st.header("🧪 Pengenceran Larutan (C₁V₁ = C₂V₂)")

    col1, col2 = st.columns(2)

    with col1:
        C1 = st.number_input("Konsentrasi awal (C1)", min_value=0.0, value=1.0)
        C2 = st.number_input("Konsentrasi akhir (C2)", min_value=0.0, value=0.1)

    with col2:
        V2 = st.number_input("Volume akhir (V2)", min_value=0.0, value=500.0)
        V2_unit = st.selectbox("Satuan volume", ["mL", "L", "µL"], key="vol3")

    V2_L = volume_to_liter(V2, V2_unit)

    if C1 > 0 and V2_L > 0:
        V1_L = (C2 * V2_L) / C1
        st.subheader("📊 Hasil Perhitungan")
        st.metric("Volume stok (V1)", f"{V1_L*1000:.6g} mL")

st.markdown("---")
st.caption("© 2026 • Streamlit Lab Calculator")
