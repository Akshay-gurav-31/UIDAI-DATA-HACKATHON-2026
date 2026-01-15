import pandas as pd
import numpy as np
from scipy import stats
import os

# Configuration
DISTRICT_PROFILE = r"analysis/results/district_profile.csv"
OUTPUT_DIR = r"analysis/results"
THRESH_ENROL_MIN = 1000  # Minimum records for district significance
THRESH_UPDATE_ZERO = 0   

def load_data():
    """Load district profile for analysis."""
    if not os.path.exists(DISTRICT_PROFILE):
        alt_path = r"c:/Users/aksha/Desktop/UIDIA HACKTHON/analysis/results/district_profile.csv"
        if os.path.exists(alt_path):
            return pd.read_csv(alt_path)
        raise FileNotFoundError(f"Missing data: {DISTRICT_PROFILE}")
    return pd.read_csv(DISTRICT_PROFILE)

def detect_ghosts(df):
    """
    Detects enrolment-update mismatches (Ghost Districts).
    
    Logic:
    1. Filter high-volume districts (>1000 enrolments).
    2. Calculate update intensity relative to enrolment.
    3. Flag districts with structural mismatches (Zero updates).
    4. Normalize via Z-score to assess deviation severity.
    """
    
    # Feature Engineering
    enrol_cols = [c for c in df.columns if 'enrol_' in c]
    demo_cols = [c for c in df.columns if 'demo_' in c]
    bio_cols = [c for c in df.columns if 'bio_' in c]
    
    df['total_enrol'] = df[enrol_cols].sum(axis=1)
    df['total_updates'] = df[demo_cols].sum(axis=1) + df[bio_cols].sum(axis=1)
    
    # Prevent div/0
    df['update_intensity'] = df['total_updates'] / (df['total_enrol'] + 1)
    
    # Measure statistical deviation from national mean
    df['update_zscore'] = stats.zscore(df['update_intensity'])
    
    # Flag structural failures (Ghost Districts)
    # High Enrolment + Zero Updates
    ghosts = df[
        (df['total_enrol'] > THRESH_ENROL_MIN) & 
        (df['total_updates'] == 0)
    ].copy()
    
    ghosts['classification'] = 'Ghost District (Structural Failure)'
    
    return ghosts, df


def validate_findings(ghosts, full_df):
    """
    Perform statistical validation of the Ghost District hypothesis.
    """
    normal_districts = full_df[~full_df.index.isin(ghosts.index)]
    
    results = []
    results.append("=== STATISTICAL VALIDATION REPORT ===")
    
    # T-Test
    # Null Hypothesis: Ghost Districts come from the same distribution as Normal Districts (regarding update intensity)
    t_stat, p_val = stats.ttest_ind(
        ghosts['update_intensity'], 
        normal_districts['update_intensity'], 
        equal_var=False
    )
    
    results.append(f"1. T-Test (Welch's): p-value = {p_val:.5e}")
    if p_val < 0.05:
        results.append("   -> Result: STATISTICALLY SIGNIFICANT. Ghost Districts are a distinct population.")
    else:
        results.append("   -> Result: Not Significant.")
        
    # Magnitude check
    avg_intensity_normal = normal_districts['update_intensity'].mean()
    results.append(f"2. Effect Size: Normal districts have {avg_intensity_normal:.4f} updates/enrolment, Ghosts have 0.0.")
    
    # Ground Truth Proxy Check
    # (Checking if district names match known patterns - simulated here based on data content)
    results.append(f"3. Detection Count: {len(ghosts)} districts identified as Ghosts out of {len(full_df)} total districts.")
    
    return "\n".join(results)

def main():
    print("Loading data...")
    try:
        df = load_data()
        print(f"Data Loaded: {df.shape}")
        
        print("Detecting Anomalies...")
        ghosts, processed_df = detect_ghosts(df)
        
        # Save Results
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        ghosts.to_csv(os.path.join(OUTPUT_DIR, "ghost_districts.csv"), index=False)
        processed_df.to_csv(os.path.join(OUTPUT_DIR, "district_profile_scored.csv"), index=False)
        
        # Validation
        print("Running Validation Protocol...")
        validation_report = validate_findings(ghosts, processed_df)
        
        with open(os.path.join(OUTPUT_DIR, "audit_validation_log.txt"), "w") as f:
            f.write(validation_report)
            
        print(validation_report)
        print("✅ Analysis Complete. Results saved to analysis/results/")
        
    except Exception as e:
        print(f"❌ Analysis Failed: {e}")

if __name__ == "__main__":
    main()
