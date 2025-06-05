import streamlit as st
import pandas as pd
import os
from PIL import Image  # ← NEU: Logo-Anzeige

st.markdown("""
<style>

/* =========================
   🎨 GRUNDDESIGN & FARBEN
========================= */

html, body, .block-container {
    background-color: #FFFFFF;  # Haupt-Hintergrund weiß
    color: #2C332F;             # Standard-Schrift in dunklem Grau
    font-family: 'Helvetica Neue', sans-serif;
}

/* =========================
   🧭 SIDEBAR
========================= */

[data-testid="stSidebar"] {
    background-color: #F5F5F5 !important;  # Sidebar-Hintergrund hellgrau
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #2C332F !important;  # Sidebar-Text in dunklem Grau
}

/* =========================
   ✍️ INPUTS & DROPDOWNS
========================= */

.stTextInput input,
.stMultiSelect div[role="textbox"],
.stSelectbox div[data-baseweb="select"] {
    background-color: #2C332F !important;  # Dunkler Hintergrund
    color: white !important;               # Weiße Schrift in Eingabefeldern
    border-radius: 6px;
}

/* Platzhaltertext in hellerem Grau */
.stTextInput input::placeholder {
    color: #DDDDDD !important;
}

/* =========================
   🟩 BUTTONS & INTERAKTION
========================= */

.stButton > button {
    background-color: #007632;  # Primärfarbe Grün
    color: white !important;
    border-radius: 6px;
    font-weight: bold;
    padding: 0.4rem 1.2rem;
}
.stButton > button:hover {
    background-color: #2C332F;
    color: white;
}

/* Spezifisch: Button in der Intelligenten Suche */
div[role='button'] {
    color: white !important;
}

/* Export-Button */
.stDownloadButton > button {
    color: white !important;
    background-color: #2C332F !important;
}

/* Button im .stForm (z. B. "Hinzufügen") */
.stForm .stButton button {
    color: white !important;
}

/* =========================
   📊 METRIKEN & ZAHLEN
========================= */

div[data-testid="stMetricValue"],
div[data-testid="stMetricLabel"],
.stMetric, .stMetricLabel, .stMetricValue, .stMetricDelta {
    color: black !important;
}

/* =========================
   📑 FILTER-FORMULAR STYLE
========================= */

.stMultiSelect, .stSelectbox, .stTextInput > div > input {
    background-color: #F5F5F5;
    border-radius: 8px;
    padding: 0.3rem;
    color: #2C332F;
}

/* =========================
   📄 DATEN & HEADINGS
========================= */

.stDataFrame {
    background-color: white;
    border-radius: 8px;
    color: #2C332F;
}

h1, h2, h3, h4, h5, h6, label, .stMarkdown {
    color: #2C332F !important;
}

/* =========================
   🔕 DEAKTIVIERT / NICHT ZEIGEN
========================= */

# .stAlert { display: none !important; }  # Erfolgsmeldung wie „CSV geladen“ ausblenden, wenn nicht benötigt

</style>
""", unsafe_allow_html=True)


# 🔗 Direkt-Link zum Logo (RAW GitHub-Content)
logo_url = "https://raw.githubusercontent.com/JDivineTeams/blank-app/main/logo_jdivine.png"

# Mittig anzeigen mit Titel darunter
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
        st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src="{logo_url}" width="150" style="margin-bottom: 0.5rem;" />
            <h1 style='color: #2C332F; font-size: 1.8rem;'>Produkt-Matching Tool – JDivine Teams</h1>
        </div>
        """,
        unsafe_allow_html=True
    )


# Beispielhafte Kunden-Filterpresets
preset_filter = {
    "": {},  # Kein Preset
    "Feuerwehr": {
        "produkt": ["Hoodie", "Jacken"],
        "druckart": ["Stickerei"],
        "geschlecht": ["Unisex"],
    },
    "Tanzgruppe": {
        "produkt": ["T-Shirt", "Polo-Shirts"],
        "druckart": ["DTG"],
        "geschlecht": ["Damen", "Herren"],
    },
    "Sportverein": {
        "produkt": ["Hoodie", "T-Shirt"],
        "druckart": ["Flex"],
        "geschlecht": ["Unisex"],
    },
}


# ✅ Spaltenbereinigung für konsistente Filter
def clean_columns(df):
    df.columns = df.columns.str.strip().str.replace("\n", "", regex=False).str.replace("\r", "", regex=False).str.lower()
    return df

# ✅ Preisfelder bereinigen (Komma → Punkt, nur in Preisfeldern!)
def clean_price_columns(df):
    preis_spalten = ["produktpreis", "versandkosten", "ek-preis", "vk-preis"]
    for col in preis_spalten:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("€", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# 🔁 CSV-Datei aus GitHub-Repo laden
csv_path = "JDivine_Produktdaten_Tshirts_34Stk.csv"
repo_loaded = False  # Status-Marker

if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path, sep=";")
        df = clean_columns(df)
        df = clean_price_columns(df)

        def extract_main_brand(marke):
            if pd.isna(marke):
                return ""
            return marke.split()[0].upper()

        df["marke_kurz"] = df["marke"].apply(extract_main_brand)
        repo_loaded = True  # erfolgreich geladen
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der CSV-Datei: {e}")
        df = None
else:
    df = None

# 📤 Optionaler Datei-Upload
uploaded_file = st.file_uploader("📤 Optional: Eigene Produktdaten hochladen", type="csv")
if uploaded_file:
    try:
        extra_df = pd.read_csv(uploaded_file, sep=";", engine="python")
        extra_df = clean_columns(extra_df)
        extra_df = clean_price_columns(extra_df)
        if df is None:
            df = extra_df
        else:
            df = pd.concat([df, extra_df], ignore_index=True)
        st.success("✅ Eigene CSV-Daten wurden erfolgreich ergänzt.")
    except Exception as e:
        st.error(f"❌ Fehler beim Verarbeiten der hochgeladenen Datei: {e}")
        df = None
else:
    if not repo_loaded:
        st.warning("⚠️ Es wurde keine CSV geladen. Bitte lade manuell eine Datei hoch.")


# 🚫 Falls keine Daten geladen wurden
if df is None or df.empty:
    st.stop()

# 🛑 Prüfe auf 'produkt'
if "produkt" not in df.columns:
    st.error("❌ Spalte 'produkt' fehlt in den Daten. Bitte prüfen.")
    st.stop()

# Sidebar Styling
# Fix: Texte in Sidebar sichtbar machen (weiß auf dunkel)
st.markdown("""
    <style>
        .sidebar .stText, .sidebar .stSelectbox label, .sidebar .stMultiSelect label,
        .sidebar .stSlider label, .sidebar .stMetric label, .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6 {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)


# 📊 Sidebar Filter
with st.sidebar:
    st.header("🔍 Filter")
    preset = st.selectbox("🎯 Kundentyp wählen (Preset)", list(preset_filter.keys()))

    # Automatisch Filter setzen
    if preset and preset in preset_filter:
        selected_preset = preset_filter[preset]
        sel_produkte = selected_preset.get("produkt", [])
        sel_druckarten = selected_preset.get("druckart", [])
        sel_geschlecht = selected_preset.get("geschlecht", [])

    sel_produkte = st.multiselect("Produkt(e):", sorted(df["produkt"].dropna().unique()))
    sel_geschlecht = st.multiselect("Geschlecht(e):", sorted(df["geschlecht"].dropna().unique())) if "geschlecht" in df.columns else []
    sel_marken = st.multiselect("Marke(n):", sorted(df["marke_kurz"].dropna().unique()))
    sel_materialien = st.multiselect("Material(ien):", sorted(df["material"].dropna().unique())) if "material" in df.columns else []
    sel_anwendungen = st.multiselect("Anwendungsbereich(e):", sorted(df["anwendungsbereich"].dropna().unique())) if "anwendungsbereich" in df.columns else []
    sel_druckarten = st.multiselect("Druckart(en):", sorted(df["druckart"].dropna().unique())) if "druckart" in df.columns else []

    sel_farben = st.multiselect("Farbe(n):", sorted(df["farbe"].dropna().unique())) if "farbe" in df.columns else []
    sel_groessen = st.multiselect("Größe(n):", sorted(df["größe"].dropna().unique())) if "größe" in df.columns else []

    st.markdown("---")

    if "vk-preis" in df.columns and df["vk-preis"].notnull().any():
        min_price = float(df["vk-preis"].min())
        max_price = float(df["vk-preis"].max())
        if min_price < max_price:
            preisfilter = st.slider("💰 Verkaufspreis filtern (€)", min_price, max_price, (min_price, max_price), step=0.50)
        else:
            st.info(f"Nur ein Preis verfügbar: {min_price} € – Preisfilter wird übersprungen.")
            preisfilter = (min_price, max_price)
    else:
        preisfilter = (0, 9999)

# 🧮 Filter anwenden (ZUERST Standardfilter ohne Anwendungsbereich)
filtered = df.copy()
if sel_produkte:
    filtered = filtered[filtered["produkt"].isin(sel_produkte)]
if sel_geschlecht:
    filtered = filtered[filtered["geschlecht"].isin(sel_geschlecht)]
if sel_marken:
    filtered = filtered[filtered["marke_kurz"].isin(sel_marken)]
if sel_materialien:
    filtered = filtered[filtered["material"].isin(sel_materialien)]
if sel_druckarten:
    filtered = filtered[filtered["druckart"].isin(sel_druckarten)]
if sel_farben:
    filtered = filtered[filtered["farbe"].isin(sel_farben)]
if sel_groessen:
    filtered = filtered[filtered["größe"].isin(sel_groessen)]
if "vk-preis" in filtered.columns:
    filtered = filtered[filtered["vk-preis"].between(preisfilter[0], preisfilter[1])]


# 🔍 Erweiterte Freitextsuche über alle Spalten

# Session State initialisieren
if "search_terms" not in st.session_state:
    st.session_state.search_terms = []
if "eingabe_neu" not in st.session_state:
    st.session_state.eingabe_neu = ""

st.markdown("### 🔍 Suchleiste")

with st.form("suchformular", clear_on_submit=True):
    st.text_input("Begriff(e) eingeben (z. B. 'bio', 'hoodie', 'gildan')", key="eingabe_neu")
    submitted = st.form_submit_button("➕ Hinzufügen")

if submitted:
    neue_woerter = [w.strip().lower() for w in st.session_state.eingabe_neu.split() if w.strip()]
    neue_woerter = [w for w in neue_woerter if w not in st.session_state.search_terms]
    st.session_state.search_terms.extend(neue_woerter)


# Aktive Filter anzeigen mit ❌
st.markdown("**🗂️ Aktive Suchbegriffe:**")
to_remove = []
for i, begriff in enumerate(st.session_state.search_terms):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"• _{begriff}_")
    with col2:
        if st.button("❌", key=f"remove_search_{i}"):
            to_remove.append(begriff)
for item in to_remove:
    st.session_state.search_terms.remove(item)
# Seite neu laden → Liste sofort aktualisiert

# Begriffe auf DataFrame anwenden
for term in st.session_state.search_terms:
    mask = pd.Series(False, index=filtered.index)
    for col in filtered.columns:
        mask |= filtered[col].astype(str).str.contains(term, case=False, na=False)
    filtered = filtered[mask]


with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Live-Kennzahlen")

    if not filtered.empty and "vk-preis" in filtered.columns:
        st.metric("📦 Gefundene Produkte", len(filtered))
        st.metric("💰 Durchschnitt VK (€)", f"{filtered['vk-preis'].mean():.2f}")
        st.metric("🔻 Günstigster VK (€)", f"{filtered['vk-preis'].min():.2f}")
    else:
        st.info("Keine Ergebnisse zur Auswertung.")

# 📈 Ergebnisse anzeigen
st.markdown("### 🎯 Gefundene Kombinationen:")
if not filtered.empty:
    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "📥 Export als CSV",
        data=filtered.to_csv(index=False),
        file_name="JDivine_Teamwear_Filter.csv",
        mime="text/csv"
    )
else:
    st.warning("🚫 Keine Ergebnisse für die aktuelle Filterauswahl.")

# Basisstruktur der Kategorien und Unterkategorien für Top-Listen
top_categories = {
    "Empfehlungen von JDivine": [],
    "Top 10 Marken": "data/top_10_marken.csv",
    "Top 10 T-Shirts": "data/top_10_tshirts.csv",
    "Top 10 Hoodies": "data/top_10_hoodies.csv",
    "Top 10 Poloshirts": "data/top_10_poloshirts.csv",
    "Top 10 Pullover": "data/top_10_pullover.csv",
    "Top 10 Jacken": "data/top_10_jacken.csv",
    "Top 10 Anwendungsbereich": {
        "Top 10 Alltag": "data/top_10_alltag.csv",
        "Top 10 Firma, Seriosität": "data/top_10_firma.csv",
        "Top 10 Umwelt": "data/top_10_umwelt.csv",
        "Top 10 Sport": "data/top_10_sport.csv",
        "Top 10 Freizeit": "data/top_10_freizeit.csv"
    }
}

# Platzhalter-CSVs mit den Spalten, die später von dir befüllt werden sollen
columns = [
    "Platz", "Produkt", "Marke", "EK-Preis (€)", "VK-Preis (€)",
    "Versand (€)", "Druckart", "Farbe(n)", "Größe(n)", "Anwendungsbereich"
]

# CSV-Dateien mit Platzhalter erstellen
os.makedirs("data", exist_ok=True)
for key, value in top_categories.items():
    if isinstance(value, str):
        df = pd.DataFrame(columns=columns)
        df.to_csv(value, index=False)
    elif isinstance(value, dict):
        for subkey, subpath in value.items():
            df = pd.DataFrame(columns=columns)
            df.to_csv(subpath, index=False)

# Rückmeldung
sorted_files = sorted(os.listdir("data"))
sorted_files
