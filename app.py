import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="cudai",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
    
)


USERS = {
    "waryo": "123456789",
    "user1": "password1"
}

# Inisialisasi session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "data" not in st.session_state:
    st.session_state.data = None

# Login Page
if not st.session_state.authenticated:
    st.title("LINK BIRUUU NEW :smile:")
    st.subheader("INPUT WOI", divider=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(username) == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

page = st.sidebar.selectbox(
    "📄 Go to Page",
    ("Dashboard", "Upload Data", "Finance Chatbot", "Settings")
)

# Sample chatbot reply
def finance_bot(question, df):
    if df is None:
        return "Please upload your data first."
    if "pengeluaran terbesar" in question.lower():
        max_row = df.loc[df["Amount"].idxmin()]
        return f"Pengeluaran terbesar Anda adalah {abs(max_row['Amount']):,.0f} untuk {max_row['Category']} pada {max_row['Date']}."
    return "Maaf, saya belum memahami pertanyaan Anda sepenuhnya."


# Dashboard Page
if page == "Dashboard":
    st.title("📊 Personal Finance Dashboard")
    if st.session_state.data is None:
        st.info("Please upload your transaction data first on the 'Upload Data' page.")
    else:
        df = st.session_state.data
        total_income = df[df["Amount"] > 0]["Amount"].sum()
        total_expense = df[df["Amount"] < 0]["Amount"].sum()
        net_balance = total_income + total_expense

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"Rp {total_income:,.0f}")
        col2.metric("Total Expense", f"Rp {abs(total_expense):,.0f}")
        col3.metric("Net Balance", f"Rp {net_balance:,.0f}")

        st.subheader("📈 Monthly Expenses")
        df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)
        monthly = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().reset_index()
        fig = px.bar(monthly, x="Month", y="Amount", title="Monthly Expenses", labels={'Amount':'Total Expense'})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Expense by Category")
        category = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().reset_index()
        fig2 = px.bar(category, x="Category", y="Amount", title="Expenses by Category", labels={'Amount':'Total Expense'})
        st.plotly_chart(fig2, use_container_width=True)


# Upload Page
elif page == "Upload Data":
    st.title("📁 Upload Your Financial Transactions")
    st.markdown("Format file: CSV dengan kolom `Date`, `Amount`, `Category`")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df["Date"] = pd.to_datetime(df["Date"])
            st.dataframe(df.head())
            st.session_state.data = df
            st.success("Data uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading data: {e}")

# Chatbot Page
elif page == "Finance Chatbot":
    st.title("🔬 Lab Concentration & Mass Converter")
    st.markdown(
    """
      A handy Streamlit app to:
- convert **mass (g)** + **volume** → **molarity / normality / ppm**
- convert **molarity / normality / ppm** → **mass to weigh (g)**
- perform **dilution calculations** (C1V1 = C2V2)

**Notes:** Normality requires the number of equivalents per mole (n). For ppm conversions involving molar units, provide the molar mass.
"""
)



    calc_type = st.radio("Pilih jenis kalkulator:", (
    "Hitung konsentrasi dari massa (g → M/N/ppm)",
    "Hitung massa dari konsentrasi (M/N/ppm → g)",
    "Pengenceran (C1V1 = C2V2)"
))

# Helper converters

def vol_to_liters(volume: float, unit: str) -> float:
    if unit == "L":
        return volume
    elif unit == "mL":
        return volume / 1000.0
    elif unit == "µL":
        return volume / 1e6
    else:
        return volume


def conc_to_molar(conc_value: float, conc_unit: str, molar_mass: float = None, eq_per_mol: float = None):
    """
    Convert a concentration with unit to mol/L (for molarity) or eq/L (for normality). 
    Supports: M, mM, µM, N, ppm
    If unit is ppm and molar_mass is provided it returns mol/L. If unit is N and eq_per_mol provided it returns mol/L = N / eq_per_mol
    """
    unit = conc_unit
    if unit == "M":
        return conc_value
    if unit == "mM":
        return conc_value / 1000.0
    if unit == "µM":
        return conc_value / 1e6
    if unit == "N":
        if not eq_per_mol or eq_per_mol == 0:
            # if eq_per_mol unknown, return None to indicate error
            return None
        return conc_value / eq_per_mol
    if unit == "ppm":
        # ppm ~ mg solute / L solution. Convert ppm -> mol/L using molar mass (g/mol)
        if not molar_mass or molar_mass == 0:
            return None
        # ppm (mg/L) -> g/L = ppm/1000 -> mol/L = (g/L) / (g/mol) = ppm/(1000*molar_mass)
        return conc_value / (1000.0 * molar_mass)
    return None


def molar_to_display(value_molar: float):
    """
    Return a dict of nicely formatted concentration units based on mol/L
    """
    return {
        "M": value_molar,
        "mM": value_molar * 1000.0,
        "µM": value_molar * 1e6,
    }

# Section 1: mass -> concentration
if calc_type == "Hitung konsentrasi dari massa (g → M/N/ppm)":
    st.header("Hitung konsentrasi dari massa (g → M/N/ppm)")
    col1, col2 = st.columns(2)
    with col1:
        mass_g = st.number_input("Massa zat (gram)", min_value=0.0, value=1.0, format="%.6f")
        molar_mass = st.number_input("Molar mass (g/mol)", min_value=0.0, value=58.44, format="%.6f",
                                     help="Contoh: NaCl = 58.44 g/mol. Dibutuhkan untuk M ⇄ ppm konversi juga.")
        eq_per_mol = st.number_input("Equivalents per mole (n, untuk Normalitas)", min_value=0.0, value=1.0,
                                     help="Masukkan 1 untuk zat netral, 2 untuk H2SO4 (2 ekivalen), dst.")
    with col2:
        vol = st.number_input("Volume larutan", min_value=0.0, value=100.0, format="%.6f")
        vol_unit = st.selectbox("Satuan volume", ("mL", "L", "µL"), index=0)

    V_L = vol_to_liters(vol, vol_unit)

    if V_L == 0:
        st.warning("Masukkan volume yang bukan nol.")
    else:
        mol = mass_g / molar_mass if molar_mass != 0 else None
        if mol is None:
            st.error("Molar mass harus diisi dan tidak nol untuk perhitungan molaritas dan ppm dari massa.")
        else:
            molarity = mol / V_L
            normality = molarity * eq_per_mol
            ppm = (mass_g * 1000.0) / V_L  # mg/L

            st.subheader("Hasil")
            st.write(f"Massa: **{mass_g:.6f} g** | Volume: **{vol:.6f} {vol_unit}**")
            st.write(f"Molar mass: **{molar_mass:.6f} g/mol** | Equivalents per mole (n): **{eq_per_mol:.6f}**")

            cols = st.columns(3)
            cols[0].metric("Molaritas (mol/L)", f"{molarity:.6g} M")
            cols[1].metric("Normalitas (eq/L)", f"{normality:.6g} N")
            cols[2].metric("PPM (mg/L)", f"{ppm:.6g} ppm")

            with st.expander("Langkah perhitungan"):
                st.write("Rumus dan langkah:")
                st.latex(r"\text{mol} = \frac{masa\ (g)}{molar\ mass\ (g/mol)}")
                st.latex(r"Molaritas\ (M) = \frac{mol}{Volume\ (L)}")
                st.latex(r"Normalitas\ (N) = Molaritas \times n\ (equivalents\ per\ mole)")
                st.latex(r"PPM\ (mg/L) = \frac{masa\ (g)\times 1000}{Volume\ (L)}")
                st.write("---")
                st.write(f"mol = {mass_g:.6f} / {molar_mass:.6f} = {mol:.6g} mol")
                st.write(f"Molaritas = {mol:.6g} / {V_L:.6g} L = {molarity:.6g} M")
                st.write(f"Normalitas = {molarity:.6g} * {eq_per_mol:.6g} = {normality:.6g} N")
                st.write(f"PPM = {mass_g:.6f} g *1000 / {V_L:.6g} L = {ppm:.6g} ppm")

# Section 2: concentration -> mass
elif calc_type == "Hitung massa dari konsentrasi (M/N/ppm → g)":
    st.header("Hitung massa yang harus ditimbang dari konsentrasi (M/N/ppm → g)")
    col1, col2 = st.columns(2)
    with col1:
        conc_value = st.number_input("Nilai konsentrasi (angka)", min_value=0.0, value=0.1, format="%.6f")
        conc_unit = st.selectbox("Satuan konsentrasi", ("M", "mM", "µM", "N", "ppm"), index=0)
        molar_mass2 = st.number_input("Molar mass (g/mol) — diperlukan untuk M ⇄ ppm dan ppm→g", min_value=0.0, value=58.44,
                                      format="%.6f")
    with col2:
        vol2 = st.number_input("Volume larutan", min_value=0.0, value=250.0, format="%.6f")
        vol2_unit = st.selectbox("Satuan volume", ("mL", "L", "µL"), index=0)
        eq_per_mol2 = st.number_input("Equivalents per mole (n, untuk Normalitas)", min_value=0.0, value=1.0)

    V2_L = vol_to_liters(vol2, vol2_unit)

    if V2_L == 0:
        st.warning("Masukkan volume yang bukan nol.")
    else:
        # convert input concentration to mol/L where appropriate
        molar_equiv = conc_to_molar(conc_value, conc_unit, molar_mass=molar_mass2, eq_per_mol=eq_per_mol2)
        if molar_equiv is None:
            st.error("Konversi tidak dapat dilakukan — pastikan molar mass/eq tersedia untuk unit yang dipilih.")
        else:
            # molar_equiv is mol/L
            mass_needed_g = molar_equiv * V2_L * molar_mass2
            # For normality input (N), user expects mass for that normality: molar_equiv was computed as mol/L = N/n
            if conc_unit == "ppm":
                # if user gave ppm and we converted to mol/L, mass can be obtained directly from ppm formula
                mass_from_ppm = conc_value * V2_L / 1000.0  # ppm (mg/L) * L -> mg -> /1000 -> g
                mass_needed_g = mass_from_ppm

            st.subheader("Hasil")
            st.write(f"Volume akhir: **{vol2:.6f} {vol2_unit}** (={V2_L:.6g} L)")
            st.write(f"Konsentrasi target: **{conc_value:.6f} {conc_unit}**")
            st.metric("Massa yang harus ditimbang (g)", f"{mass_needed_g:.6g} g")

            with st.expander("Langkah perhitungan"):
                if conc_unit == "ppm":
                    st.write("PPM -> massa: massa (g) = ppm (mg/L) * V (L) / 1000")
                    st.write(f"massa = {conc_value} * {V2_L} / 1000 = {mass_needed_g:.6g} g")
                else:
                    st.write("Rumus umum untuk molaritas:")
                    st.latex(r"massa\ (g) = M\ (mol/L) \times V\ (L) \times molar\ mass\ (g/mol)")
                    st.write(f"massa = {molar_equiv:.6g} mol/L * {V2_L:.6g} L * {molar_mass2:.6g} g/mol = {mass_needed_g:.6g} g")

# Section 3: Dilution
else:
    st.header("Pengenceran (C1V1 = C2V2)")
    st.write("Masukkan konsentrasi awal & akhir dan volume akhir — kami hitung volume stok yang diperlukan (V1).")
    col1, col2 = st.columns(2)
    with col1:
        C1_val = st.number_input("Konsentrasi awal (C1)", min_value=0.0, value=1.0, format="%.6f")
        C1_unit = st.selectbox("Satuan C1", ("M", "mM", "µM", "N", "ppm"), index=0)
        molar_mass3 = st.number_input("Molar mass (g/mol) — diperlukan untuk ppm konversi", min_value=0.0, value=58.44,
                                      format="%.6f")
        eq_per_mol3 = st.number_input("Equivalents per mole (n, untuk Normalitas)", min_value=0.0, value=1.0)
    with col2:
        C2_val = st.number_input("Konsentrasi akhir (C2)", min_value=0.0, value=0.1, format="%.6f")
        C2_unit = st.selectbox("Satuan C2", ("M", "mM", "µM", "N", "ppm"), index=1)
        V2 = st.number_input("Volume akhir (V2)", min_value=0.0, value=500.0, format="%.6f")
        V2_unit = st.selectbox("Satuan volume akhir", ("mL", "L", "µL"), index=0)

    V2_L = vol_to_liters(V2, V2_unit)

    # convert C1 and C2 to mol/L equivalence
    C1_molL = conc_to_molar(C1_val, C1_unit, molar_mass=molar_mass3, eq_per_mol=eq_per_mol3)
    C2_molL = conc_to_molar(C2_val, C2_unit, molar_mass=molar_mass3, eq_per_mol=eq_per_mol3)

    if V2_L == 0:
        st.warning("Masukkan volume akhir yang bukan nol.")
    elif (C1_molL is None) or (C2_molL is None):
        st.error("Tidak dapat mengonversi C1 atau C2 ke mol/L. Jika menggunakan ppm, pastikan molar mass diisi; jika N, pastikan n diisi.")
    else:
        if C1_molL == 0:
            st.error("Konsentrasi awal C1 tidak boleh nol.")
        else:
            V1_L = (C2_molL * V2_L) / C1_molL
            # display in user-friendly units (mL if small)
            def choose_vol_unit(v_l):
                if v_l >= 1:
                    return (v_l, "L")
                else:
                    return (v_l * 1000.0, "mL")

            V1_display, V1_unit = choose_vol_unit(V1_L)

            st.subheader("Hasil")
            st.write(f"C1 = {C1_val} {C1_unit} (=> {C1_molL:.6g} mol/L)")
            st.write(f"C2 = {C2_val} {C2_unit} (=> {C2_molL:.6g} mol/L)")
            st.write(f"V2 = {V2:.6f} {V2_unit} (=> {V2_L:.6g} L)")
            st.metric("Volume stok yang diperlukan (V1)", f"{V1_display:.6g} {V1_unit}")

            with st.expander("Langkah perhitungan"):
                st.write("Persamaan: C1 * V1 = C2 * V2 \Rightarrow V1 = C2*V2 / C1")
                st.write(f"V1 (L) = {C2_molL:.6g} * {V2_L:.6g} / {C1_molL:.6g} = {V1_L:.6g} L")

st.markdown("---")
st.caption("Versi: 1.0 — Jika Anda ingin saya tambahkan fitur: simpan ke GitHub, export CSV, atau mode batch, katakan saja!")
    











