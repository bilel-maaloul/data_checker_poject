
import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np
import sys
from functions.report_functions import get_text,add_report_Date
from functions.plot_functions import plot_date_completness
days_of_week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
periods = ["Daily", "Weekly", "Monthly"]
date_cols = []
 # Custom CSS style for the text input

def get_periodicity(data,date_col):
    unique = data[date_col].sort_values().unique()
    df_date = pd.DataFrame()
    df_date["Date"] = unique
    d = df_date.diff().mode().loc[0,"Date"].days
    if d==1:
        return "Daily",1
    if (d>=6)&(d<=9):
        return "Weekly", df_date["Date"][0].day_name()
    if (d>28) & (d<32):
        return  "Monthly",df_date["Date"][0].day==1
    

def period_to_freq(period,op):
    if period=="Daily":
        return "D"
    if period=="Weekly":
        return "W-"+str(op)
    if period=="Month":
        if op:
            return "MS"
        else:
            return "M"


def create_mapping_table(data,reference_dates,cat_cols=[]):
    if len(cat_cols)>0:
        df_mapping = data[cat_cols].drop_duplicates()
        df_mapping["key"] = 1
        reference_dates["key"] = 1
        return pd.merge(reference_dates,df_mapping,on="key")[["Date"]+cat_cols]
    else:
        return reference_dates

def get_merge_date_mapping(data,df_mapping,date_col,cat_cols):
    return pd.merge(df_mapping,
                    data[[date_col]+cat_cols],
                    left_on=["Date"]+cat_cols,
                    right_on=[date_col]+cat_cols,
                    how="left",
                    indicator=True).drop_duplicates()

def categories_with_missing_dates(data,cat_cols) :
    return data[data["_merge"]=="left_only"][cat_cols].drop_duplicates()


######################
# Main page
######################


st.title("Date Handle")
if "df" not in st.session_state:
    st.warning("input data before moving to this page")
else:
    df = st.session_state["df"]
    st.dataframe(df.head())
    default_types_map = dict(df.dtypes)
    categorical_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['object']]
    date_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['datetime64[ns]']]
if len(date_cols)==0:
    st.warning("No date column selected")
else:
    try:
        selected_date_col = st.selectbox("date column : ", date_cols)

        selected_cat_cols = st.multiselect("categorical column(s) : ", categorical_cols, default=[],max_selections=3)

        periodicity = get_periodicity(df,selected_date_col)
        if periodicity:

            col1, col2 = st.columns(2)
            
            selected_period = col1.selectbox("select periodicity",periods,index=periods.index(periodicity[0]))

            container = col2.empty()
            
            option = 0
            if selected_period == "Daily":
                container = col2.empty()
            if selected_period == "Weekly":
                try:
                    option = container.selectbox("select day of week",days_of_week,index=days_of_week.index(periodicity[1]))
                except:
                    st.write("""there are no weeks periods""")

            if selected_period == "Monthly":
                option = container.checkbox("starting side", value= bool(periodicity[1]))

            col1, col2 = st.columns(2)
            selected_start_date = col1.date_input("start date", df[selected_date_col].min())
            selected_end_date = col2.date_input("end date", df[selected_date_col].max())

            freq = period_to_freq(selected_period,option)

            reference_dates = pd.DataFrame({"Date":pd.date_range(selected_start_date,selected_end_date,freq=freq)})
        
            df_mapping = create_mapping_table(df,reference_dates,selected_cat_cols)
            df_merge = get_merge_date_mapping(df,df_mapping,selected_date_col,selected_cat_cols)
            missing_data = categories_with_missing_dates(df_merge,selected_cat_cols)
            if len(selected_cat_cols)==0 or len(missing_data)==0:
                    plot_date_completness(df_merge)
                    all_texts=get_text(df_merge)
                    add_report_Date(all_texts)
            else:
                st_cols = st.columns(len(selected_cat_cols))
                selected1 = st_cols[0].selectbox(selected_cat_cols[0], missing_data[selected_cat_cols[0]].unique())
                updated_missing_data = missing_data[missing_data[selected_cat_cols[0]]==selected1]
                filter_selected = df_merge[selected_cat_cols[0]]==selected1
                try :
                    selected2 = st_cols[1].selectbox(selected_cat_cols[1], updated_missing_data[selected_cat_cols[1]].unique())
                    updated_missing_data = missing_data[missing_data[selected_cat_cols[1]]==selected2]
                    filter_selected &= df_merge[selected_cat_cols[1]]==selected2
                except:
                    pass
                try :
                    selected3 = st_cols[2].selectbox(selected_cat_cols[2], updated_missing_data[selected_cat_cols[2]].unique())
                    filter_selected &= df_merge[selected_cat_cols[2]]==selected3
                except:
                    plot_date_completness(df_merge[filter_selected])
                    all_texts=get_text(df_merge[filter_selected])
                    add_report_Date(all_texts)
        else:

            st.warning("No type of periodicity was detected")
    except:
        pass
    






