import pandas as pd
import glob
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UIDIA-Datasets'))

def load_dataset(folder_name):
    path = os.path.join(BASE_DIR, folder_name, "*.csv")
    files = glob.glob(path)
    if not files:
        print(f"No files found in {path}")
        return pd.DataFrame()
    
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    final_df = pd.concat(dfs, ignore_index=True)
    
    # Standardize column names
    final_df.columns = [c.strip().lower() for c in final_df.columns]
    
    # Parse dates
    if 'date' in final_df.columns:
        final_df['date'] = pd.to_datetime(final_df['date'], dayfirst=True, errors='coerce')
        
    return final_df

def load_all():
    print("Loading Biometric Data...")
    bio = load_dataset("api_data_aadhar_biometric")
    
    print("Loading Demographic Data...")
    demo = load_dataset("api_data_aadhar_demographic")
    
    print("Loading Enrolment Data...")
    enrol = load_dataset("api_data_aadhar_enrolment")
    
    return bio, demo, enrol

if __name__ == "__main__":
    b, d, e = load_all()
    print(f"Biometric: {b.shape}")
    print(b.head())
    print(f"Demographic: {d.shape}")
    print(d.head())
    print(f"Enrolment: {e.shape}")
    print(e.head())
