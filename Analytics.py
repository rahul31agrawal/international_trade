import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Import / Export Analytics!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Import / Export EDA")
st.markdown('<style>div.block-container{padding-top:1rem;} </style>',unsafe_allow_html=True)

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

first_column_name = sorted_df.columns[0]

second_column_name = sorted_df.columns[1]
third_column_name = sorted_df.columns[2]



sorting_column = first_column_name

# Remove commas and convert the values in the sorting column to numeric
sorted_df[sorting_column] = pd.to_numeric(sorted_df[sorting_column].replace(',', ''), errors='coerce')

# Sort the DataFrame based on the specified column
df_sorted = sorted_df.sort_values(by=sorting_column, ascending=False)

result = df_sorted.iloc[:10,:].reset_index()

result.loc[10] = ['Others'] + df_sorted.iloc[10:,:].sum().to_list()
result.loc[11] = ['Total']+ df_sorted.sum().to_list()


# CELL
result['% M-o-M'] = (result[first_column_name] - result[second_column_name])/(result[second_column_name]) * 100
result['% M-o-M'] = result['% M-o-M'].round(2)

result['% Y-o-Y'] = (result[first_column_name] - result[third_column_name])/(result[third_column_name]) * 100
result['% Y-o-Y'] = result['% Y-o-Y'].round(2)

result = result[['Partner Country',first_column_name,second_column_name,'% M-o-M',third_column_name,'% Y-o-Y']]

mom_change_value = result['% M-o-M'].iloc[-1]
current_month_total_value = result[first_column_name].iloc[-1]


yoy_change_value = result['% Y-o-Y'].iloc[-1]
previous_year_same_month_total_value = result[third_column_name].iloc[-1]

# Create a custom style function
def color_negative_red(val):
    color = 'red' if val < 0 else 'green'
    return f'color: {color}'


# Apply the style function to the '% M-o-M' column
styled_result = result.style.applymap(color_negative_red, subset=['% M-o-M','% Y-o-Y'])



# Calculation for cumulative data table
cumulative_data_df = filtered_df.copy()


# Find the latest date in the DataFrame
latest_date_for_cumulative = cumulative_data_df['date'].max()

# Extract the year from the latest date
latest_year_for_cumulative = latest_date_for_cumulative.year

# Filter data for the years 2023 and 2022
filtered_cumulative_data = cumulative_data_df[cumulative_data_df['date'].dt.year.isin([latest_year_for_cumulative, latest_year_for_cumulative - 1])]



# Convert the 'Date' column to datetime format (if not already)
filtered_cumulative_data['date'] = pd.to_datetime(filtered_cumulative_data['date'])

latest_date_prev_year_cumul = latest_date - pd.DateOffset(years=1)


filtered_df_prev_year = filtered_cumulative_data[(filtered_cumulative_data['date'] <= latest_date_prev_year_cumul)]


max_dates = filtered_df_prev_year.groupby(filtered_df_prev_year['date'].dt.year)['date'].transform('max')

# Function to calculate the duration for each row based on the maximum date for the year
def calculate_duration(row):
    year = row['date'].year
    max_date_for_year = max_dates[filtered_df_prev_year['date'].dt.year == year].iloc[0]
    
    if row['date'] <= max_date_for_year:
        return f"January-{max_date_for_year.strftime('%B')}'{str(year)[2:]}"
    else:
        return f"Data not in January-{max_date_for_year.strftime('%B')}"

# Apply the function to create a new column 'Duration'
filtered_df_prev_year['Duration'] = filtered_df_prev_year.apply(calculate_duration, axis=1)
prev_duration_value = filtered_df_prev_year['Duration'].iloc[0]



latest_year_filtered_data = cumulative_data_df[cumulative_data_df['date'].dt.year.isin([latest_year_for_cumulative])]

max_dates2 = latest_year_filtered_data.groupby(latest_year_filtered_data['date'].dt.year)['date'].transform('max')


# Function to calculate the duration for each row based on the maximum date for the year
def calculate_duration2(row):
    year = row['date'].year
    max_date_for_year2 = max_dates2[latest_year_filtered_data['date'].dt.year == year].iloc[0]
    
    if row['date'] <= max_date_for_year2:
        return f"January-{max_date_for_year2.strftime('%B')}'{str(year)[2:]}"
    else:
        return f"Data not in January-{max_date_for_year2.strftime('%B')}"

# Apply the function to create a new column 'Duration'
latest_year_filtered_data['Duration'] = latest_year_filtered_data.apply(calculate_duration2, axis=1)
first_duration_value = latest_year_filtered_data['Duration'].iloc[0]



final_cumulative_data_df = pd.concat([filtered_df_prev_year, latest_year_filtered_data], ignore_index=True)

final_cumulative_data_df["Quantity"] = final_cumulative_data_df["Quantity"].astype(int)

cumul_pivot_table_df = final_cumulative_data_df.pivot_table(index=['Partner Country'], columns=['Duration'], values='Quantity', aggfunc='sum')


# Specify the desired column order
column_order = [ first_duration_value, prev_duration_value]

# Create a new DataFrame with columns in the specified order
cumul_pivot_table_df = cumul_pivot_table_df[column_order]


# Find the name of the second column dynamically
cumul_second_column_name = cumul_pivot_table_df.columns[0]
cumul_third_column_name = cumul_pivot_table_df.columns[1]

# Remove commas and convert the values in the sorting column to numeric
#cumul_pivot_table_df[cumul_second_column_name] = pd.to_numeric(cumul_pivot_table_df[cumul_second_column_name].replace(',', ''), errors='coerce')
# Sort DataFrame based on the second column
cumul_pivot_table_df = cumul_pivot_table_df.sort_values(by=cumul_second_column_name, ascending=False)


cumul_result = cumul_pivot_table_df.iloc[:10,:].reset_index()
cumul_result.loc[10] = ['Others'] + cumul_pivot_table_df.iloc[10:,:].sum().to_list()
cumul_result.loc[11] = ['Total']+ cumul_pivot_table_df.sum().to_list()


cumul_result['% Y-T-D'] = (cumul_result[cumul_second_column_name] - cumul_result[cumul_third_column_name])/(cumul_result[cumul_third_column_name]) * 100
cumul_result['% Y-T-D'] = cumul_result['% Y-T-D'].round(2)






# Apply the style function to the '% M-o-M' column
cumul_styled_result = cumul_result.style.applymap(color_negative_red, subset=['% Y-T-D'])



st.dataframe(styled_result.format({'% Y-o-Y': '{:.2f}', '% M-o-M': '{:.2f}',first_column_name: '{:,.0f}',second_column_name: '{:,.0f}',third_column_name: '{:,.0f}'}), height=480)


st.dataframe(cumul_styled_result.format({'% Y-T-D': '{:.2f}',cumul_second_column_name: '{:,.0f}',cumul_third_column_name: '{:,.0f}'}), height=480)

with col1:
    st.metric(label="Current month Quantity in tons", value="{:,}".format(int(current_month_total_value)), delta=f" M-o-M change {mom_change_value:.2f} % ")

with col2:
    st.metric(label="Same month previous year Quantity in tons", value="{:,}".format(int(previous_year_same_month_total_value)), delta=f" Y-o-Y change {yoy_change_value:.2f} % ")

