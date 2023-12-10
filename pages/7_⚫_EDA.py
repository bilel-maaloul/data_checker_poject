import pandas as pd
import numpy as np
import streamlit as st
import sys
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from functions.plot_functions import plot_Distribution,plot_time_series,plot_time_period
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb 
if  "filters" not in st.session_state:
     st.session_state['filters']= ['white space', 'negative values','zero values']
     
if  "report" in st.session_state:
    df_report= st.session_state['report']
else :
     st.session_state['report']= pd.DataFrame({
                        'file names': [],
                        'Type of issue': [],
                         'Description' :[]})
     df_report= st.session_state['report']
if  "names" in st.session_state:
     list_names= st.session_state['names'] 
else:
      st.session_state['names']=''

if "df" in st.session_state:
    df = st.session_state["df"]

else :
    df = pd.DataFrame()

def calculate_variation(old_value, new_value):
    return ((new_value - old_value) / old_value) * 100


def prepare_variation_table(from_period1,from_period2,filtered_df_1,filtered_df_2):
    

    variation_table={
        'Columns': [],
        'period from '+str(from_period1): [],
        'period from '+str(from_period2): [],
        'variation%': []
    }
    variation_table=pd.DataFrame(variation_table)
    total_period_1=0
    total_period_2=0
    total_variation=0
    for col in selected_numerical_col_period:
            period1_sum=filtered_df_1[col].sum()
            period2_sum=filtered_df_2[col].sum()
            total_period_1+=period1_sum
            total_period_2+=period2_sum
            variation=calculate_variation(period1_sum,period2_sum)
            total_variation+=variation
            
            

            new_col={'Columns':col,
                 'period from '+from_period1:currency+'{:.2f}'.format(period1_sum ) ,
                'period from '+str(from_period2):currency+ '{:.2f}'.format(period2_sum ),
                'variation%' :variation}
            new_row_index = len(variation_table)
            variation_table.loc[new_row_index] = new_col
   
    total={'Columns':'total',
                 'period from '+from_period1:currency+'{:.2f}'.format(total_period_1) ,
                'period from '+str(from_period2):currency+ '{:.2f}'.format(total_period_2 ),
                'variation%' :total_variation }
    new_row_index = len(variation_table)
    variation_table.loc[new_row_index] = total

    return variation_table
     
def prepare_proportion_table(from_period1,from_period2,filtered_df_1,filtered_df_2):
    proportion_table={
        'Columns': [],
        'period from '+str(from_period1): [],
        'prop %': [],
        'period from '+str(from_period2): [],
        'prop_%': [],
        'variation%': []
    }
    
    proportion_table=pd.DataFrame(proportion_table)
    try:
        try:
            
            category_sums_total_1 = filtered_df_1[selected_numerical_col_period[0]].sum()
            category_sums_total_2 = filtered_df_2[selected_numerical_col_period[0]].sum()
            category_sums_1 = filtered_df_1.groupby(selected_categorical_col_period[0])[selected_numerical_col_period[0]].sum()
            category_sums_2 = filtered_df_2.groupby(selected_categorical_col_period[0])[selected_numerical_col_period[0]].sum()
          
            
            
            # Filter the dataframes based on uncommon categories
            uncommon_categories_1 = category_sums_1.index.difference(category_sums_2.index)
            uncommon_categories_2 = category_sums_2.index.difference(category_sums_1.index)

            category_sums_uncommon_1 = category_sums_1[category_sums_1.index.isin(uncommon_categories_1)]
            category_sums_uncommon_2 = category_sums_2[category_sums_2.index.isin(uncommon_categories_2)]


            # Filter the dataframes based on common categories
            common_categories = category_sums_1.index.intersection(category_sums_2.index)
            category_sums_1 = category_sums_1[category_sums_1.index.isin(common_categories)]
            category_sums_2 = category_sums_2[category_sums_2.index.isin(common_categories)]
        
        except:
             pass
        
        sum_prop_1=0
        sum_prop_2=0
        sum_variation=0
        
        for i in range(len(category_sums_1)):
            
            sum_period1=category_sums_1[i]
            sum_period2=category_sums_2[i]
            prop1=(sum_period1/category_sums_total_1)*100
            prop2=(sum_period2/category_sums_total_2)*100
            sum_prop_1+=prop1
            sum_prop_2+=prop2
            variation_prop=calculate_variation(sum_period1,sum_period2)
            sum_variation=sum_variation+variation_prop
            name_col= selected_numerical_col_period[0]+'_'+common_categories[i]
           

            new_col={'Columns':name_col,
                    'period from '+str(from_period1):currency+'{:,.2f}'.format(sum_period1 ),
                    'prop %': '{:.2f}'.format(prop1) ,
                    'period from '+str(from_period2): currency+'{:,.2f}'.format(sum_period2 ),
                    'prop_%':'{:.2f}'.format(prop2) ,
                    'variation%' :variation_prop.round(2),
                    }
            new_row_index = len(proportion_table)
            proportion_table.loc[new_row_index] = new_col
            
        for i in range(len(category_sums_uncommon_1)):
            sum_period1=category_sums_uncommon_1[i]
            prop1=(sum_period1/category_sums_total_1)*100
            sum_prop_1+=prop1
            name_col= selected_numerical_col_period[0]+'_'+uncommon_categories_1[i]
            new_col={'Columns':name_col,
                    'period from '+str(from_period1):currency+'{:,.2f}'.format(sum_period1 ),
                    'prop %': '{:.2f}'.format(prop1) ,
                    'period from '+str(from_period2): '-',
                    'prop_%':'-' ,
                    'variation%' :float('{:.2f}'.format(0)),
                    }
            new_row_index = len(proportion_table)
            proportion_table.loc[new_row_index] = new_col
        for i in range(len(category_sums_uncommon_2)):
            sum_period2=category_sums_uncommon_2[i]
            prop2=(sum_period2/category_sums_total_2)*100
            sum_prop_2+=prop2
            name_col= selected_numerical_col_period[0]+'_'+uncommon_categories_2[i]
            new_col={'Columns':name_col,
                    'period from '+str(from_period1):'-',
                    'prop %':'-' ,
                    'period from '+str(from_period2):currency+'{:,.2f}'.format(sum_period2 ),
                    'prop_%': '{:.2f}'.format(prop2) ,
                    'variation%' :0,
                    }
            new_row_index = len(proportion_table)
            proportion_table.loc[new_row_index] = new_col
             
             
       
        total= {'Columns':'total',
                    'period from '+str(from_period1):currency+'{:,.2f}'.format(category_sums_total_1 ),
                    'prop %': '{:,.2f}'.format(sum_prop_1) ,
                    'period from '+str(from_period2):currency+ '{:,.2f}'.format(category_sums_total_2 ),
                    'prop_%':'{:,.2f}'.format(sum_prop_2) ,
                    'variation%' :round(sum_variation,2),
                    }
        new_row_index = len(proportion_table)
        proportion_table.loc[new_row_index]=total
    except:
         pass
    return proportion_table

def color_negative_red(value):
    if value >0:
        return 'background-color: rgba(0, 128, 0, 0.3); color: black'
    else:
        return 'background-color: rgba(255, 0, 0, 0.3); color: black'
         

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  # Explicitly set the engine to 'xlsxwriter'
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()  # Close the writer, which writes the data to the output buffer
    processed_data = output.getvalue()
    return processed_data

def present_table(selected_numerical_col_period,selected_categorical_col_period,proportion_table,variation_table):
    if len(selected_numerical_col_period)==1:
        if selected_categorical_col_period:
            st.dataframe(proportion_table.style.applymap(color_negative_red,subset=['variation%'])
                ,use_container_width=True,hide_index=True, column_config={'Variation%': {'format': '{::2%}'}})
            df_xlsx = to_excel(proportion_table)
            st.download_button(label='📥 Download proprtion table',
                   data=df_xlsx,
                   file_name='proprtion_table.xlsx',
                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
        else:
            st.dataframe(variation_table.style.applymap(color_negative_red,subset=['variation%']),use_container_width=True,hide_index=True)
            df_xlsx = to_excel(variation_table)
            st.download_button(label='📥 Download variation table',
                    data=df_xlsx,
                    file_name=' variation_table.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.dataframe(variation_table.style.applymap(color_negative_red,subset=['variation%']),use_container_width=True,hide_index=True)
        df_xlsx = to_excel(variation_table)
        st.download_button(label='📥 Download variation table',
                    data=df_xlsx,
                    file_name=' variation_table.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


st.title("Distribution")
categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
numerical_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()
col1,col2,col3=st.columns(3)
selected_categorical_col = col1.multiselect("select categorical column: ", options=categorical_columns,max_selections=1,key='cat')
selected_numerical_col = col2.multiselect("select numerical column: ", options=numerical_columns,max_selections=1,key='num')
if selected_categorical_col and selected_numerical_col:
    categorical_col = selected_categorical_col[0]
    numerical_col = selected_numerical_col[0]

    unique_cat_count = df[selected_categorical_col].nunique()
    if  unique_cat_count[0]>=2 and unique_cat_count[0]<=6:
         selected_chart=col3.radio("Chart Type : ",["Pie Chart", "Horizontal Bar Chart","Treemap"],horizontal=True)
    elif unique_cat_count[0]>=7 and unique_cat_count[0]<=14:
        selected_chart=col3.radio("Chart Type : ",["Horizontal Bar Chart","Pie Chart", "Treemap"],horizontal=True)
    elif unique_cat_count[0]>14:
         selected_chart= selected_chart=col3.radio("Chart Type : ",["Treemap","Pie Chart", "Horizontal Bar Chart",],horizontal=True)



    plot_Distribution(df,selected_categorical_col[0],selected_numerical_col[0],unique_cat_count,selected_chart)


st.title("Time series")

col4,col5,col6=st.columns(3)
selected_numerical_col_time = col4.multiselect("select numerical column: ", options=numerical_columns,max_selections=3,key='num_time')
try:
    default_types_map = dict(df.dtypes)
    date_col = [col for col in default_types_map.keys() if default_types_map[col] in ['datetime64[ns]']][0]
    if date_col:
        date_range = pd.date_range(start=df[date_col].min(), end=df[date_col].max(), freq='D')
        date_range_df = pd.DataFrame({date_col: date_range})
        # Merge the original data with the date range DataFrame
        df= pd.merge(date_range_df, df, on=date_col, how='left')     
    plot_time_series(df,selected_numerical_col_time,categorical_columns,date_col,st) 
except:
     pass


st.title("period comparison")

col7,col8,col9=st.columns(3)
selected_numerical_col_period = col7.multiselect("select numerical column: ", options=numerical_columns,max_selections=3,key='num_period')
try:
    if len(selected_numerical_col_period)==1:
            selected_categorical_col_period = col8.multiselect("select categorical column: ", options=categorical_columns,max_selections=1,key='cat_period')
    else:
        selected_categorical_col_period=col8.empty()
    col10,col11=st.columns(2)
    col12,col13=col10.columns(2)
    from_period1= pd.to_datetime( col12.date_input("from period 1",key='from1'))
    to_period1= pd.to_datetime(col13.date_input("to period 1",key='to1'))
    col14,col15=col11.columns(2)
    from_period2= pd.to_datetime(col14.date_input("from period 2",key='from2'))
    to_period2= pd.to_datetime(col15.date_input("to period 2",key='to2') ) 
    col16,col17=st.columns(2)
    currency=''
    checkbox_value = col16.checkbox("Money")
    if checkbox_value:
        money=col17.radio('operation: ',['Euro','Dollar'],horizontal=1)
        if money=='Euro':
            currency='€'
        else:
            currency='$'

    filtered_df_1 = df[(df[date_col] >= from_period1) & (df[date_col] <= to_period1)]
    filtered_df_2 = df[(df[date_col] >= from_period2) & (df[date_col] <= to_period2)]
    from_period1=str(from_period1).replace('00:00:00','')
    from_period2=str(from_period2).replace('00:00:00','')


    plot_time_period(filtered_df_1,filtered_df_2,selected_numerical_col_period,date_col,col9,col10,col11,selected_categorical_col_period)
    proportion_table=prepare_proportion_table(from_period1,from_period2,filtered_df_1,filtered_df_2)
    variation_table=prepare_variation_table(from_period1,from_period2,filtered_df_1,filtered_df_2)
    proportion_table['variation%']=proportion_table['variation%'].astype('int')
    variation_table['variation%']=variation_table['variation%'].astype('int')
    present_table(selected_numerical_col_period,selected_categorical_col_period,proportion_table,variation_table)
                  
except :
    pass



                



        
            
                    
        