import pandas as pd
import numpy as np
import data_loader
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis", "results")

def process_daily_trends(bio, demo, enrol):
    print("Generating Daily Trends...")
    
    # Resample only numeric columns to Daily sum
    # We must ensure 'date' is index
    
    bio_daily = bio.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('bio_')
    demo_daily = demo.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('demo_')
    enrol_daily = enrol.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('enrol_')
    
    # Merge all
    daily = pd.concat([enrol_daily, demo_daily, bio_daily], axis=1).fillna(0)
    
    daily.to_csv(os.path.join(OUTPUT_DIR, "daily_trends.csv"))
    print(f"Saved {os.path.join(OUTPUT_DIR, 'daily_trends.csv')}")
    return daily

def process_district_profile(bio, demo, enrol):
    print("Generating District Profiles...")
    
    # Group by State and District
    # We use a custom cleaner for district names if needed, but for now we aggregate raw
    
    def group_df(df, prefix):
        # drop pincode before grouping if it causes issues, or sum it (pincode sum is meaningless, so drop or ignore)
        numeric = df.select_dtypes(include=[np.number]).columns
        cols = [c for c in numeric if c != 'pincode']
        return df.groupby(['state', 'district'])[cols].sum().add_prefix(prefix)

    b_grp = group_df(bio, "bio_")
    d_grp = group_df(demo, "demo_")
    e_grp = group_df(enrol, "enrol_")
    
    # Outer join to capture all districts even if missing in one dataset
    profile = e_grp.join(d_grp, how='outer').join(b_grp, how='outer').fillna(0)
    
    # Add Derived Metrics
    # Efficiency: Bio Updates per Enrolment (is this meaningful? maybe not directly, but ratio helps)
    # Intensity: Total Updates (Bio + Demo) / Enrolment (Proxy for "Activity per new user" - meaningless if stock exceeds flow)
    # Better: Absolute numbers are key here.
    
    profile.to_csv(os.path.join(OUTPUT_DIR, "district_profile.csv"))
    print(f"Saved {os.path.join(OUTPUT_DIR, 'district_profile.csv')}")
    return profile

def analyze_correlations(daily_trends):
    print("Analyzing Correlations...")
    corr = daily_trends.corr()
    corr.to_csv(os.path.join(OUTPUT_DIR, "correlations.csv"))
    print(f"Saved {os.path.join(OUTPUT_DIR, 'correlations.csv')}")

def main():
    bio, demo, enrol = data_loader.load_all()
    
    daily = process_daily_trends(bio, demo, enrol)
    process_district_profile(bio, demo, enrol)
    analyze_correlations(daily)

if __name__ == "__main__":
    main()
