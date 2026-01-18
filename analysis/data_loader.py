import pandas as pd
import glob
import os

# Configuration for dataset directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UIDIA-Datasets'))

def load_dataset(folder_name):
    """Memory-efficient loading and standardizing of CSV datasets from a specified folder."""
    path = os.path.join(BASE_DIR, folder_name, "*.csv")
    files = glob.glob(path)
    if not files:
        print(f"I/O Warning: No data files identified in {path}")
        return pd.DataFrame()
    
    dfs = []
    for f in files:
        try:
            # Load individual CSV shards
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Data Read Error: Failed to process {f}. Details: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    final_df = pd.concat(dfs, ignore_index=True)
    
    # Standardize schema: Trim whitespace and normalize to lowercase
    final_df.columns = [c.strip().lower() for c in final_df.columns]
    
    # Temporal normalization: Ensure standard datetime objects
    if 'date' in final_df.columns:
        final_df['date'] = pd.to_datetime(final_df['date'], dayfirst=True, errors='coerce')
        
    return final_df

def load_all():
    """Orchestrates ingestion across all core Aadhaar transaction datasets."""
    print("Initializing multi-stream data ingestion...")
    
    print("Ingesting Biometric Transaction Logs...")
    bio = load_dataset("api_data_aadhar_biometric")
    
    print("Ingesting Demographic Update Logs...")
    demo = load_dataset("api_data_aadhar_demographic")
    
    print("Ingesting Enrolment Registry Logs...")
    enrol = load_dataset("api_data_aadhar_enrolment")
    
    return bio, demo, enrol

if __name__ == "__main__":
    # Internal validation logic
    b, d, e = load_all()
    print(f"Summary Statistics - Bio: {b.shape}, Demo: {d.shape}, Enrolment: {e.shape}")
