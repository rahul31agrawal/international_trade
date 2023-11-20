import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Import / Export Dashboard!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Import / Export Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;} </style>',unsafe_allow_html=True)




# Get the current working directory (where the script is located)
current_dir = os.path.dirname(os.path.realpath(__file__))

# Specify the relative path to the Excel file
file_path = os.path.join(current_dir, "..", "Final consolidation US.xlsx")

# Read the Excel file
df = pd.read_excel(file_path)


#df = pd.read_excel("Final consolidation US.xlsx")


#df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

df['Date'] = pd.to_datetime(df['Date'])

# Extract the year and create a new column 'Year'

dashboard_df = df.copy()

st.sidebar.header("Choose your filter: ")
# Create for Category
category = st.sidebar.selectbox("Import or Export", dashboard_df["Category"].unique())
if not category:
    df2 = dashboard_df.copy()
else:
    df2 = dashboard_df[dashboard_df["Category"].isin([category])]


# Create for Commodity
commodity = st.sidebar.selectbox("Pick the Commodity", df2["Commodity"].unique())
if not commodity:
    df3 = df2.copy()
else:
    df3 = df2[df2["Commodity"].isin([commodity])]

# Create for City
reporting_country = st.sidebar.selectbox("Pick the Reporting Country",df3["Reporting Country"].unique())

# create for reporting country
if not commodity:
    df4 = df3.copy()
else:
    df4 = df3[df3["Reporting Country"].isin([reporting_country])]


# Create for Year
selected_year = st.sidebar.selectbox("Pick the year",df4["Year"].unique())


def apply_filter(df, category, commodity, reporting_country, year):
    if not category and not commodity and not reporting_country:
        filtered_df = df[df["Year"] == year]
    elif not category and not reporting_country:
        filtered_df = df[df["Category"].isin([category]) & (df["Year"] == year)]
    elif not commodity and not reporting_country:
        filtered_df = df[df["Commodity"].isin([commodity]) & (df["Year"] == year)]
    elif commodity and reporting_country:
        filtered_df = df[df["Commodity"].isin([commodity]) & df["Reporting Country"].isin([reporting_country]) & (df["Year"] == year)]
    elif category and reporting_country:
        filtered_df = df[df["Category"].isin([category]) & df["Reporting Country"].isin([reporting_country]) & (df["Year"] == year)]
    elif category and commodity:
        filtered_df = df[df["Category"].isin([category]) & df["Commodity"].isin([commodity]) & (df["Year"] == year)]
    elif reporting_country:
        filtered_df = df[df["Reporting Country"].isin([reporting_country]) & (df["Year"] == year)]
    else:
        filtered_df = df[df["Category"].isin([category]) & df["Commodity"].isin([commodity]) & df["Reporting Country"].isin([reporting_country]) & (df["Year"] == year)]

    return filtered_df



result_df = apply_filter(df4, category, commodity, reporting_country, selected_year)



# Create a new column for formatted dates
result_df['FormattedDate'] = result_df['Date'].dt.strftime('%b %y')

bar_graph_df = result_df.copy()

bar_graph_df = bar_graph_df.groupby(by=['FormattedDate','Date'])['Quantity'].sum().reset_index()

# Sort the DataFrame by the datetime column
bar_graph_df = bar_graph_df.sort_values('Date')

# Create a bar graph using Plotly Express
fig = px.bar(bar_graph_df, x='FormattedDate', y='Quantity',text = 'Quantity',color_discrete_sequence=['#0083B8']*len(bar_graph_df),template='plotly_white',title=f""" {reporting_country} {commodity} {category}""")

# Format the text to display without decimal places
fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
# Show the plot
st.plotly_chart(fig)

doughnut_chart_df = result_df.copy()
doughnut_chart_df = doughnut_chart_df.groupby(by=['Partner Country'])['Quantity'].sum().reset_index()
#Create a doughnut chart using Plotly Express
# Sort the DataFrame by Quantity in descending order and select the top 10
top_10_df = doughnut_chart_df.sort_values(by='Quantity', ascending=False).head(10)

# Create a doughnut chart using Plotly Express
pie_fig = px.pie(top_10_df, values='Quantity', names='Partner Country', hole=.5)

# Customize the layout
pie_fig.update_layout(
    title="Doughnut Chart with Top 10 Partner Countries",
    template="plotly_white",
    height=500,
    width=500,
    showlegend=True, 
    
)

# Set textinfo for values and percentage
pie_fig.update_traces(textinfo='value+percent', insidetextorientation='radial',  # Display text radially inside
    textposition='outside')

st.plotly_chart(pie_fig)
