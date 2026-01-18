import pandas as pd
import numpy as np
import os
from data_loader import load_all
from anomaly_detector import detect_ghosts

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.getcwd()))
RESULTS_DIR = os.path.join(BASE_DIR, "analysis", "results")

def deep_dive():
    print("Initializing Deep Dive Analysis...")
    
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    # 1. Load All Datasets
    bio, demo, enrol = load_all()
    if enrol.empty or demo.empty:
        print("Data Loading Error: Datasets are empty. Verify data source paths.")
        return

    print(f"Data ingestion complete. Enrolment: {len(enrol)}, Demographic: {len(demo)}, Biometric: {len(bio)}")

    # 2. Generate District Profile (Aggregation)
    def group_df(df, prefix):
        numeric = df.select_dtypes(include=[np.number]).columns
        cols = [c for c in numeric if c != 'pincode']
        return df.groupby(['state', 'district'])[cols].sum().add_prefix(prefix)

    b_grp = group_df(bio, "bio_")
    d_grp = group_df(demo, "demo_")
    e_grp = group_df(enrol, "enrol_")
    
    profile = e_grp.join(d_grp, how='outer').join(b_grp, how='outer').fillna(0).reset_index()
    profile_path = os.path.join(RESULTS_DIR, "district_profile.csv")
    profile.to_csv(profile_path, index=False)
    print(f"Regional profile preserved at {profile_path}")

    # 3. Detect Ghost Districts and Scored Profile
    ghosts, processed_df = detect_ghosts(profile)
    
    # 4. State Performance Ranking
    state_stats = processed_df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum'
    }).reset_index()
    
    state_stats['update_rate'] = (state_stats['total_updates'] / (state_stats['total_enrol'] + 1)) * 100
    
    # Count Ghosts per state
    ghost_counts = ghosts.groupby('state').size().reset_index(name='ghost_count')
    state_stats = state_stats.merge(ghost_counts, on='state', how='left').fillna(0)
    
    print("\nSTATE PERFORMANCE RANKING (TOP 5):")
    print(state_stats.sort_values('update_rate', ascending=False).head(5)[['state', 'update_rate', 'ghost_count']])
    
    print("\nBOTTOM 5 STATES (BY GHOST COUNT):")
    print(state_stats.sort_values('ghost_count', ascending=False).head(5)[['state', 'update_rate', 'ghost_count']])

    # 5. Age Group Spikes (from raw enrolment)
    enrol['month'] = enrol['date'].dt.month
    enrol['month_name'] = enrol['date'].dt.month_name()
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    age_monthly = enrol.groupby(['month', 'month_name'])[age_cols].sum().reset_index()
    
    print("\nAGE GROUP MONTHLY PEAKS:")
    for col in age_cols:
        peak_idx = age_monthly[col].idxmax()
        peak_m = age_monthly.loc[peak_idx, 'month_name']
        peak_v = age_monthly[col].max()
        print(f"Group {col}: Peak Month {peak_m}, Volume {peak_v:,.0f}")

    # 6. Statistical Anomaly Flagging (|Z| > 2.0)
    high_outliers = processed_df[processed_df['update_zscore'] > 2.0].sort_values('update_zscore', ascending=False)
    low_outliers = processed_df[processed_df['update_zscore'] < -2.0].sort_values('update_zscore', ascending=True)
    
    print("\nHIGH INTENSITY ANOMALIES (|Z| > 2.0):")
    print(high_outliers.head(5)[['district', 'state', 'update_zscore', 'update_intensity']])
    
    print("\nLOW INTENSITY ANOMALIES (|Z| < -2.0):")
    print(low_outliers.head(5)[['district', 'state', 'update_zscore', 'update_intensity']])

    # Persist results for report generation
    state_stats.to_csv(os.path.join(RESULTS_DIR, 'state_results.csv'), index=False)
    processed_df.to_csv(os.path.join(RESULTS_DIR, 'district_anomalies.csv'), index=False)
    age_monthly.to_csv(os.path.join(RESULTS_DIR, 'age_trends.csv'), index=False)
    print("\nAnalysis results stored in: analysis/results/")

if __name__ == "__main__":
    deep_dive()
