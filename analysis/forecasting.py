import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Configuration for export directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_DIR = os.path.join(BASE_DIR, "final_submission", "images")

def run_forecast():
    """Executes a predictive trend analysis for Aadhaar enrolment throughput."""
    # Ingest monthly stats from the temporal analysis module
    from analyze_monthly_trends import analyze_monthly_enrollment
    monthly_stats = analyze_monthly_enrollment()
    
    if monthly_stats is None:
        print("Error: Predictive model dependency (temporal analysis) returned null.")
        return

    # Temporal sequencing for time-series modeling
    data = monthly_stats['total_enrol'].values
    x = np.arange(len(data))
    
    # Linear Regression (Ordinary Least Squares) for trend estimation
    z = np.polyfit(x, data, 1)
    p = np.poly1d(z)
    
    # Projection window: Next 6 fiscal periods
    future_x = np.arange(12, 18)
    forecast_mean = p(future_x)
    
    # Statistical uncertainty estimation (Residual Standard Error)
    residuals = data - p(x)
    std_error = np.std(residuals)
    
    # Projection Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_stats['month_name'], data, label='Historical Observation (2024-25)', marker='o', color='#2C3E50', linewidth=2)
    
    future_months = ['Jan-26', 'Feb-26', 'Mar-26', 'Apr-26', 'May-26', 'Jun-26']
    plt.plot(future_months, forecast_mean, label='Predictive Trend (2026)', linestyle='--', marker='s', color='#E74C3C')
    plt.fill_between(future_months, forecast_mean - 2*std_error, forecast_mean + 2*std_error, color='#E74C3C', alpha=0.15, label='95% Predictive Interval')
    
    plt.title('Aadhaar Enrolment Forecasting (90-Day Predictive Model)', fontsize=14, fontweight='bold')
    plt.ylabel('Transactional Throughput')
    plt.xlabel('Fiscal Month')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    output_path = os.path.join(IMAGE_DIR, 'enrollment_forecast.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Predictive visualization exported to {output_path}")

if __name__ == "__main__":
    run_forecast()

if __name__ == "__main__":
    run_forecast()
