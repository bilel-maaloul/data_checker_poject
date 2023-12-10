import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np
try:
    from functions.report_functions import get_error_rows,add_report_missing
    from functions.plot_functions import  plot_completion_pie
except:
    pass
pd.set_option("styler.render.max_elements", 999_999_999_999)


if 'filters'  in st.session_state:
   list_filters=  st.session_state['filters'] 
else:
    list_filters= ['white space', 'negative values','zero values']

if 'options'  in st.session_state:
    options=  st.session_state['options']

else:
    options = ['white space', 'negative values','zero values']




def get_ambiguous_values(data, cat_cols,num_cols,other_strings=list_filters):
    
    cat_cols = [col for col in data.columns if col in cat_cols]
    num_cols = [col for col in data.columns if col in num_cols]
    filters = pd.Series(False, index=data.index)

    if 'negative values' in other_strings:
        filters |= (data[num_cols] < 0).sum(axis=1) > 0

    if 'zero values' in other_strings:
        filters |= (data[num_cols] == 0).sum(axis=1) > 0
        
    for col in cat_cols:
        if 'white space' in other_strings:  
            filters|= data[col].astype(str).str.isspace()


        filters|= data[col].astype(str).isin([i for i in other_strings if i!='white space' and i!='negative values' and i!='zero values'])

    return filters



            


# Create a function to apply the background color and text color based on conditions
def define_color_background(value, ambiguous_strings=list_filters):
    condition_ambiguous = str(value).isspace()|(value in ambiguous_strings)|(isinstance(value, (int, float)) and value < 0)|(isinstance(value, (int, float)) and value ==0 )
    if condition_ambiguous:
        return 'background-color: rgba(226, 135, 67, 0.5); color: black'
    elif pd.isnull(value):
        return 'background-color: rgba(128, 5, 23, 0.5); color: white'
    else:
        return ''


######################
# Main page
######################
st.title("Missing Values")

if "df" not in st.session_state:
    st.warning("input data before moving to this page")
else:
    
    
    df = st.session_state["df"]
    st.dataframe(df.head())
    st.markdown("# filters for Ambiguous values ")
    

    filters = st.text_input("Add filters  (all added filters will be saved in the select filters)")
    
    col1, col2 = st.columns(2)
    button_container = col1.empty()

    if button_container.button('Add to filters',key='add'):
         
        
            if filters not in st.session_state['filters']:
                if filters in options:
                    st.warning("the input already exists in the options of select_column")
                else:
                    st.session_state['filters'].append(filters)
            else:
                  st.warning("the input already exists")
                  

    # Refresh the selected columns with updated options
    
    try:
        
        selected_cols = st.multiselect("Select filters: ", options=options,default=list_filters)
    except:
       
        for i in list_filters:
            if i not in options:
                options.append(i)
        selected_cols = st.multiselect("Select filters: ", options=options,default=list_filters)


    st.session_state['options']=options
    list_options=list_filters
    col3, col4 = st.columns(2)
    button_container_ = col3.empty()

    list_filters=selected_cols
    
    if list_filters!=st.session_state['filters']:
        st.session_state['filters']=list_filters
        st.experimental_rerun()
    
    default_types_map = dict(df.dtypes)
    categorical_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['object']]
    date_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['datetime64[ns]']]
    
         
    numerical_cols = [col for col in default_types_map.keys() if default_types_map[col] in ['float64', 'int64']]
   
    completion_all = round((100*df.notna().sum()/df.shape[0]).mean(),2)
    ambiguous_prop = round((100*get_ambiguous_values(data=df,cat_cols=categorical_cols,num_cols=numerical_cols).sum()/df.shape[0]).mean(),2)
    plot_completion_pie("All",completion_all,ambiguous_prop,st)
    # selected_ambiguous_values = []
    st.write("*Ambiguous values can be white spaces, negative values and zero values ")
    # col1,col2,col3 = st.columns(3)
    # value_to_add = col1.text_input('Add ambiguous value')
    #
    # # # If the user enters some text, append it to the list
    # # if value_to_add:
    # #     selected_ambiguous_values.append(value_to_add)
    #
    #
    # if col2.button("add"):
    #     selected_ambiguous_values.append(value_to_add)
    #
    # selected_ambiguous_values = col3.multiselect("selected ambiguous values",selected_ambiguous_values)
    # st.write(selected_ambiguous_values)
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
    
    list_values=get_error_rows(df)
    
    n=0
    for col in df.columns:
        completion_col = round((100*df[[col]].notna().sum()/df.shape[0]).mean(),2)
        ambiguous_filter = get_ambiguous_values(df[[col]],categorical_cols,numerical_cols)
        ambiguous_prop_col = round((100*ambiguous_filter.sum()/df.shape[0]).mean(),4)
       
       
        text=''
        if completion_col<100 or ambiguous_filter.sum()>0:
            col1,col2 = st.columns([1,2])
            plot_completion_pie(col,completion_col,ambiguous_prop_col,col1)
            col2.dataframe(df[df[col].isna()|ambiguous_filter].head(40).style.applymap(define_color_background, subset=[col]))
            st.markdown(css, unsafe_allow_html=True)
            for part_text in list_values[n]:
                text=text+part_text   
            n=n+1
            add_report_missing(col,text)
            st.write("________________________________________________________________")
    