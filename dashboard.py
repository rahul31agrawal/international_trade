import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Import / Export!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Import / Export EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\My Data\Rahul Edrive\my_code\dashboard")
    df = pd.read_excel("Final consolidation US.xlsx")


col1, col2 = st.columns((2))
df["Date"] = pd.to_datetime(df["Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Date"]).min()
endDate = pd.to_datetime(df["Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))


df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Category
category = st.sidebar.multiselect("Import or Export", df["Category"].unique())
if not category:
    df2 = df.copy()
else:
    df2 = df[df["Category"].isin(category)]


# Create for Commodity
commodity = st.sidebar.multiselect("Pick the Commodity", df2["Commodity"].unique())
if not commodity:
    df3 = df2.copy()
else:
    df3 = df2[df2["Commodity"].isin(commodity)]

# Create for City
reporting_country = st.sidebar.multiselect("Pick the Reporting Country",df3["Reporting Country"].unique())

# Filter the data based on category, State and City

if not category and not commodity and not reporting_country:
    filtered_df = df
elif not commodity and not reporting_country:
    filtered_df = df[df["Category"].isin(category)]
elif not category and not reporting_country:
    filtered_df = df[df["Commodity"].isin(commodity)]
elif commodity and reporting_country:
    filtered_df = df3[df["Commodity"].isin(commodity) & df3["Reporting Country"].isin(reporting_country)]
elif category and reporting_country:
    filtered_df = df3[df["Category"].isin(category) & df3["Reporting Country"].isin(reporting_country)]
elif category and commodity:
    filtered_df = df3[df["Category"].isin(category) & df3["Commodity"].isin(commodity)]
elif reporting_country:
    filtered_df = df3[df3["Reporting Country"].isin(reporting_country)]
else:
    filtered_df = df3[df3["Category"].isin(category) & df3["Commodity"].isin(commodity) & df3["Reporting Country"].isin(reporting_country)]


# My code starts here

filtered_df.rename(columns={'Date':'date'}, inplace=True)
# Find the latest date
latest_date = filtered_df['date'].max()

# Create copies for calculations
latest_date_minus_1 = latest_date - pd.DateOffset(months=1)
latest_date_prev_year = latest_date - pd.DateOffset(years=1)
second_filtered_df = filtered_df[(filtered_df['date'] == latest_date) | (filtered_df['date'] == latest_date_minus_1) | (filtered_df['date'] == latest_date_prev_year)]

#second_filtered_df.groupby(['Partner Country','date'])['Quantity'].sum().reset_index().pivot_table(index = ['Partner Country'], columns = ['date'])['Quantity']

second_filtered_df["Quantity"] = second_filtered_df["Quantity"].astype(int)
# Create a pivot table
pivot_table_df = second_filtered_df.pivot_table(index=['Partner Country'], columns=['date'], values='Quantity', aggfunc='sum')

# Sort columns in decreasing order of date
pivot_table_df = pivot_table_df[sorted(pivot_table_df.columns, reverse=True)]

# Find the name of the second column dynamically
second_column_name = pivot_table_df.columns[1]

# Sort DataFrame based on the second column
sorted_df = pivot_table_df.sort_values(by=second_column_name, ascending=False)
# Convert the column names to datetime objects
sorted_df.columns = pd.to_datetime(sorted_df.columns)

# Format the datetime objects as desired (e.g., 'Month'YY)
formatted_columns = sorted_df.columns.strftime('%B\'%y')

#In this example, the %B format code is used to represent the full month name, and %y is used to represent the last two digits of the year.

# Rename the DataFrame columns with the formatted values
sorted_df.columns =  formatted_columns




sorting_column = "September'23"

# Remove commas and convert the values in the sorting column to numeric
sorted_df[sorting_column] = pd.to_numeric(sorted_df[sorting_column].replace(',', ''), errors='coerce')

# Sort the DataFrame based on the specified column
df_sorted = sorted_df.sort_values(by=sorting_column, ascending=False)

with col1:
    st.dataframe(df_sorted, height=300)




