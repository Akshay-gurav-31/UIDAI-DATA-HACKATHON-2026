import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration for directory structure
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(BASE_DIR, "analysis", "results", "district_profile.csv")
IMAGE_DIR = os.path.join(BASE_DIR, "final_submission", "images")

def analyze_states():
    """Performs comparative regional analysis across states and union territories."""
    if not os.path.exists(DATA_FILE):
        print(f"I/O Error: Regional profile not identified at {DATA_FILE}. Execute diagnostic scripts first.")
        return

    df = pd.read_csv(DATA_FILE)
    
    # Regional aggregation logic
    state_stats = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'update_intensity': 'mean',
        'district': 'count'
    }).reset_index()
    
    # Performance Indexing (Relative Efficiency Score)
    state_stats['efficiency_score'] = (state_stats['update_intensity'] / state_stats['update_intensity'].max()) * 100
    
    # Regional failure identification (Ghost District Density)
    ghost_counts = df[df['total_updates'] == 0].groupby('state').size().reset_index(name='ghost_count')
    state_stats = state_stats.merge(ghost_counts, on='state', how='left').fillna(0)
    
    # Sorting by performance metrics
    state_stats = state_stats.sort_values('efficiency_score', ascending=False)
    
    print("Regional Performance Dashboard (Top Decile):")
    print(state_stats.head(10)[['state', 'total_enrol', 'efficiency_score', 'ghost_count']])
    
    # Persistence for audit reporting
    output_path = os.path.join(BASE_DIR, "analysis", "results", "state_results.csv")
    state_stats.to_csv(output_path, index=False)
    
    # High-resolution visualization generation
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Metric 1: Efficiency Distribution
    plt.subplot(2, 1, 1)
    sns.barplot(data=state_stats.head(15), x='state', y='efficiency_score', palette='viridis')
    plt.title('Top 15 States by Aadhaar Update Efficiency Index', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.ylabel('Efficiency Index (%)')
    
    # Metric 2: Failure Density
    plt.subplot(2, 1, 2)
    sns.barplot(data=state_stats.sort_values('ghost_count', ascending=False).head(15), x='state', y='ghost_count', palette='magma')
    plt.title('Regional Entities with Critical Ghost District Density', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.ylabel('Ghost District Count')
    
    plt.tight_layout()
    viz_path = os.path.join(IMAGE_DIR, 'state_performance_matrix.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Regional performance matrix exported to {viz_path}")

if __name__ == "__main__":
    analyze_states()

if __name__ == "__main__":
    analyze_states()
