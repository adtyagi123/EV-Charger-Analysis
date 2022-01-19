#Libraries to run the app
import os, glob
import pandas as pd
import streamlit as st
import pycountry
import plotly.express as px


#Creating single source data for the app
#Reference: https://www.iea.org/articles/global-ev-data-explorer
os.chdir(os.path.dirname(__file__) + r"\Data")
all_filenames = [i for i in glob.glob('*.{}'.format('csv'))]
df = pd.concat(map(pd.read_csv, all_filenames))
df = df.drop(columns = 'unit')
df.to_csv(os.getcwd() +'\\CompiledData.csv')
df = df.replace('USA', 'United States')

#Adding country Iso code for region
def findCountry (country_name):
    try:
        return pycountry.countries.get(name=country_name).alpha_3
    except:
        return ("not founded")
df['ISO Alpha'] = df.apply(lambda row: findCountry(row.region) , axis = 1)


#Header and description for the app
st.title('EV Data Analysis')

st.markdown("""
This app provides insights on EV data across world.
* **Python libraries: ** base64, pandas, streamlit
* **Datasource: ** [IEA: Global EV Data Explorer](https://www.iea.org/articles/global-ev-data-explorer)
* **Noted legend: ** BEVs are battery electric vehicles. PHEVs are plug-in hybrid electric vehicles. FCEVs are fuel cell electric vehicles. EVs refers to all electric vehicles (BEVs + PHEVs).
""")


#Data analysis of EV Sales and Stocks with respect to vehicle type
df_SS = df[(df['parameter'] != 'EV chargers')]

#Data analysis of EV Sales and Stocks with respect to vehicle type
df_chargers = df[(df['parameter'] == 'EV chargers')]

st.sidebar.header('EV Data Category')
input_parameter = st.sidebar.selectbox('Category', df_SS['parameter'].unique())

st.sidebar.header('EV Vehicle Type')
input_mode = st.sidebar.selectbox('Vehicle Type', df_SS['mode'].unique())

st.sidebar.header('Region')
input_region = st.sidebar.selectbox('Region', df_SS['region'].unique())

#Dataframe clean up for plot generations:
filteredData = df_SS[(df_SS['parameter'] == input_parameter) & (df_SS['mode'] == input_mode) & (df_SS['region'] == input_region)]
filteredData = filteredData.loc[:, ~filteredData.columns.str.contains('^Unnamed')]
filteredData = filteredData.drop_duplicates()
filteredData = filteredData.sort_values(by=['year'])

#Bar chart Plotting:
st.subheader("EV Sales/Stock Data Analysis")
st.markdown("""
Bar chart plot of EV Data Analysis for selected region.
""")

fig_barchart = px.bar(filteredData, x="year", y="value", color="powertrain",  title=f"{input_parameter} Analysis of {input_mode} at {input_region} ")
st.plotly_chart(fig_barchart, use_container_width = True)


#Data analysis for EV chargers
st.subheader("EV Charger Analysis")
st.markdown("""
Global trend of EV chargers over time
""")

#Dataframe clean up for EV Chargers:
df_chargers = df_chargers.loc[:, ~df_chargers.columns.str.contains('^Unnamed')]
df_chargers = df_chargers.drop_duplicates()
df_chargers = df_chargers.sort_values(by=['year'])

fig_bubblePlot = px.scatter_geo(df_chargers, locations="ISO Alpha",
                     hover_name="region", size="value", animation_frame="year",color = 'powertrain',size_max=50,
                     projection="natural earth")
st.plotly_chart(fig_bubblePlot, use_container_width = True)

st.markdown("""
Choose the region you want to view from menu :
""")

if st.button('Show EV Charger Analysis'):
    df_chargers_line = df_chargers[(df_chargers['region'] == input_region) ]
    fig_line = px.line(df_chargers_line, x="year", y="value", color='powertrain')
    st.plotly_chart(fig_line, use_container_width = True)
