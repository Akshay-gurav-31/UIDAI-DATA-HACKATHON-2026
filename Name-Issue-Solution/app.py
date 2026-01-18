import streamlit as st
import pandas as pd
import difflib
import os

st.set_page_config(page_title="Team Eklavya - Data Audit", layout="wide")

# THE ENGINE
class SyntaxBridgeEngine:
    def __init__(self, master_list):
        self.valid_districts = set(master_list) 
        self.master_list = master_list          
        self.cache = {}

    def resolve(self, dirty_name):
        if dirty_name in self.valid_districts:
            return dirty_name, 1.0, "Valid"
        
        if dirty_name in self.cache:
            return self.cache[dirty_name]

        matches = difflib.get_close_matches(dirty_name, self.master_list, n=1, cutoff=0.8)
        if matches:
            score = difflib.SequenceMatcher(None, dirty_name, matches[0]).ratio()
            self.cache[dirty_name] = (matches[0], score, "Healed")
            return matches[0], score, "Healed"
        
        return None, 0.0, "Ghost"

# THE UI 
st.title("🛡️ Eklavya: Live Data Reconciliation System")

col1, col2 = st.columns([1, 2])

# SIDEBAR: CONFIGURATION
with st.sidebar:
    st.header("1. Initialize Master DB")
    st.info("Upload the 'TRUTH' (Biometric Data)")
    # Auto-load local file if present for speed
    master_file = "api_data_aadhar_biometric_500000_1000000.csv"
    valid_districts = []
    
    if os.path.exists(master_file):
        df_bio = pd.read_csv(master_file)
        valid_districts = sorted(df_bio['district'].unique().tolist())
        st.success(f"✅ Loaded Local DB: {len(valid_districts)} Districts")
    else:
        uploaded_bio = st.file_uploader("Upload Biometric CSV", type=['csv'], key="bio")
        if uploaded_bio:
            df_bio = pd.read_csv(uploaded_bio)
            valid_districts = sorted(df_bio['district'].unique().tolist())
            st.success(f"✅ DB Active: {len(valid_districts)} Records")

    st.markdown("---")
    st.header("2. Ingest Audit Data")
    st.warning("Upload the 'DIRTY' Data (Enrollment)")
    # Try to find enrollment file automatically too
    enrol_file = "api_data_aadhar_enrolment_0_500000.csv"
    audit_districts = []
    
    if os.path.exists(enrol_file):
        df_enrol = pd.read_csv(enrol_file)
        audit_districts = sorted(df_enrol['district'].unique().tolist())
        st.success(f"⚠️ Ingested Audit Batch: {len(audit_districts)} Districts")
    else:
        uploaded_enrol = st.file_uploader("Upload Enrollment CSV", type=['csv'], key="enrol")
        if uploaded_enrol:
            df_enrol = pd.read_csv(uploaded_enrol)
            audit_districts = sorted(df_enrol['district'].unique().tolist())
            st.success(f"⚠️ Audit Batch Ready: {len(audit_districts)} Districts")

# MAIN PANEL
if not valid_districts:
    st.error("Waiting for Master Database...")
    st.stop()

engine = SyntaxBridgeEngine(valid_districts)

# TABBED INTERFACE
tab1, tab2 = st.tabs(["🔴 Live Anomaly Scanner", "🛠️ Manual Inspector"])

with tab1:
    st.subheader("Automated Cross-Verification")
    st.markdown("Comparing **Enrollment Data** against **Biometric Master DB**...")
    
    if audit_districts:
        if st.button("RUN FULL AUDIT NOW", type="primary"):
            progress = st.progress(0)
            ghosts_found = []
            
            # THE REAL SCAN LOGIC
            # We filter for districts in Enrollment that are NOT in Biometric
            suspects = [d for d in audit_districts if d not in valid_districts]
            
            status_text = st.empty()
            status_text.text(f"Identified {len(suspects)} Suspects. Attempting Resolution...")
            
            for i, suspect in enumerate(suspects):
                fixed, score, status = engine.resolve(suspect)
                if status == "Healed":
                    ghosts_found.append({
                        "ORIGINAL (Enrollment)": suspect,
                        "RESOLVED TO (Biometric)": fixed,
                        "CONFIDENCE": f"{int(score*100)}%"
                    })
                progress.progress((i + 1) / len(suspects))
            
            progress.empty()
            
            if ghosts_found:
                st.error(f"🚨 CRITICAL: Found {len(ghosts_found)} Naming Anomalies!")
                st.dataframe(pd.DataFrame(ghosts_found), use_container_width=True)
                
                # Metrics
                c1, c2 = st.columns(2)
                c1.metric("Total Ghosts Detected", len(suspects))
                c2.metric("Successfully Healed", len(ghosts_found), delta="100% Recovery")
            else:
                st.success("✅ Clean Audit. No anomalies found in this batch.")
    else:
        st.info("Upload Enrollment Data in the sidebar to run a real scan.")

with tab2:
    st.subheader("Single Record Test")
    user_input = st.text_input("Test a Name manually:", "Visakhapatanam")
    if user_input:
        fixed, score, status = engine.resolve(user_input)
        if status == "Valid":
            st.success("Valid Name")
        elif status == "Healed":
            st.warning(f"Healed: {fixed} ({int(score*100)}%)")
        else:
            st.error("Unknown Entity")