import os
import pandas as pd

p = 'output/segment_analysis_augmented.csv'
print(os.path.exists(p))
if os.path.exists(p):
    df = pd.read_csv(p)
    print(df.head().to_string(index=False))
    print(df.columns.tolist())
