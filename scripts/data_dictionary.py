import pandas as pd
import os

# Load the cleaned dataset
df = pd.read_csv("output/processed_cloud_data.csv")

print("=" * 60)
print("DATA DICTIONARY")
print("=" * 60)

dictionary = []

for column in df.columns:

    data_type = str(df[column].dtype)

    if data_type == "object":
        business_type = "Categorical"
    elif "int" in data_type or "float" in data_type:
        business_type = "Numerical"
    else:
        business_type = "Other"

    dictionary.append({
        "Column Name": column,
        "Data Type": data_type,
        "Business Type": business_type,
        "Missing Values": df[column].isnull().sum(),
        "Unique Values": df[column].nunique(),
        "Description": ""
    })

dictionary_df = pd.DataFrame(dictionary)

print(dictionary_df)

os.makedirs("output", exist_ok=True)

dictionary_df.to_csv("output/data_dictionary.csv", index=False)

print("\nData Dictionary saved successfully!")