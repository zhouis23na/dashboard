import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_number

sns.set(style='darkgrid')

## Create Seasonly df
def create_seasonly_rentals_df(df: pd.DataFrame):
    seasonly_rentals_df = df.groupby(by='season').cnt.sum().reset_index()
    return seasonly_rentals_df

## Create Hourly df
def create_hourly_rentals_df(df: pd.DataFrame):
    hourly_rentals_df = df.groupby(by='hr').cnt.sum().reset_index()
    return hourly_rentals_df

## Create Timely df
def create_timely_rentals_df(df: pd.DataFrame):
    timely_rentals_df = df.groupby(by='Time').cnt.sum().reset_index()
    return timely_rentals_df

hour_df = pd.read_csv('C:/Users/AKMAL/Documents/python_2024/Dicoding_Data_Science/submission/dashboard/hour_cleaned_df.csv')
day_df = pd.read_csv('C:/Users/AKMAL/Documents/python_2024/Dicoding_Data_Science/submission/dashboard/day_cleaned_df.csv')

# Normalize temperature and humidity in hourly data
hour_df['temp'] = (hour_df['temp'] - hour_df['temp'].min()) / (hour_df['temp'].max() - hour_df['temp'].min())
hour_df['atemp'] = (hour_df['atemp'] - hour_df['atemp'].min()) / (hour_df['atemp'].max() - hour_df['atemp'].min())
hour_df['hum'] = (hour_df['hum'] - hour_df['hum'].min()) / (hour_df['hum'].max() - hour_df['hum'].min())

hour_df['temp'] = hour_df['temp'] * (39 - (-8)) + (-8)
hour_df['atemp'] = hour_df['atemp'] * (50 - (-16)) + (-16)
hour_df['hum'] = hour_df['hum'] * 100

# Convert date columns to datetime
day_df.sort_values(by='dteday', inplace=True, ascending=True)
day_df.reset_index(drop=True, inplace=True)

hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Date range for sidebar filters
date_min = day_df['dteday'].min()
date_max = day_df['dteday'].max()

with st.sidebar:
    st.header('Filter Options')
    start_date, end_date = st.date_input(
        label='Select Date Range',
        min_value=date_min,
        max_value=date_max,
        value=[date_min, date_max],
    )

# Filter data based on selected date range
access_hour_df = hour_df[(hour_df['dteday'] >= str(start_date)) & (hour_df['dteday'] <= str(end_date))]
access_day_df = day_df[(day_df['dteday'] >= str(start_date)) & (day_df['dteday'] <= str(end_date))]

# Create dataframes for visualization
seasonly_rentals_df = create_seasonly_rentals_df(access_day_df)
hourly_rentals_df = create_hourly_rentals_df(access_hour_df)
timely_rentals_df = create_timely_rentals_df(access_hour_df)

st.title('Bike Rentals Dashboard 🚴‍♂️')
st.markdown("### Overview")
st.markdown(
    "This dashboard provides insights into bike rental data, including seasonal trends, hourly usage, and environmental factors like temperature and humidity."
)

# Seasonly Rentals
st.subheader('Seasonal Rentals')
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    data=seasonly_rentals_df.sort_values(by='cnt', ascending=False),
    x='season',
    y='cnt',
    palette='Blues_r',
    ax=ax,
    hue='season'
)
ax.set_title('Number of Rentals by Season', fontsize=18)
ax.set_xlabel('Season', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Daily Rentals
st.subheader('Daily Rentals')
total_orders = format_number(access_day_df['cnt'].sum(), locale='de_DE')
st.metric('Total Rentals', value=total_orders)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    access_day_df['dteday'],
    access_day_df['cnt'],
    linewidth=2,
    color='#08519C'
)
ax.set_title('Daily Rentals Trend', fontsize=18)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Timely Rentals
st.subheader('Rentals by Time of Day')
timely_rentals_df['Time'] = pd.Categorical(timely_rentals_df['Time'], ['Morning', 'Day', 'Afternoon', 'Evening'])
colors = ["#08519C", "#08519C", "#08519C", "#08519C"]
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    data=timely_rentals_df.sort_values(by='Time', ascending=True),
    x='Time',
    y='cnt',
    palette=colors,
    ax=ax
)
ax.set_title('Number of Rentals by Time of Day', fontsize=18)
ax.set_xlabel('Time of Day', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Hourly Rentals
st.subheader('Top 5 Rental Hours')
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    data=hourly_rentals_df.sort_values(by='cnt', ascending=False).head(5),
    x='hr',
    y='cnt',
    palette='Blues_r',
    hue='hr',
    ax=ax
)
ax.set_title('Top 5 Hours for Rentals', fontsize=18)
ax.set_xlabel('Hour', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
st.pyplot(fig)

# Temperature and Humidity
st.subheader('Environmental Factors')
avg_temp = access_hour_df['temp'].mean()
avg_atemp = access_hour_df['atemp'].mean()
avg_hum = access_hour_df['hum'].mean()

col1, col2, col3 = st.columns(3)
col1.metric('Average Temperature (°C)', f"{avg_temp:.2f}")
col2.metric('Average Feeling Temperature (°C)', f"{avg_atemp:.2f}")
col3.metric('Average Humidity (%)', f"{avg_hum:.2f}")