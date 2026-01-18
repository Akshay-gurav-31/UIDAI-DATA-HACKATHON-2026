import pandas as pd
import numpy as np
import data_loader
import os

# Configuration for directory structure
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis", "results")

def process_daily_trends(bio, demo, enrol):
    """Aggregates multi-source datasets into a unified daily time-series."""
    print("Generating Daily Unified Trends...")
    
    # Resample numeric columns to daily sums
    bio_daily = bio.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('bio_')
    demo_daily = demo.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('demo_')
    enrol_daily = enrol.set_index('date').select_dtypes(include=[np.number]).resample('D').sum().add_prefix('enrol_')
    
    # Consolidate and fill missing temporal indices
    daily = pd.concat([enrol_daily, demo_daily, bio_daily], axis=1).fillna(0)
    
    output_path = os.path.join(OUTPUT_DIR, "daily_trends.csv")
    daily.to_csv(output_path)
    print(f"Daily trends persisted to {output_path}")
    return daily

def process_district_profile(bio, demo, enrol):
    """Generates comprehensive district-level profiles across all update types."""
    print("Generating Regional District Profiles...")
    
    def group_df(df, prefix):
        # Filter for numeric data, excluding non-aggregatable identifiers like pincode
        numeric = df.select_dtypes(include=[np.number]).columns
        cols = [c for c in numeric if c != 'pincode']
        return df.groupby(['state', 'district'])[cols].sum().add_prefix(prefix)

    b_grp = group_df(bio, "bio_")
    d_grp = group_df(demo, "demo_")
    e_grp = group_df(enrol, "enrol_")
    
    # Outer join to ensure inclusive regional coverage
    profile = e_grp.join(d_grp, how='outer').join(b_grp, how='outer').fillna(0)
    
    output_path = os.path.join(OUTPUT_DIR, "district_profile.csv")
    profile.to_csv(output_path)
    print(f"Regional profiles persisted to {output_path}")
    return profile

def analyze_correlations(daily_trends):
    """Calculates Pearson correlation coefficients across transaction indices."""
    print("Executing Transactional Correlation Analysis...")
    corr = daily_trends.corr()
    output_path = os.path.join(OUTPUT_DIR, "correlations.csv")
    corr.to_csv(output_path)
    print(f"Correlation matrix persisted to {output_path}")

def main():
    """Execution entry point for the data aggregation pipeline."""
    try:
        bio, demo, enrol = data_loader.load_all()
        daily = process_daily_trends(bio, demo, enrol)
        process_district_profile(bio, demo, enrol)
        analyze_correlations(daily)
        print("Data processing pipeline completed successfully.")
    except Exception as e:
        print(f"Pipeline Execution Error: {e}")

if __name__ == "__main__":
    main()
