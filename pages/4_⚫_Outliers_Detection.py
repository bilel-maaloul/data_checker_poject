import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np

from functions.plot_functions import plot_with_outliers


date_cols = []
numerical_cols = []


st.title("Outlier Detection")

css = """
        <style>
        /* Customize the input box */
        div.stTextInput > div > div > input[type="text"] {
            border: 2px solid #3498db;
            border-radius: 5px;
            padding: 10px;
            font-size: 18px;
            outline: none;
            box-shadow: none;
        }

        /* Add a nice hover effect */
        div.stTextInput > div > div > input[type="text"]:hover {
            border-color: #2980b9;
        }

        /* Style the placeholder text */
        div.stTextInput > div > div > input[type="text"]::placeholder {
            color: #95a5a6;
        }

      
       
        .stTextArea textarea {
            background-color: #3D3D3D;
            color : white
            }
        </style>
        """

def get_dates_values(data, date_col, col_1, col_2=None,operation=None):
    
    data2 = data.copy()
    if col_2 == None:
        df_return = data2.groupby(date_col,as_index=False)[col_1].sum()
        return df_return[date_col], df_return[col_1]
    elif operation == "diff":
        df_return = data2.groupby(date_col,as_index=False).sum()
        df_return["diff"] = data2[col_1]-data2[col_2]
        return df_return[date_col], df_return["diff"]
    elif operation =="ratio":
        df_return = data2.groupby(date_col,as_index=False).sum()
        df_return["ratio"] = data2[col_1]/data2[col_2]
    return df_return[date_col], df_return["ratio"]



                   



######################
# Main page
######################
   
if "df" not in st.session_state:
    st.warning("input data before moving to this page")
else:
    df = st.session_state["df"]
    st.dataframe(df.head())
    default_types_map = dict(df.dtypes)
    categorical_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['object']]
    date_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['datetime64[ns]']]
    numerical_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['float64', 'int64']]
if (len(date_cols)==0)|(len(numerical_cols)==0):
    st.warning("No date or numerical column selected")
else:
    
    col1,col2 = st.columns(2)
    selected_date_col = col1.selectbox("date column : ", date_cols)
    selected_col1 = col2.selectbox("select column : ", numerical_cols)
   

# Set the 'date' column as the index
   
# Reindex the dataframe to include all dates within a specified range
    
    

    selected_type = st.radio("type of outlier : ",["values","variation"])

    col1,col2 = st.columns(2)
    selected_operation = col1.radio("operation : ",["uni-variation","diff","ratio"])
    date_range = pd.date_range(start=df[selected_date_col].min(), end=df[selected_date_col].max(), freq='D')
    date_range_df = pd.DataFrame({selected_date_col: date_range})
    # Merge the original data with the date range DataFrame
    df= pd.merge(date_range_df, df, on=selected_date_col, how='left')
    df = df.select_dtypes(exclude='category')
  
    empty_box = col2.empty()
    if selected_operation != "uni-variation":
        selected_col2 = col2.selectbox("select second column : ", numerical_cols)
        dates,values = get_dates_values(df,selected_date_col,selected_col1,selected_col2,selected_operation)
        
        plot_with_outliers(dates,values,selected_type,selected_col1,selected_operation,selected_col2)
        
    else:
        dates,values = get_dates_values(df,selected_date_col,selected_col1)
       
       
        selected_col2=''
        plot_with_outliers(dates,values,selected_type,selected_col1,selected_operation,selected_col2)
        


