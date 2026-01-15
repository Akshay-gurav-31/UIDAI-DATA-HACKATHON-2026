import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis.data_loader import load_dataset

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "monthly_pulse_verification.txt")

def log_and_print(msg):
    """Print to console and write to file"""
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def check_pulse_in_dataset(dataset_name, df):
    """Check for Monthly Pulse pattern in a given dataset"""
    log_and_print(f"\n{'='*80}")
    log_and_print(f"Checking Monthly Pulse in: {dataset_name}")
    log_and_print(f"{'='*80}")
    
    if df.empty:
        log_and_print(f"❌ Dataset is empty")
        return
    
    log_and_print(f"📊 Total records: {len(df):,}")
    log_and_print(f"📊 Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Extract day from date
    df['day'] = df['date'].dt.day
    
    # Group by day
    day_counts = df.groupby('day').size().reset_index(name='record_count')
    day_counts['percentage'] = (day_counts['record_count'] / day_counts['record_count'].sum()) * 100
    
    # Sort by record count
    sorted_days = day_counts.sort_values(by='record_count', ascending=False)
    
    log_and_print(f"\n📊 Top 10 Days with highest record volume:")
    log_and_print(sorted_days.head(10).to_string(index=False))
    
    # Check 1st day specifically
    first_day_data = day_counts[day_counts['day'] == 1]
    if not first_day_data.empty:
        first_day_pct = first_day_data['percentage'].values[0]
        first_day_count = first_day_data['record_count'].values[0]
        log_and_print(f"\n📈 1st day of month:")
        log_and_print(f"   - Records: {first_day_count:,}")
        log_and_print(f"   - Percentage: {first_day_pct:.2f}%")
        
        if first_day_pct > 80:
            log_and_print(f"✅ STRONG PULSE DETECTED! (1st day has {first_day_pct:.1f}%)")
            return True
        elif first_day_pct > 50:
            log_and_print(f"⚠️  MODERATE PULSE (1st day has {first_day_pct:.1f}%)")
            return True
        else:
            log_and_print(f"❌ NO SIGNIFICANT PULSE (1st day has only {first_day_pct:.1f}%)")
            return False
    else:
        log_and_print("❌ No data for 1st day of month")
        return False

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    log_and_print("="*80)
    log_and_print("MONTHLY PULSE VERIFICATION - ALL DATASETS")
    log_and_print("="*80)
    log_and_print(f"Generated: {pd.Timestamp.now()}")
    log_and_print(f"PDF Claim: 91.3% of data occurs on the 1st day of the month")
    
    # Load all datasets
    log_and_print("\n📂 Loading datasets...")
    enrol = load_dataset("api_data_aadhar_enrolment")
    demo = load_dataset("api_data_aadhar_demographic")
    bio = load_dataset("api_data_aadhar_biometric")
    
    # Check each dataset
    results = {}
    results['Enrolment'] = check_pulse_in_dataset("ENROLMENT Dataset", enrol)
    results['Demographic'] = check_pulse_in_dataset("DEMOGRAPHIC Dataset", demo)
    results['Biometric'] = check_pulse_in_dataset("BIOMETRIC Dataset", bio)
    
    # Final summary
    log_and_print("\n" + "="*80)
    log_and_print("FINAL SUMMARY")
    log_and_print("="*80)
    
    pulse_found = False
    for dataset, has_pulse in results.items():
        status = "✅ PULSE FOUND" if has_pulse else "❌ NO PULSE"
        log_and_print(f"{dataset}: {status}")
        if has_pulse:
            pulse_found = True
    
    if pulse_found:
        log_and_print("\n✅ Monthly Pulse pattern VERIFIED in at least one dataset")
    else:
        log_and_print("\n❌ Monthly Pulse pattern NOT FOUND in any dataset")
        log_and_print("⚠️  PDF claim cannot be verified with current data")
    
    log_and_print(f"\nFull results saved to: {OUTPUT_FILE}")
