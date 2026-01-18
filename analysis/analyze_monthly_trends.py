import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analysis.data_loader import load_dataset

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "monthly_enrollment_analysis.txt")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'final_submission', 'images')

def log_and_print(msg):
    """Broadcasts message to console and audit log file."""
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def analyze_monthly_enrollment():
    """Executes a diagnostic analysis of monthly enrolment cycles."""
    log_and_print("="*80)
    log_and_print("TEMPORAL ENROLMENT CYCLES: AUDIT REPORT")
    log_and_print("="*80)
    log_and_print(f"Audit Timestamp: {pd.Timestamp.now()}\n")
    
    # Dataset Ingestion
    log_and_print("Ingesting Enrolment Transaction Registry...")
    enrol = load_dataset("api_data_aadhar_enrolment")
    
    if enrol.empty:
        log_and_print("ERROR: Ingestion failed - Enrolment dataset is null.")
        return None
    
    log_and_print(f"Total Transaction Volume: {len(enrol):,}")
    log_and_print(f"Audit Window: {enrol['date'].min()} to {enrol['date'].max()}\n")
    
    # Feature Derivation
    enrol['month'] = enrol['date'].dt.month
    enrol['month_name'] = enrol['date'].dt.strftime('%B')
    enrol['year'] = enrol['date'].dt.year
    enrol['total_enrol'] = enrol['age_0_5'] + enrol['age_5_17'] + enrol['age_18_greater']
    
    # Regional and Temporal Aggregation
    monthly_stats = enrol.groupby(['month', 'month_name']).agg({
        'total_enrol': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'district': 'nunique'
    }).reset_index()
    
    monthly_stats = monthly_stats.sort_values('month')
    monthly_stats['percentage'] = (monthly_stats['total_enrol'] / monthly_stats['total_enrol'].sum()) * 100
    
    log_and_print("="*80)
    log_and_print("TEMPORAL DISTRIBUTION SUMMARY")
    log_and_print("="*80)
    log_and_print(monthly_stats[['month_name', 'total_enrol', 'percentage', 'district']].to_string(index=False))
    
    # Identification of Extremes
    peak_month = monthly_stats.loc[monthly_stats['total_enrol'].idxmax()]
    low_month = monthly_stats.loc[monthly_stats['total_enrol'].idxmin()]
    
    log_and_print(f"\nPEAK PERFORMANCE MONTH: {peak_month['month_name']}")
    log_and_print(f"   - Transaction Throughput: {int(peak_month['total_enrol']):,}")
    log_and_print(f"   - Relative Volume: {peak_month['percentage']:.2f}%")
    log_and_print(f"   - Active Regional Entities: {int(peak_month['district'])}")
    
    log_and_print(f"\nMINIMUM THROUGHPUT MONTH: {low_month['month_name']}")
    log_and_print(f"   - Transaction Throughput: {int(low_month['total_enrol']):,}")
    log_and_print(f"   - Relative Volume: {low_month['percentage']:.2f}%")
    log_and_print(f"   - Active Regional Entities: {int(low_month['district'])}")
    
    # Cohort Analysis
    log_and_print("\n" + "="*80)
    log_and_print("DEMOGRAPHIC COHORT DRIFT BY PERIOD")
    log_and_print("="*80)
    
    age_analysis = monthly_stats[['month_name', 'age_0_5', 'age_5_17', 'age_18_greater']].copy()
    age_analysis['dominant_segment'] = age_analysis[['age_0_5', 'age_5_17', 'age_18_greater']].idxmax(axis=1)
    
    log_and_print(age_analysis.to_string(index=False))
    
    # Statistical Insights
    log_and_print("\n" + "="*80)
    log_and_print("STATISTICAL OBSERVATIONS")
    log_and_print("="*80)
    
    variance = monthly_stats['total_enrol'].std() / monthly_stats['total_enrol'].mean() * 100
    log_and_print(f"Coefficient of Transactional Variation: {variance:.2f}%")
    
    if variance > 30:
        log_and_print("Observation: Significant seasonal variance detected in regional throughput.")
    else:
        log_and_print("Observation: Moderate temporal stability in enrolment patterns.")
    
    # Temporal Parity Check
    first_half = monthly_stats[monthly_stats['month'] <= 6]['total_enrol'].sum()
    second_half = monthly_stats[monthly_stats['month'] > 6]['total_enrol'].sum()
    
    log_and_print(f"\nH1 Performance (Jan-Jun): {int(first_half):,} transactions")
    log_and_print(f"H2 Performance (Jul-Dec): {int(second_half):,} transactions")
    
    log_and_print(f"\nFull audit log available at: {OUTPUT_FILE}")
    
    return monthly_stats

def create_visualization(monthly_stats):
    """Generates high-resolution visualization for temporal trends."""
    if monthly_stats is None:
        return
    
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Enrolment Trajectory
    ax1.bar(monthly_stats['month_name'], monthly_stats['total_enrol'], 
            color='#2C3E50', alpha=0.8, edgecolor='black')
    ax1.set_title("Temporal Enrolment Trajectory - UIDAI Ecosystem", 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel("Transaction Throughput", fontweight='bold', fontsize=12)
    ax1.set_xlabel("Registration Month", fontweight='bold', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    
    for i, (idx, row) in enumerate(monthly_stats.iterrows()):
        ax1.text(i, row['total_enrol'], f"{int(row['total_enrol']/1000)}K", 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Demographic Drift
    x = range(len(monthly_stats))
    width = 0.25
    
    ax2.bar([i - width for i in x], monthly_stats['age_0_5'], width, 
            label='Infant (0-5)', color='#3498DB', alpha=0.8)
    ax2.bar(x, monthly_stats['age_5_17'], width, 
            label='Juvenile (5-17)', color='#E74C3C', alpha=0.8)
    ax2.bar([i + width for i in x], monthly_stats['age_18_greater'], width, 
            label='Adult (18+)', color='#27AE60', alpha=0.8)
    
    ax2.set_title("Age Cohort Distribution Across Temporal Windows", 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel("Transactional Load", fontweight='bold', fontsize=12)
    ax2.set_xlabel("Registration month", fontweight='bold', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(monthly_stats['month_name'], rotation=45)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    output_path = os.path.join(IMAGE_DIR, 'monthly_enrollment_trends_v2.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualization asset exported to: {output_path}")

if __name__ == "__main__":
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    monthly_stats = analyze_monthly_enrollment()
    create_visualization(monthly_stats)

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    monthly_stats = analyze_monthly_enrollment()
    create_visualization(monthly_stats)
