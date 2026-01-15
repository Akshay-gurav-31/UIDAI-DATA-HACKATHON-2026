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
    """Print to console and write to file"""
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def analyze_monthly_enrollment():
    """Analyze monthly enrollment trends"""
    log_and_print("="*80)
    log_and_print("MONTHLY ENROLLMENT TRENDS ANALYSIS")
    log_and_print("="*80)
    log_and_print(f"Generated: {pd.Timestamp.now()}\n")
    
    # Load enrollment data
    log_and_print("📂 Loading Enrollment dataset...")
    enrol = load_dataset("api_data_aadhar_enrolment")
    
    if enrol.empty:
        log_and_print("❌ Error: Enrollment dataset is empty")
        return None
    
    log_and_print(f"📊 Total records: {len(enrol):,}")
    log_and_print(f"📊 Date range: {enrol['date'].min()} to {enrol['date'].max()}\n")
    
    # Create month column
    enrol['month'] = enrol['date'].dt.month
    enrol['month_name'] = enrol['date'].dt.strftime('%B')
    enrol['year'] = enrol['date'].dt.year
    
    # Calculate total enrollments per record
    enrol['total_enrol'] = enrol['age_0_5'] + enrol['age_5_17'] + enrol['age_18_greater']
    
    # Group by month
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
    log_and_print("MONTHLY ENROLLMENT DISTRIBUTION")
    log_and_print("="*80)
    log_and_print(monthly_stats[['month_name', 'total_enrol', 'percentage', 'district']].to_string(index=False))
    
    # Find peak and low months
    peak_month = monthly_stats.loc[monthly_stats['total_enrol'].idxmax()]
    low_month = monthly_stats.loc[monthly_stats['total_enrol'].idxmin()]
    
    log_and_print(f"\n📈 PEAK MONTH: {peak_month['month_name']}")
    log_and_print(f"   - Total Enrollments: {int(peak_month['total_enrol']):,}")
    log_and_print(f"   - Percentage: {peak_month['percentage']:.2f}%")
    log_and_print(f"   - Districts covered: {int(peak_month['district'])}")
    
    log_and_print(f"\n📉 LOWEST MONTH: {low_month['month_name']}")
    log_and_print(f"   - Total Enrollments: {int(low_month['total_enrol']):,}")
    log_and_print(f"   - Percentage: {low_month['percentage']:.2f}%")
    log_and_print(f"   - Districts covered: {int(low_month['district'])}")
    
    # Age group analysis
    log_and_print("\n" + "="*80)
    log_and_print("AGE GROUP DISTRIBUTION BY MONTH")
    log_and_print("="*80)
    
    age_analysis = monthly_stats[['month_name', 'age_0_5', 'age_5_17', 'age_18_greater']].copy()
    age_analysis['dominant_group'] = age_analysis[['age_0_5', 'age_5_17', 'age_18_greater']].idxmax(axis=1)
    
    log_and_print(age_analysis.to_string(index=False))
    
    # Key insights
    log_and_print("\n" + "="*80)
    log_and_print("KEY INSIGHTS")
    log_and_print("="*80)
    
    variance = monthly_stats['total_enrol'].std() / monthly_stats['total_enrol'].mean() * 100
    log_and_print(f"📊 Coefficient of Variation: {variance:.2f}%")
    
    if variance > 30:
        log_and_print("✅ SIGNIFICANT seasonal variation detected in enrollment patterns")
    else:
        log_and_print("⚠️  MODERATE seasonal variation in enrollment patterns")
    
    # Calculate trend
    first_half = monthly_stats[monthly_stats['month'] <= 6]['total_enrol'].sum()
    second_half = monthly_stats[monthly_stats['month'] > 6]['total_enrol'].sum()
    
    log_and_print(f"\n📊 First Half (Jan-Jun): {int(first_half):,} enrollments")
    log_and_print(f"📊 Second Half (Jul-Dec): {int(second_half):,} enrollments")
    
    if first_half > second_half:
        diff_pct = ((first_half - second_half) / second_half) * 100
        log_and_print(f"✅ First half shows {diff_pct:.1f}% MORE enrollments than second half")
    else:
        diff_pct = ((second_half - first_half) / first_half) * 100
        log_and_print(f"✅ Second half shows {diff_pct:.1f}% MORE enrollments than first half")
    
    log_and_print(f"\nFull results saved to: {OUTPUT_FILE}")
    
    return monthly_stats

def create_visualization(monthly_stats):
    """Create visualization for monthly trends"""
    if monthly_stats is None:
        return
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Monthly enrollment trend
    ax1.bar(monthly_stats['month_name'], monthly_stats['total_enrol'], 
            color='#2C3E50', alpha=0.8, edgecolor='black')
    ax1.set_title('Monthly Enrollment Trends - Aadhaar Registration Patterns', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Total Enrollments', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Month', fontweight='bold', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(monthly_stats.iterrows()):
        ax1.text(i, row['total_enrol'], f"{int(row['total_enrol']/1000)}K", 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Plot 2: Age group distribution
    x = range(len(monthly_stats))
    width = 0.25
    
    ax2.bar([i - width for i in x], monthly_stats['age_0_5'], width, 
            label='0-5 years', color='#3498DB', alpha=0.8)
    ax2.bar(x, monthly_stats['age_5_17'], width, 
            label='5-17 years', color='#E74C3C', alpha=0.8)
    ax2.bar([i + width for i in x], monthly_stats['age_18_greater'], width, 
            label='18+ years', color='#27AE60', alpha=0.8)
    
    ax2.set_title('Age Group Distribution Across Months', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('Enrollments', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Month', fontweight='bold', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(monthly_stats['month_name'], rotation=45)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    output_path = os.path.join(IMAGE_DIR, 'monthly_enrollment_trends_v2.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualization saved: {output_path}")

if __name__ == "__main__":
    # Clear previous results
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    monthly_stats = analyze_monthly_enrollment()
    create_visualization(monthly_stats)
