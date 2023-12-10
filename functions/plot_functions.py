import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np
import sys
from  functions.report_functions import add_report_outliers,text_report
import plotly.express as px
from plotly.subplots import make_subplots

######################
# Date_Handle page
#####################

def get_filter_combinations(data, cat_columns):
    filter_combinations = []
    cat_values = [data[column].unique() for column in cat_columns]
    cat_combinations = product(*cat_values)
    for combination in cat_combinations:
        filter_labels = []
        filter_expression = True
        for i, column in enumerate(cat_columns):
            value = combination[i]
            filter_labels.append(combination[i])
            filter_expression = filter_expression&(data[column] == value)
        filter_label = "_".join(filter_labels)
        filter_combinations.append((filter_label, filter_expression))
    return filter_combinations

def plot_date_completion(data,date_col,cat_cols):
    fig = go.Figure()
    if len(cat_cols)==0:
        fig.add_trace(go.Bar(
            x=data[date_col].sort_values().unique(),
            y=np.ones(data.shape[0]),
            name= "all"
        ))
    else:
        combinations = get_filter_combinations(data,cat_cols)
        for combination in combinations:
            dd = data[combination[1]]
            fig.add_trace(go.Bar(
                x=dd[date_col],
                y=np.ones(dd.shape[0]),
                name= combination[0]
            ))
    
    fig.layout.xaxis.tickvals
    fig.update_layout(plot_bgcolor="white",barmode='stack', xaxis_tickangle=-45)
    fig.update_layout(title=dict(text="Date completion over time"))
    st.plotly_chart(fig, use_container_width=True)

def barchart_completion(data,date_col,cat_cols,freq):
    len_date_range = len(pd.date_range(data[date_col].min(),data[date_col].max(),freq=freq))

    labels = []
    values = []
    if len(cat_cols)==0:
        labels.append("all")
        values.append(round(100*data.shape[0]/len_date_range,2))
    else:
        combinations = get_filter_combinations(data, cat_cols)
        for combination in combinations:
            labels.append(combination[0])
            values.append(round(100*data[combination[1]].shape[0]/len_date_range,2))
    fig = go.Figure(go.Bar(x=values, y=labels, orientation='h', text=values, textposition='auto'))
    fig.update_layout(font=dict(size=18),plot_bgcolor="white",title=dict(text="Date completion"))
    st.plotly_chart(fig, use_container_width=True)

def plot_date_completness(data):
    fig = go.Figure()
    view1 = data[data["_merge"].isin(["both","right_only"])]
    view2 = data[data["_merge"]=="left_only"]

    completion_ratio = round(100*view1.shape[0]/data.shape[0],2)
    fig.add_trace(go.Bar(x=view1["Date"].astype(str).unique(),
                         y=np.ones(view1.shape[0]),
                         name= "available",
                         marker_color='green'
                         ))
    fig.add_trace(go.Bar(x=view2["Date"].astype(str).unique(),
                         y=np.ones(view2.shape[0]),
                         name= "missing",
                         marker_color='#800517'
                         ))
    fig.layout.xaxis.tickvals = pd.date_range(str(data["Date"].min()), str(data["Date"].max()), freq='QS')
    fig.update_xaxes(tickangle=-90)
    fig.update_layout(yaxis={'visible': False, 'showticklabels': False})
    fig.update_layout(font=dict(size=18),plot_bgcolor="white",title=dict(text="Date completion "+str(completion_ratio)+" %"))
    st.plotly_chart(fig, use_container_width=True)

######################
# missing_values page
#####################

def plot_completion_pie(label,value,amb_value,area):
    fig = go.Figure(data=[go.Pie(
        labels=['completion','ambiguous values', 'missing values'],
        values=[value-amb_value,amb_value,100-value],
        hole=0.40,
        marker=dict(colors=['green','#e28743', '#800517'])# Set the size of the hole in the middle of the pie chart to 25%
    )])
    fig.update_layout(title=dict(text=label))
    area.plotly_chart(fig, use_container_width=True)

######################
# outliers Detections page
#####################


def plot_with_outliers(dates,values,type_ouliter,col,selected_operation,selected_col2):
    df1 = pd.DataFrame()
    df1["date"] = dates
    df1["value"] = values
    st.write(type_ouliter)
    if type_ouliter == "variation":
        df1["shift"] = df1["value"].shift(1)
        df1["diff"] = df1["value"]-df1["shift"]
        q1 = df1.describe().loc["25%","diff"]
        q3 = df1.describe().loc["75%","diff"]
        iqr = q3-q1
        upper = q3+1.5*iqr
        lower = q1-1.5*iqr
        df1.loc[df1["diff"]<lower, "var_class"] = "lower_outlier"
        df1.loc[df1["diff"]>upper, "var_class"] = "upper_outlier"
    else:
        q1 = df1.describe().loc["25%","value"]
        q3 = df1.describe().loc["75%","value"]
        iqr = q3-q1
        upper = q3+1.5*iqr
        lower = q1-1.5*iqr
        df1.loc[df1["value"]<lower, "var_class"] = "lower_outlier"
        df1.loc[df1["value"]>upper, "var_class"] = "upper_outlier"
    fig = go.Figure()
    fig.add_trace(go.Scatter(name='value',x = df1["date"].astype(str),y = df1["value"],mode = 'lines',line_color="#808080"))
    view = df1.loc[df1["var_class"]=="upper_outlier"]
    fig.add_trace(go.Scatter(name='upper_outlier',x = view["date"].astype(str),y = view["value"],mode = 'markers',line_color="#BF0000"))
    view = df1.loc[df1["var_class"]=="lower_outlier"]
    fig.add_trace(go.Scatter(name='lower_outlier',x = view["date"].astype(str),y = view["value"],mode = 'markers',line_color="#2900BF"))
    if type_ouliter=="values":
        fig.add_shape(name='upper_limit', type='line', x0=str(df1["date"].min()), y0=upper, x1=str(df1["date"].max()), y1=upper, line=dict(color='#BF0000',),)
        fig.add_shape(name='lower_limit', type='line', x0=str(df1["date"].min()), y0=lower, x1=str(df1["date"].max()), y1=lower, line=dict(color='#2900BF',),)
   
    fig.layout.xaxis.tickformat = "%d-%m-%Y"
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(font=dict(size=18),plot_bgcolor="white",title=dict(text="Outlier detection"))
    st.plotly_chart(fig, use_container_width=True)
    text=text_report(df1, type_ouliter, col, upper, lower,selected_operation, selected_col2)
    add_report_outliers(text,col)

######################
# EDA page
#####################

def plot_Distribution(df,selected_categorical_col,selected_numerical_col,unique_cat_count,selected_chart):
     if selected_categorical_col and selected_numerical_col:
        grouped_data = df.groupby(selected_categorical_col)[selected_numerical_col].sum().reset_index()      
        grouped_data = grouped_data.sort_values(by=selected_numerical_col, ascending=True)
        if selected_chart=="Pie Chart":
            # Group data by the categorical column and calculate sums of the numerical column
            # Create a Plotly pie chart
            fig = px.pie(grouped_data, names=selected_categorical_col, values=selected_numerical_col, title=f'Pie Chart: {selected_numerical_col} by{selected_categorical_col}')

            # Display the Plotly figure using Streamlit
            st.plotly_chart(fig,use_container_width=True)
        elif selected_chart=='Horizontal Bar Chart':
            # Create a horizontal bar chart using Plotly Express
            fig = px.bar(grouped_data, y=selected_categorical_col, x=selected_numerical_col, orientation='h', title=f'Distribution:  {selected_numerical_col} by{selected_categorical_col} ')
            # Display the Plotly figure using Streamlit
            st.plotly_chart(fig,use_container_width=True)
        else:

        # Create a treemap using Plotly Express
            fig = px.treemap(grouped_data, path=[selected_categorical_col], values=selected_numerical_col, title=f'Treemap: {selected_numerical_col} by{selected_categorical_col}')
        # Display the Plotly figure using Streamlit
            st.plotly_chart(fig,use_container_width=True)

def plot_single(df,selected_numerical_col,date_col,col,selected_categorical_col=[]):
    colors = ["#0b10a1", "#a10b21","#FF7F50"]
    if len(selected_categorical_col)==1:
        full_df=st.session_state["df"]
        grouped_df_ = full_df.groupby([date_col, selected_categorical_col[0]])[selected_numerical_col[0]].sum().reset_index()
        grouped_df = df.groupby([date_col, selected_categorical_col[0]])[selected_numerical_col[0]].sum().reset_index()  
        fig = go.Figure()
        for category in grouped_df_[selected_categorical_col[0]].unique():
            category_df = grouped_df[grouped_df[selected_categorical_col[0]] == category]
            fig.add_trace(go.Scatter(x=category_df[date_col], y=category_df[selected_numerical_col[0]], name=category,mode='lines'))
            fig.update_layout( title=selected_numerical_col[0]+' by '+selected_categorical_col[0]+' overtime',xaxis_title=date_col,
                yaxis_title=selected_numerical_col[0]              )
       
    else:
        grouped_df = df.groupby([date_col])[selected_numerical_col].sum().reset_index() 
        if len(selected_numerical_col)>=1:
            title=', '.join(selected_numerical_col)
            
            fig = go.Figure()
            for i in range(len(selected_numerical_col)):
                fig.add_trace(go.Scatter(name=selected_numerical_col[i],x = grouped_df[date_col].astype(str),y =  grouped_df[selected_numerical_col[i]],mode = 'lines',line_color=colors[i], xaxis='x2', yaxis='y2'))
               
            fig.layout.xaxis.tickvals = pd.date_range(str(grouped_df[date_col].min()), str(df[date_col].max()), freq='M')
            fig.layout.xaxis.tickformat = "%m-%Y"
            fig.update_xaxes(tickangle=-90)
            fig.update_layout(title=title+' overtime', xaxis_title=date_col, yaxis_title='Y-axis')
        else:
            fig = go.Figure(data=go.Scatter(x=grouped_df[date_col], y=grouped_df[selected_numerical_col[0]], mode='lines'))
    # Set plot title and axis labels
            fig.update_layout(title=selected_numerical_col[0]+' overtime', xaxis_title=date_col, yaxis_title=selected_numerical_col[0])
    # Display the Plotly figure using Streamlit
    col.plotly_chart(fig,use_container_width=True)

def plot_dual(df,selected_numerical_col,date_col,col):
    colors = ["#0b10a1", "#a10b21","#FF7F50"]
    df = df.groupby([date_col])[selected_numerical_col].sum().reset_index() 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
            # Add traces
    fig.add_trace(
            go.Scatter(name= selected_numerical_col[0],x=df[date_col], y=df[selected_numerical_col[0]],mode = 'lines',line_color=colors[0]),
            secondary_y=True,
                )
    fig.add_trace(
            go.Scatter(name= selected_numerical_col[1],x=df[date_col], y=df[selected_numerical_col[1]], mode = 'lines',line_color=colors[1]),
            secondary_y=False,
                )
    if len(selected_numerical_col)>2:
        fig.add_trace(
        go.Scatter(name= selected_numerical_col[2],x=df[date_col], y=df[selected_numerical_col[2]], mode = 'lines',line_color=colors[2]),
        secondary_y=False,
                )               
     # Add figure title
    
    # Set x-axis title
    fig.update_xaxes(title_text=date_col)
        # Set y-axes titles
    title=', '.join(selected_numerical_col)
    fig.update_layout(
    title=title+' overtime',
    xaxis_title='Date',
    legend=dict(x=10, y=1, traceorder='normal'),
    yaxis=dict(side='left',title=selected_numerical_col[0]),
    yaxis2=dict(side='right', overlaying='y',title= selected_numerical_col[1])    
    )
    col.plotly_chart(fig, use_container_width=True)



def plot_stacked(df,selected_numerical_col,date_col,col,selected_categorical_col=[]):
    colors = ["#0b10a1", "#a10b21","#FF7F50"]
    if len(selected_categorical_col)==1:
        sp=st.session_state["df"]
        grouped_df_ = sp.groupby([date_col, selected_categorical_col[0]])[selected_numerical_col[0]].sum().reset_index()
        grouped_df = df.groupby([date_col, selected_categorical_col[0]])[selected_numerical_col[0]].sum().reset_index()  
        fig = go.Figure()
     
        for category in grouped_df_[selected_categorical_col[0]].unique():
            category_df = grouped_df[grouped_df[selected_categorical_col[0]] == category]
            fig.add_trace(go.Scatter(x=category_df[date_col], y=category_df[selected_numerical_col[0]], name=category,stackgroup='one',mode='lines'))
            fig.update_layout( title=selected_numerical_col[0]+' by '+selected_categorical_col[0]+' overtime',xaxis_title=date_col, yaxis_title=selected_numerical_col[0])
        col.plotly_chart(fig, use_container_width=True)
    else:
        grouped_df = df.groupby([date_col])[selected_numerical_col].sum().reset_index()  
        fig=go.Figure()
        for i in range(len(selected_numerical_col)):
            fig.add_trace(go.Scatter(name=selected_numerical_col[i],x = grouped_df[date_col].astype(str),y =  grouped_df[selected_numerical_col[i]],mode ='lines',stackgroup='one',line_color=colors[i]))  
        fig.layout.xaxis.tickvals = pd.date_range(str(grouped_df[date_col].min()), str(grouped_df[date_col].max()), freq='M')
        fig.layout.xaxis.tickformat = "%m-%Y"
        fig.update_xaxes(tickangle=-90)
        title=', '.join(selected_numerical_col)
        fig.update_layout(font=dict(size=18),plot_bgcolor="white",title=dict(text=title+' overtime'),xaxis_title=date_col)
        col.plotly_chart(fig, use_container_width=True)

        

def multiples_plot(df,selected_numerical_col,date_col,col,selected_categorical_col=[]):
   
    if len(selected_categorical_col)==1:
        date_range = pd.date_range(start=df[date_col].min(), end=df[date_col].max(), freq='D')
        date_range_df = pd.DataFrame({date_col: date_range})
    # Merge the original data with the date range DataFrame
        df= pd.merge(date_range_df, df, on=date_col, how='left')
        grouped_df = df.groupby([date_col, selected_categorical_col[0]])[selected_numerical_col[0]].sum().reset_index()

        unique_categories = sorted(grouped_df[selected_categorical_col[0]].unique())
                      # Loop through unique categories and create a separate figure for each
        for category in unique_categories:
            category_df = grouped_df[grouped_df[selected_categorical_col[0]] == category]
            category_df= pd.merge(date_range_df, category_df, on=date_col, how='left')
            category_df=category_df.fillna(0)
            
                        # Create a new figure for each category
           
            fig = go.Figure(data=[

            go.Scatter(x=category_df[date_col], y=category_df[selected_numerical_col[0]], name=category)
                        ])

            fig.update_layout( title=f' Line Chart - Category: {category}')
           
            col.plotly_chart(fig,use_container_width=True)    
    else:
         grouped_df = df.groupby([date_col])[selected_numerical_col].sum().reset_index()  
         for num_col in selected_numerical_col:
                    fig = go.Figure(data=go.Scatter(x=grouped_df[date_col], y=grouped_df[num_col], mode='lines'))
                # Set plot title and axis labels
                    fig.update_layout(title='Line Plot '+num_col, xaxis_title='X-axis', yaxis_title='Y-axis')
                # Display the Plotly figure using Streamlit
                    col.plotly_chart(fig,use_container_width=True)

        


def plot_time_series(df,selected_numerical_col_time,categorical_columns,date_col,col='')  :
    col5,col6=st.columns(2)        
    if len(selected_numerical_col_time)==1:
        selected_categorical_col_time = col5.multiselect("select categorical column: ", options=categorical_columns,max_selections=1,key='cat_time')
        if len(selected_numerical_col_time)==1 and len(selected_categorical_col_time)==1:
            

            myslider_time = col6.radio("Chart Type : ",["one axis","stacked","multiple plots"],horizontal=True)

            if myslider_time=="one axis":
                plot_single(df,selected_numerical_col_time,date_col,col,selected_categorical_col_time)

            elif myslider_time=="stacked":
                plot_stacked(df,selected_numerical_col_time,date_col,col,selected_categorical_col_time)
            elif myslider_time=="multiple plots":
                 multiples_plot(df,selected_numerical_col_time,date_col,st,selected_categorical_col_time)             
        else:
                plot_single(df,selected_numerical_col_time,date_col,st,selected_categorical_col_time)
    elif len(selected_numerical_col_time)>1:
            df = df.groupby([date_col])[selected_numerical_col_time].sum().reset_index()
            myslider_time = col6.radio("Chart Type : ",["one axis","double axis","stacked","multiple plots"],horizontal=True)
            if myslider_time=="one axis":
                plot_single(df,selected_numerical_col_time,date_col,st,categorical_columns)

            elif myslider_time=="double axis":
                plot_dual(df,selected_numerical_col_time,date_col,st)

            elif myslider_time=="stacked":
                plot_stacked(df,selected_numerical_col_time,date_col,st)
            elif myslider_time=="multiple plots":
                multiples_plot(df,selected_numerical_col_time,date_col,st)


def plot_time_period(filtered_df_1,filtered_df_2,selected_numerical_col_period,date_col,col9,col10,col11,selected_categorical_col_period):
    
    if len(selected_numerical_col_period)==1 :
        if   len(selected_categorical_col_period)==1 :
            myslider_period = col9.radio("Chart Type : ",["one axis","stacked","multiple plots"],horizontal=True,key=1)
                    # Display the Plotly figure using Streamlit
            if  myslider_period=="one axis":
                plot_single(filtered_df_1,selected_numerical_col_period,date_col,col10,selected_categorical_col_period)
                plot_single(filtered_df_2,selected_numerical_col_period,date_col,col11, selected_categorical_col_period)
            elif myslider_period=='stacked':
            
                plot_stacked(filtered_df_1,selected_numerical_col_period,date_col,col10,selected_categorical_col_period)
                plot_stacked(filtered_df_2,selected_numerical_col_period,date_col,col11,selected_categorical_col_period)
            elif myslider_period=='multiple plots':
                multiples_plot(filtered_df_1,selected_numerical_col_period,date_col,col10,selected_categorical_col_period)
                multiples_plot(filtered_df_2,selected_numerical_col_period,date_col,col11,selected_categorical_col_period)
        else:
            plot_single(filtered_df_1,selected_numerical_col_period,date_col,col10, selected_categorical_col_period)
            plot_single(filtered_df_2,selected_numerical_col_period,date_col,col11, selected_categorical_col_period)
    else:
        myslider_period = col9.radio("Chart Type : ",["one axis","double axis","stacked","multiple plots"],horizontal=True,key=2)
        if myslider_period=='one axis':
            plot_single(filtered_df_1,selected_numerical_col_period,date_col,col10)
            plot_single(filtered_df_2,selected_numerical_col_period,date_col,col11)
        elif myslider_period=='double axis':
            plot_dual(filtered_df_1,selected_numerical_col_period,date_col,col10)
            plot_dual(filtered_df_2,selected_numerical_col_period,date_col,col11)
        elif myslider_period=='stacked':
            plot_stacked(filtered_df_1,selected_numerical_col_period,date_col,col10)
            plot_stacked(filtered_df_2,selected_numerical_col_period,date_col,col11)
        elif myslider_period=='multiple plots':
            multiples_plot(filtered_df_1,selected_numerical_col_period,date_col,col10)
            multiples_plot(filtered_df_2,selected_numerical_col_period,date_col,col11)
