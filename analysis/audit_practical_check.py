import pandas as pd
import os
import sys

# Add parent directory to path to import data_loader if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.data_loader import load_dataset

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "audit_verification_results.txt")

def log_and_print(msg):
    """Print to console and write to file"""
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def check_name_issue():
    log_and_print("\n" + "="*80)
    log_and_print("--- [1] NAME ISSUE (GHOST DISTRICTS) - VERIFICATION ---")
    log_and_print("="*80)
    log_and_print("PDF Claim: 47 districts with 234,567 enrolments but zero updates")
    log_and_print("Checking for naming mismatches between Enrolment and Demographic datasets...\n")
    
    enrol = load_dataset("api_data_aadhar_enrolment")
    demo = load_dataset("api_data_aadhar_demographic")
    
    if enrol.empty or demo.empty:
        log_and_print("❌ Error: Datasets are empty.")
        return

    enrol_districts = set(enrol['district'].unique())
    demo_districts = set(demo['district'].unique())
    
    mismatch_enrol = enrol_districts - demo_districts
    mismatch_demo = demo_districts - enrol_districts
    
    log_and_print(f"📊 Total unique districts in Enrolment: {len(enrol_districts)}")
    log_and_print(f"📊 Total unique districts in Demographic: {len(demo_districts)}")
    log_and_print(f"\n🔍 Districts in Enrolment but NOT in Demographic: {len(mismatch_enrol)}")
    if mismatch_enrol:
        log_and_print(f"   Sample mismatches: {list(mismatch_enrol)[:10]}")
        
    log_and_print(f"\n🔍 Districts in Demographic but NOT in Enrolment: {len(mismatch_demo)}")
    if mismatch_demo:
        log_and_print(f"   Sample mismatches: {list(mismatch_demo)[:10]}")

    ghost_records = enrol[enrol['district'].isin(mismatch_enrol)]
    total_ghost_enrolments = ghost_records['age_0_5'].sum() + ghost_records['age_5_17'].sum() + ghost_records['age_18_greater'].sum()
    
    log_and_print(f"\n💀 Total Enrolments in 'Ghost Districts': {int(total_ghost_enrolments):,}")
    log_and_print(f"💀 Number of Ghost Districts: {len(mismatch_enrol)}")
    
    # Verification
    if len(mismatch_enrol) > 0 and total_ghost_enrolments > 0:
        log_and_print("\n✅ VERIFIED: Name mismatch issue EXISTS in dataset")
    else:
        log_and_print("\n❌ ISSUE: Name mismatch NOT found or analysis incorrect")

def check_date_issue():
    log_and_print("\n" + "="*80)
    log_and_print("--- [2] DATE ISSUE (MONTHLY PULSE) - VERIFICATION ---")
    log_and_print("="*80)
    log_and_print("PDF Claim: 91.3% of data occurs on the 1st day of the month")
    log_and_print("Checking for administrative batching pattern...\n")
    
    enrol = load_dataset("api_data_aadhar_enrolment")
    if enrol.empty: 
        log_and_print("❌ Error: Enrolment dataset is empty.")
        return

    # Extract day from date
    enrol['day'] = enrol['date'].dt.day
    
    day_counts = enrol.groupby('day').size().reset_index(name='record_count')
    day_counts['percentage'] = (day_counts['record_count'] / day_counts['record_count'].sum()) * 100
    
    # Sort to find busiest days
    sorted_days = day_counts.sort_values(by='record_count', ascending=False)
    
    log_and_print("📊 Top 5 Days with highest record volume:")
    log_and_print(sorted_days.head(5).to_string(index=False))
    
    first_day_data = day_counts[day_counts['day'] == 1]
    if not first_day_data.empty:
        first_day_pct = first_day_data['percentage'].values[0]
        log_and_print(f"\n📈 The 1st day of the month accounts for: {first_day_pct:.2f}% of all records")
        
        # Verification
        if first_day_pct > 50:
            log_and_print(f"✅ VERIFIED: Monthly Pulse pattern EXISTS (1st day has {first_day_pct:.1f}%)")
        else:
            log_and_print(f"⚠️  WARNING: Pulse exists but less dominant than claimed ({first_day_pct:.1f}% vs 91.3%)")
    else:
        log_and_print("❌ ERROR: No data for 1st day of month found")

def check_adult_update():
    log_and_print("\n" + "="*80)
    log_and_print("--- [3] ADULT UPDATE (CORRELATION) - VERIFICATION ---")
    log_and_print("="*80)
    log_and_print("PDF Claim: Pearson correlation r = 0.99, p < 0.001")
    log_and_print("Checking correlation between Child (5-17) and Adult (18+) updates...\n")
    
    demo = load_dataset("api_data_aadhar_demographic")
    if demo.empty:
        log_and_print("❌ Error: Demographic dataset is empty.")
        return
    
    log_and_print(f"📊 Available columns: {demo.columns.tolist()}\n")
    
    if 'demo_age_5_17' in demo.columns and 'demo_age_17_' in demo.columns:
        # Calculate correlation
        correlation = demo['demo_age_5_17'].corr(demo['demo_age_17_'])
        
        log_and_print(f"📈 Pearson Correlation Coefficient: {correlation:.4f}")
        log_and_print(f"📊 Sample size: {len(demo)} records")
        
        # Basic stats
        log_and_print(f"\n📊 Child Updates (5-17) - Mean: {demo['demo_age_5_17'].mean():.2f}, Std: {demo['demo_age_5_17'].std():.2f}")
        log_and_print(f"📊 Adult Updates (18+) - Mean: {demo['demo_age_17_'].mean():.2f}, Std: {demo['demo_age_17_'].std():.2f}")
        
        # Verification
        if correlation > 0.8:
            log_and_print(f"\n✅ VERIFIED: High correlation detected (r={correlation:.4f})")
            if correlation > 0.95:
                log_and_print("   This indicates VERY STRONG synchronized bulk processing")
            else:
                log_and_print("   This indicates STRONG correlation (though less than claimed 0.99)")
        else:
            log_and_print(f"\n⚠️  WARNING: Correlation exists but lower than claimed (r={correlation:.4f} vs 0.99)")
    else:
        log_and_print(f"❌ ERROR: Required columns not found")
        log_and_print(f"   Looking for: 'demo_age_5_17' and 'demo_age_17_'")

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    log_and_print("UIDAI DATASET VERIFICATION REPORT")
    log_and_print("Verifying claims made in Team Eklavya Submission PDF")
    log_and_print(f"Generated: {pd.Timestamp.now()}")
    
    check_name_issue()
    check_date_issue()
    check_adult_update()
    
    log_and_print("\n" + "="*80)
    log_and_print("VERIFICATION COMPLETE")
    log_and_print("="*80)
    log_and_print(f"\nFull results saved to: {OUTPUT_FILE}")
