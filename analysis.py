import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(r"C:\Users\Josh\OneDrive\Documents\healthcare-claims-analysis")
print("Current folder:", os.getcwd())

train_df = pd.read_csv("Train_Inpatientdata-1542865627584.csv")
test_df = pd.read_csv("Test_Inpatientdata-1542969243754.csv")


train_df['source'] = 'train'
test_df['source'] = 'test'

df = pd.concat([
    train_df.assign(source='train'),
    test_df.assign(source='test')
], ignore_index=True)

provider_avg = df.groupby('Provider')['InscClaimAmtReimbursed'].mean().reset_index()
provider_avg = provider_avg.sort_values(by='InscClaimAmtReimbursed', ascending=False)

provider_avg.head(10)

provider_summary = df.groupby('Provider').agg(
    Avg_Reimbursement=('InscClaimAmtReimbursed', 'mean'),
    Total_Claims=('ClaimID', 'count'),
    Unique_Patients=('BeneID', 'nunique')
).reset_index()

provider_summary = provider_summary.rename(columns={
    'InscClaimAmtReimbursed': 'Avg_Reimbursement',
    'ClaimID': 'Total_Claims',
    'BeneID': 'Unique_Patients'
})

provider_summary['claims_per_patient'] = (
    provider_summary['Total_Claims'] / provider_summary['Unique_Patients']
)


reimb_threshold = (
    provider_summary['Avg_Reimbursement'].mean() +
    2 * provider_summary['Avg_Reimbursement'].std()
)

# Claims per patient threshold
cpp_threshold = (
    provider_summary['claims_per_patient'].mean() +
    2 * provider_summary['claims_per_patient'].std()
)

# Flag outliers
provider_summary['is_outlier'] = (
    provider_summary['Avg_Reimbursement'] > reimb_threshold
)

# Flag suspicious providers (multi-condition)
suspicious_providers = provider_summary[
    (provider_summary['Avg_Reimbursement'] > reimb_threshold) &
    (provider_summary['claims_per_patient'] > cpp_threshold)
]

print("Outliers:")
print(provider_summary[provider_summary['is_outlier'] == True])

print("\nSuspicious Providers:")
print(suspicious_providers)

top10 = provider_summary.sort_values(
    by='Avg_Reimbursement',
    ascending=False
).head(10)

plt.figure(figsize=(12, 6))
plt.bar(top10['Provider'], top10['Avg_Reimbursement'])

plt.title('Top 10 Providers by Average Reimbursement', fontsize=14)
plt.xlabel('Provider ID', fontsize=12)
plt.ylabel('Average Reimbursement ($)', fontsize=12)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


print(provider_summary['Avg_Reimbursement'].describe())

plt.figure(figsize=(10, 6))

plt.hist(provider_summary['Avg_Reimbursement'], bins=30)

plt.title('Distribution of Average Reimbursement Across Providers', fontsize=14)
plt.xlabel('Average Reimbursement ($)', fontsize=12)
plt.ylabel('Number of Providers', fontsize=12)

plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 6))
plt.hist(provider_summary['Avg_Reimbursement'], bins=30)

plt.axvline(provider_summary['Avg_Reimbursement'].mean())
plt.axvline(reimb_threshold)

plt.title('Distribution with Mean & Outlier Threshold')
plt.xlabel('Average Reimbursement ($)')
plt.ylabel('Number of Providers')

plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 6))

# All providers
plt.scatter(
    provider_summary['claims_per_patient'],
    provider_summary['Avg_Reimbursement']
)

# Highlight suspicious providers
plt.scatter(
    suspicious_providers['claims_per_patient'],
    suspicious_providers['Avg_Reimbursement']
)

plt.axhline(reimb_threshold)
plt.axvline(cpp_threshold)

plt.xlabel('Claims per Patient')
plt.ylabel('Average Reimbursement ($)')
plt.title('Provider Risk Analysis')

plt.tight_layout()
plt.show()

len(provider_summary[provider_summary['is_outlier']])
suspicious_providers.describe()
provider_summary.describe()

provider_summary['reimb_zscore'] = (
    (provider_summary['Avg_Reimbursement'] - provider_summary['Avg_Reimbursement'].mean()) /
    provider_summary['Avg_Reimbursement'].std()
)

provider_summary['cpp_zscore'] = (
    (provider_summary['claims_per_patient'] - provider_summary['claims_per_patient'].mean()) /
    provider_summary['claims_per_patient'].std()
)

provider_summary['risk_score'] = (
    provider_summary['reimb_zscore'] +
    provider_summary['cpp_zscore']
)

suspicious_providers = provider_summary[
    (provider_summary['Avg_Reimbursement'] > reimb_threshold) &
    (provider_summary['claims_per_patient'] > cpp_threshold)
]

suspicious_providers.sort_values(by='risk_score', ascending=False).head()


high_risk = provider_summary.sort_values(by='risk_score', ascending=False)

print(high_risk.head(10))
