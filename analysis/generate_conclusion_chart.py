import matplotlib.pyplot as plt
import os

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_DIR = os.path.join(BASE_DIR, "final_submission", "images")
OUTPUT_FILE = os.path.join(IMAGE_DIR, "conclusion_roi_breakdown.png")

# Data from the report (5-Year Total 7% Discount)
labels = ['Leakage Prevention\n(₹43.21 Cr)', 'Fraud Detection\n(₹7.87 Cr)', 'Labor Efficiency\n(₹5.29 Cr)']
sizes = [43.21, 7.87, 5.29]
colors = ['#003366', '#960000', '#A0A0A0']  # Navy (Primary), Red (Accent), Gray
explode = (0.1, 0, 0)  # offset the extraction for emphasis

# Create Pie Chart
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))

wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%',
                                  textprops=dict(color="w"),
                                  colors=colors,
                                  startangle=140,
                                  explode=explode,
                                  shadow=True)

ax.legend(wedges, labels,
          title="Value Realization Areas",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

plt.setp(autotexts, size=10, weight="bold")
ax.set_title("5-Year Value Realization: ₹56.37 Crore Total Benefit", fontsize=14, fontweight='bold', color='#333333')

# Ensure directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Save
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Pie chart saved to {OUTPUT_FILE}")
