import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np
import plotly.figure_factory as ff
from plotly.subplots import make_subplots


date_cols = []
numerical_cols = []
######################
# Main page
######################
st.title("Statistics")

def filter_data(data,mapping):
    if len(mapping)>0:
        filters = True
        for key in mapping:
            filters &= (data[key]==mapping[key])
        return data[filters]
    else:
        return data

def agg_table(data,col_names):
    df_agg = data.groupby(col_names).agg(["sum","mean"])
    df_agg.columns=[str(s1)+"_"+s2 for (s1,s2) in df_agg.columns.tolist()]
    return df_agg.style.background_gradient(axis=0,cmap='YlOrRd')

def get_dates_values(data, date_col, col_1, col_2=None,operation=None):
    data2 = data.copy()
    if col_2 == None:
        df_return = data2.groupby(date_col,as_index=False)[col_1].sum()
        return df_return[date_col], [df_return[col_1]], [col_1]
    elif operation == "diff":
        df_return = data2.groupby(date_col,as_index=False).sum()
        df_return["diff"] = data2[col_1]-data2[col_2]
        return df_return[date_col], [df_return["diff"]], [col_1+" - "+col_2]
    elif operation =="ratio":
        df_return = data2.groupby(date_col,as_index=False).sum()
        df_return["ratio"] = data2[col_1]/data2[col_2]
        return df_return[date_col], [df_return["ratio"]], [col_1+" / "+col_2]
    elif operation =="bi-variation":
        df_return = data2.groupby(date_col,as_index=False).sum()
        return df_return[date_col], [data2[col_1],data2[col_2]], [col_1,col_2]




def plot_statistics(dates, values, labels,selected_operation):
    colors = ["#0b10a1","#a10b21"]
    df1 = pd.DataFrame()
    df1["date"] = dates
    for i in range(len(values)):
        df1[labels[i]] = values[i]
    df_stat = pd.DataFrame(df1[labels].describe()).reset_index().round(2)
    
    if  selected_operation == "bi-variation":
        colors = ["#0b10a1", "#a10b21"]
        fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
        fig.add_trace(
            go.Scatter(x=dates, y=values[0], name=labels[0],mode = 'lines',line_color=colors[0]),
            secondary_y=True,
        )

        fig.add_trace(
            go.Scatter(x=dates, y=values[1], name=labels[1],mode = 'lines',line_color=colors[1]),
            secondary_y=False,
        )

        # Add figure title
        fig.update_layout(
            title_text="Double Y Axis Example"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="xaxis title")

        # Set y-axes titles
        fig.update_layout(
        title='Dual Y-axis Plot',
        xaxis_title='Date',
        yaxis_title=labels[0],
        yaxis2_title=labels[1],
        legend=dict(x=0, y=1, traceorder='normal'),
        yaxis=dict(side='left'),
        yaxis2=dict(side='right', overlaying='y')
    )
        st.plotly_chart(fig, use_container_width=True)
        df1 = pd.DataFrame()
        df1["date"] = dates
        for i in range(len(values)):
            df1[labels[i]] = values[i]

        df_stat = pd.DataFrame(df1[labels].describe()).reset_index().round(2)
        fig_stat = ff.create_table(df_stat)
        
    
        st.plotly_chart(fig_stat, use_container_width=True)
            
    else:
        
        fig_ = ff.create_table(df_stat)
        for i in range(len(values)):
            fig_.add_trace(go.Scatter(name=labels[i],x = df1["date"].astype(str),y = df1[labels[i]],mode = 'lines',line_color=colors[i], xaxis='x2', yaxis='y2'))
        fig_.update_layout(
            margin = {'t':50, 'b':100},
            xaxis = {'domain': [0, .2]},
            xaxis2 = {'domain': [0.3, 1.]},
            yaxis2 = {'anchor': 'x2'}
        )
        fig_.layout.xaxis.tickvals = pd.date_range(str(df1["date"].min()), str(df1["date"].max()), freq='M')
        fig_.layout.xaxis.tickformat = "%m-%Y"
        fig_.update_xaxes(tickangle=-90)
        fig_.update_layout(font=dict(size=18),plot_bgcolor="white")
        st.plotly_chart(fig_, use_container_width=True)
    


   

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
    col1,col2 = st.columns([1,5])
    selected_date_col = col1.selectbox("date column : ", date_cols)
    selected_col1 = col2.selectbox("select column : ", numerical_cols)

    # selected_cat_cols = st.multiselect("categorical column(s) : ", categorical_cols, default=[],max_selections=3)
    selected_values = {}
    # if len(selected_cat_cols)>0:
    #     cols = st.columns(len(selected_cat_cols))
    #     for i,col in enumerate(cols):
    #         selected_values[selected_cat_cols[i]] = col.selectbox(selected_cat_cols[i]+" :",df[selected_cat_cols[i]].unique())
    date_range = pd.date_range(start=df[selected_date_col].min(), end=df[selected_date_col].max(), freq='D')
    date_range_df = pd.DataFrame({selected_date_col: date_range})
    # Merge the original data with the date range DataFrame
    df= pd.merge(date_range_df, df, on=selected_date_col, how='left')

    df_filtered = filter_data(df,selected_values)
    col1,col2 = st.columns(2)
    selected_operation = col1.radio("operation : ",["uni-variation","bi-variation","diff","ratio"])
    # if len(selected_cat_cols)>0:
    #     st.dataframe(agg_table(df,selected_cat_cols) ,use_container_width=True)
    empty_box = col1.empty()
    
    if selected_operation != "uni-variation":
        selected_col2 = col2.selectbox("select second column : ", numerical_cols)
        dates,values,labels = get_dates_values(df_filtered,selected_date_col,selected_col1,selected_col2,selected_operation)
        plot_statistics(dates, values, labels,selected_operation)
       
    else:
        dates,values,labels = get_dates_values(df_filtered,selected_date_col,selected_col1)
        plot_statistics(dates, values, labels,selected_operation)
       
        




