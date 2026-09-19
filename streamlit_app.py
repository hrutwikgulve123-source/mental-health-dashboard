import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="Mental Health in Tech - Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM STYLING =====
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    h1 {
        color: #1f77b4;
        font-size: 2.5rem;
    }
    h2 {
        color: #2c3e50;
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_csv('survey.csv')
    # Clean age
    df = df[(df['Age'] >= 18) & (df['Age'] <= 100)].copy()
    # Convert timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    # Clean gender
    gender_mapping = {
        'M': 'Male', 'Male': 'Male', 'male': 'Male', 'm': 'Male',
        'F': 'Female', 'Female': 'Female', 'female': 'Female', 'f': 'Female',
        'Femake': 'Female', 'femail': 'Female', 'Woman': 'Female', 'woman': 'Female',
        'Man': 'Male', 'cis male': 'Male', 'cis-male': 'Male'
    }
    df['Gender'] = df['Gender'].str.strip().map(lambda x: gender_mapping.get(x, 'Other'))
    # Keep top 10 countries
    top_countries = df['Country'].value_counts().head(10).index.tolist()
    df['Country'] = df['Country'].apply(lambda x: x if x in top_countries else 'Other')
    return df

df = load_data()

# ===== SIDEBAR FILTERS =====
st.sidebar.title("🎯 FILTERS & SLICERS")
st.sidebar.markdown("---")

# Age Range Filter
age_range = st.sidebar.slider(
    "Age Range",
    int(df['Age'].min()),
    int(df['Age'].max()),
    (int(df['Age'].min()), int(df['Age'].max())),
    step=1
)

# Gender Filter
gender_filter = st.sidebar.multiselect(
    "Gender",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

# Country Filter
country_filter = st.sidebar.multiselect(
    "Country",
    options=sorted(df['Country'].unique()),
    default=sorted(df['Country'].unique())
)

# Tech Company Filter
tech_company_filter = st.sidebar.multiselect(
    "Tech Company",
    options=['Yes', 'No', 'Not sure'],
    default=['Yes', 'No', 'Not sure']
)

# Family History Filter
family_history_filter = st.sidebar.multiselect(
    "Family History of Mental Illness",
    options=['Yes', 'No'],
    default=['Yes', 'No']
)

# Treatment Seeking Filter
treatment_filter = st.sidebar.multiselect(
    "Sought Mental Health Treatment",
    options=['Yes', 'No'],
    default=['Yes', 'No']
)

# Apply Filters
df_filtered = df[
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1]) &
    (df['Gender'].isin(gender_filter)) &
    (df['Country'].isin(country_filter)) &
    (df['tech_company'].isin(tech_company_filter)) &
    (df['family_history'].isin(family_history_filter)) &
    (df['treatment'].isin(treatment_filter))
]

# ===== HEADER =====
st.title("🧠 Mental Health in Tech Survey - Interactive Dashboard")
st.markdown("### Comprehensive Analysis of Mental Health Attitudes and Workplace Support")

# Display filter info
st.info(f"📊 Showing data for {len(df_filtered):,} respondents (filtered from {len(df):,} total)")

st.markdown("---")

# ===== ROW 1: KEY METRICS =====
st.subheader("📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Respondents",
        value=f"{len(df_filtered):,}",
        delta=f"({(len(df_filtered)/len(df)*100):.1f}% of dataset)"
    )

with col2:
    treatment_pct = (df_filtered['treatment'] == 'Yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.metric(
        label="Sought Treatment",
        value=f"{treatment_pct:.1f}%",
        delta=f"{(df_filtered['treatment'] == 'Yes').sum()} people"
    )

with col3:
    family_pct = (df_filtered['family_history'] == 'Yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.metric(
        label="Family History",
        value=f"{family_pct:.1f}%",
        delta=f"{(df_filtered['family_history'] == 'Yes').sum()} people"
    )

with col4:
    benefits_pct = (df_filtered['benefits'] == 'Yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.metric(
        label="With Benefits",
        value=f"{benefits_pct:.1f}%",
        delta=f"{(df_filtered['benefits'] == 'Yes').sum()} people"
    )

with col5:
    remote_pct = (df_filtered['remote_work'] == 'Yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.metric(
        label="Remote Work",
        value=f"{remote_pct:.1f}%",
        delta=f"{(df_filtered['remote_work'] == 'Yes').sum()} people"
    )

st.markdown("---")

# ===== ROW 2: DEMOGRAPHICS =====
st.subheader("👥 Demographics Analysis")

col1, col2 = st.columns(2)

with col1:
    st.write("#### Gender Distribution")
    gender_data = df_filtered['Gender'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    ax.pie(gender_data.values, labels=gender_data.index, autopct='%1.1f%%', 
           colors=colors[:len(gender_data)], startangle=90)
    ax.set_title('Gender Distribution', fontweight='bold', fontsize=12)
    st.pyplot(fig)
    plt.close()

with col2:
    st.write("#### Age Distribution")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df_filtered['Age'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Age', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('Age Distribution', fontweight='bold', fontsize=12)
    ax.axvline(df_filtered['Age'].mean(), color='red', linestyle='--', label=f'Mean: {df_filtered["Age"].mean():.1f}')
    ax.axvline(df_filtered['Age'].median(), color='green', linestyle='--', label=f'Median: {df_filtered["Age"].median():.1f}')
    ax.legend()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ===== ROW 3: MENTAL HEALTH ANALYSIS =====
st.subheader("🏥 Mental Health Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("#### Treatment Seeking")
    treatment_data = df_filtered['treatment'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    colors_treat = ['#2ecc71', '#e74c3c']
    ax.bar(treatment_data.index, treatment_data.values, color=colors_treat[:len(treatment_data)], edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Sought Mental Health Treatment', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    for i, v in enumerate(treatment_data.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

with col2:
    st.write("#### Family History")
    family_data = df_filtered['family_history'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    colors_fam = ['#4ECDC4', '#FF6B6B']
    ax.bar(family_data.index, family_data.values, color=colors_fam[:len(family_data)], edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Family History of Mental Illness', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    for i, v in enumerate(family_data.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

with col3:
    st.write("#### Work Interference")
    work_data = df_filtered['work_interfere'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    colors_work = ['#FF6B6B', '#FFA07A', '#95E1D3', '#4ECDC4']
    ax.bar(range(len(work_data)), work_data.values, color=colors_work[:len(work_data)], edgecolor='black')
    ax.set_xticks(range(len(work_data)))
    ax.set_xticklabels(work_data.index, rotation=45, ha='right')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Mental Health Interferes with Work', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ===== ROW 4: WORKPLACE SUPPORT =====
st.subheader("💼 Workplace Support & Benefits")

col1, col2 = st.columns(2)

with col1:
    st.write("#### Employer Benefits")
    benefits_data = df_filtered['benefits'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_ben = ['#2ecc71', '#e74c3c', '#95a5a6']
    ax.bar(benefits_data.index, benefits_data.values, color=colors_ben[:len(benefits_data)], edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Employer Provides Mental Health Benefits', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    for i, v in enumerate(benefits_data.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

with col2:
    st.write("#### Remote Work Availability")
    remote_data = df_filtered['remote_work'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_remote = ['#4ECDC4', '#FF6B6B']
    ax.bar(remote_data.index, remote_data.values, color=colors_remote[:len(remote_data)], edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Remote Work Opportunity', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    for i, v in enumerate(remote_data.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ===== ROW 5: WORKPLACE STIGMA =====
st.subheader("😟 Workplace Stigma & Disclosure")

col1, col2 = st.columns(2)

with col1:
    st.write("#### Fear of Consequences")
    consequence_data = df_filtered['mental_health_consequence'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_cons = ['#e74c3c', '#2ecc71']
    ax.pie(consequence_data.values, labels=consequence_data.index, autopct='%1.1f%%',
           colors=colors_cons[:len(consequence_data)], startangle=90)
    ax.set_title('Fear Negative Consequences for Disclosure', fontweight='bold', fontsize=12)
    st.pyplot(fig)
    plt.close()

with col2:
    st.write("#### Willingness to Discuss")
    coworkers_data = df_filtered['coworkers'].value_counts()
    supervisor_data = df_filtered['supervisor'].value_counts()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    colors_discuss = ['#4ECDC4', '#FF6B6B', '#95E1D3']
    ax1.bar(coworkers_data.index, coworkers_data.values, color=colors_discuss[:len(coworkers_data)], edgecolor='black')
    ax1.set_ylabel('Count', fontweight='bold')
    ax1.set_title('Discuss with Coworkers', fontweight='bold', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    ax2.bar(supervisor_data.index, supervisor_data.values, color=colors_discuss[:len(supervisor_data)], edgecolor='black')
    ax2.set_ylabel('Count', fontweight='bold')
    ax2.set_title('Discuss with Supervisor', fontweight='bold', fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ===== ROW 6: GEOGRAPHIC ANALYSIS =====
st.subheader("🌍 Geographic Distribution")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("#### Top Countries")
    country_data = df_filtered['Country'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(range(len(country_data)), country_data.values, color='steelblue', edgecolor='black')
    ax.set_yticks(range(len(country_data)))
    ax.set_yticklabels(country_data.index)
    ax.set_xlabel('Number of Respondents', fontweight='bold')
    ax.set_title('Top 10 Countries - Survey Respondents', fontweight='bold', fontsize=12)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    for i, v in enumerate(country_data.values):
        ax.text(v + 5, i, str(v), va='center', fontweight='bold')
    st.pyplot(fig)
    plt.close()

with col1:
    st.write("#### Country Statistics")
    country_stats = pd.DataFrame({
        'Country': country_data.index,
        'Respondents': country_data.values,
        'Percentage': (country_data.values / len(df_filtered) * 100).round(1)
    })
    st.dataframe(country_stats, use_container_width=True, hide_index=True)

st.markdown("---")

# ===== ROW 7: CROSS-TABULATION ANALYSIS =====
st.subheader("🔍 Cross-Tabulation Analysis")

analysis_type = st.selectbox(
    "Select Analysis:",
    [
        "Family History vs Treatment",
        "Gender vs Treatment",
        "Country vs Benefits",
        "Tech Company vs Treatment"
    ]
)

if analysis_type == "Family History vs Treatment":
    crosstab = pd.crosstab(df_filtered['family_history'], df_filtered['treatment'])
    fig, ax = plt.subplots(figsize=(10, 6))
    crosstab.plot(kind='bar', ax=ax, color=['#3498db', '#e67e22'], edgecolor='black')
    ax.set_title('Family History Impact on Treatment Seeking', fontweight='bold', fontsize=12)
    ax.set_xlabel('Family History', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.legend(title='Sought Treatment')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=0)
    st.pyplot(fig)
    plt.close()
    st.write(crosstab)

elif analysis_type == "Gender vs Treatment":
    crosstab = pd.crosstab(df_filtered['Gender'], df_filtered['treatment'])
    fig, ax = plt.subplots(figsize=(10, 6))
    crosstab.plot(kind='bar', ax=ax, color=['#3498db', '#e67e22'], edgecolor='black')
    ax.set_title('Gender Differences in Treatment Seeking', fontweight='bold', fontsize=12)
    ax.set_xlabel('Gender', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.legend(title='Sought Treatment')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()
    st.write(crosstab)

elif analysis_type == "Country vs Benefits":
    crosstab = pd.crosstab(df_filtered['Country'], df_filtered['benefits'])
    fig, ax = plt.subplots(figsize=(12, 6))
    crosstab.plot(kind='bar', ax=ax, edgecolor='black')
    ax.set_title('Mental Health Benefits by Country', fontweight='bold', fontsize=12)
    ax.set_xlabel('Country', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.legend(title='Benefits', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

else:  # Tech Company vs Treatment
    crosstab = pd.crosstab(df_filtered['tech_company'], df_filtered['treatment'])
    fig, ax = plt.subplots(figsize=(10, 6))
    crosstab.plot(kind='bar', ax=ax, color=['#3498db', '#e67e22'], edgecolor='black')
    ax.set_title('Treatment Seeking by Company Type', fontweight='bold', fontsize=12)
    ax.set_xlabel('Tech Company', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.legend(title='Sought Treatment')
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=0)
    st.pyplot(fig)
    plt.close()
    st.write(crosstab)

st.markdown("---")

# ===== ROW 8: DATA EXPLORER =====
st.subheader("📊 Data Explorer & Download")

col1, col2 = st.columns(2)

with col1:
    st.write("#### Filtered Dataset Preview")
    st.dataframe(df_filtered.head(10), use_container_width=True)

with col2:
    st.write("#### Dataset Statistics")
    stats_data = {
        'Metric': ['Total Records', 'Average Age', 'Median Age', 'Age Range'],
        'Value': [
            len(df_filtered),
            f"{df_filtered['Age'].mean():.1f}",
            f"{df_filtered['Age'].median():.1f}",
            f"{df_filtered['Age'].min():.0f} - {df_filtered['Age'].max():.0f}"
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

# Download button
@st.cache_data
def convert_df(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv = convert_df(df_filtered)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="mental_health_filtered_data.csv",
    mime="text/csv"
)

st.markdown("---")

# ===== FOOTER =====
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem;">
    <p><strong>Mental Health in Tech Survey Dashboard</strong></p>
    <p>Data Period: August 2014 - February 2016 | Total Original Sample: 1,259 respondents</p>
    <p>🔍 Use filters in the sidebar to explore specific segments of the data</p>
</div>
""", unsafe_allow_html=True)
