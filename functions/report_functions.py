import streamlit as st
import pandas as pd
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

        /* Change the text color when the input is focused */
        div.stTextInput > div > div > input[type="text"]:focus {
            border-color: #e74c3c;
            color: #3D3D3D;
        }
       
        .stTextArea textarea {
            background-color: #3D3D3D;
            color : white
            }
        </style>
        """
######################
# Date_Handle page
#####################

def get_text(df_merge):
    Date = df_merge['Date'].tolist()
    merge = df_merge['_merge'].tolist()
    liste_date_final = []
    liste_date = []
    list_range = []
    n = 0
    k = 0
    
    
            
    for i in range(0, len(merge)):
        if merge[i] == 'left_only':
        
            liste_date.append(Date[i])
            
            n = n + 1 
        else:   
            if len(liste_date) >= 3:
                    list_range.append([liste_date[0], liste_date[-1], n])
                    n = 0
                    liste_date.clear()
            if liste_date:
                for i in liste_date:
                    liste_date_final.append(i)
    unique_list_dates = []

    [unique_list_dates.append(item) for item in liste_date_final if item not in unique_list_dates]
    liste_date_final=unique_list_dates
    if len(list_range) > 3:
        list_range = list_range[0:3]
            
    if len(liste_date_final) > 3:
        liste_date_final = liste_date_final[0:3]
                
    text = ""
    list_text = []
    
    if liste_date_final:
        list_date_str = [str(i) + '    ' for i in liste_date_final]
        text = ' missing dates in ' + str(list_date_str[:]).replace('[', '').replace(']', '').replace("'", '') + '. . . '
        list_text = [text]
        
    if list_range:
        for i in list_range:
            text = ' missing dates from ' + str(i[0]) + ' to ' + str(i[1])
            list_text.append(text)
        all_texts = "\n".join(list_text) + '  \n . . .'
      
    return all_texts


def add_report_Date(all_texts):
    st.markdown(css, unsafe_allow_html=True)
    
    # Beautiful text input
    report = st.text_area("missing Dates report ", all_texts.replace('00:00:00', ''), key="my_text_area")

    list_text = report.split("\n")
    text_final = ''
    for i in list_text:
        text_final = text_final + i

    col1, col2 = st.columns(2)
    button_container = col1.empty()
    
    if button_container.button('add to report '):
        st.session_state['report'].loc[len(st.session_state['report'])] = [ st.session_state['names'], 'missing Dates', text_final.replace('00:00:00', '')]
######################
# missing_values page
#####################

def get_error_rows(df,other_strings=st.session_state['filters']):
    list_col=[]
    other_strings_=[i for i in other_strings if i!='white space' and i!='negative values' and i!='zero values'] 
    for col in df.columns:
        list_values=[]
        text_negative=''
        text_space=''
        text_zero=''
        if df[col].isnull().sum()>0:
            text_missing= 'missing values in the column '+col +' are in ' +  str(df[col].isnull().sum() )+' rows \n'
            list_values.append(text_missing)

        if df[col].dtype in ['float64', 'int64']:    
            if 'negative values' in other_strings:
                    
                sum_negatives = 0
                # Use boolean indexing to filter rows with negative values in the specified column
                negative_values = df[df[col] < 0]
                # Calculate the sum of negative values in the specified column
                sum_negatives = negative_values[col].count()
                if sum_negatives>0:
                    text_negative='negative values in the column '+col +' are in ' +str(sum_negatives)+' rows \n'   
                    list_values.append(text_negative)
           
            if 'zero values' in other_strings:
                 
                sum_zeros=0 
                zero_values = df[df[col] == 0]
                # Calculate the sum of negative values in the specified column
                sum_zeros = zero_values[col].count()
                if sum_zeros>0:
                    text_zero='zero values in the column '+col +' are in ' +str(sum_zeros)+' rows \n'   
                    list_values.append(text_zero)
         
        if df[col].dtype in  ['object']:
            if 'white space' in other_strings:
                if df[col].astype(str).str.isspace().sum()>0:
                    text_space= 'white space in the column '+col +' are in '+ str(df[col].astype(str).str.isspace().sum()) +' rows \n'
                    list_values.append(text_space)
            for filter in other_strings_:
                n=0
                text_filter=''
                for value in df[col]:
                    if filter==value:
                        n=n+1
                if n>0:
                    text_filter='filter '+filter+' in the column '+col +' are in '+str(n)+' rows \n'
                    list_values.append(text_filter)
        if len(list_values)>0:
            list_col.append(list_values)

    return list_col

def add_report_missing(col,text):
    report= st.text_area("report for column "+col,text  ,key=col )
    col3,col4=st.columns(2)
    button_container_2 = col3.empty()
    if button_container_2.button('add to report ',key='but_'+col):
        for sentence in text.split('\n'):
            for word in sentence.split() :
                if word=='missing':
                    st.session_state['report'].loc[len(st.session_state['report'])] = [st.session_state['names'],'missing values', sentence]
                    break
                else:
                    st.session_state['report'].loc[len(st.session_state['report'])] = [st.session_state['names'],'ambiguous values', sentence]
                    break

        st.success(' successfully added to report ', icon="✅")

#########################""
# outliers Detections page
###########################


def get_value_text(df, value_df, col, upper_or_lower,type_outlier, selected_operation, selected_col2, upper_or_lower_value=0):
    list_values = []
    for index in value_df.index:
        row = value_df.loc[index]
        list_values.append((row['date'].strftime('%Y-%m-%d'), row['value']))

    text = ''
    if len(list_values) > 0:
        if len(list_values) > 3:
            list_values = list_values[:3]

        if type_outlier == 'values':
            if selected_operation == 'uni-variation':
                text = f'for the column {col}, we present values {upper_or_lower} than {round(upper_or_lower_value,2)} ' \
                       f'in {str([i[0] for i in list_values])}\n'
            elif selected_operation == 'diff':
                text = f'for the difference between {col} and {selected_col2}, we present values {upper_or_lower} ' \
                       f'than {round(upper_or_lower_value,2)} in {str([i[0] for i in list_values])}\n'
            else:
                text = f'for the ratio {col} by {selected_col2}, we present values {upper_or_lower} than ' \
                       f'{round(upper_or_lower_value,2)} in {str([i[0] for i in list_values])}\n'
        else:
            if selected_operation == 'uni-variation':
                text = f'for the column {col}, we present  {upper_or_lower}  ' \
                       f'in {str(sorted([i[0] for i in list_values]))}\n'
            elif selected_operation == 'diff':
                text = f'for the difference between {col} and {selected_col2}, we present  {upper_or_lower} ' \
                       f' in {str(sorted([i[0] for i in list_values]))}\n'
            else:
                text = f'for the ratio {col} by {selected_col2}, we present  {upper_or_lower} ' \
                       f' in {str(sorted([i[0] for i in list_values]))}\n'
        if len(list_values) >= 3:
            text += '...'

    return text.replace("['", '').replace("']",'').replace("',",' ').replace("'",'')


def text_report(df1, type_outlier, col, upper, lower,selected_operation,selected_col2):
    text = ''
    text_variation=''
    text_upper=''
    text_lower=''

    upper_df = df1[df1['var_class'] == 'upper_outlier']
    lower_df = df1[df1['var_class'] == 'lower_outlier']
    variation_df = pd.concat([upper_df, lower_df])
    variation_df = variation_df.sort_values(by="date")

    if type_outlier == 'values':
        text_upper = get_value_text(df1, upper_df, col, 'upper' ,type_outlier, selected_operation, selected_col2,upper)
        text_lower = get_value_text(df1, lower_df, col, 'lower',type_outlier, selected_operation, selected_col2, lower)
    else:
        text_variation = get_value_text(df1, variation_df, col, 'variation', type_outlier, selected_operation, selected_col2,upper)

    text = text_upper + text_lower + text_variation
    return text


def add_report_outliers(text,col):
    if len(text) > 0:
        st.markdown(css, unsafe_allow_html=True)
        report = st.text_area("report for column " + col, text, key=col)
        col3, col4 = st.columns(2)
        button_container_2 = col3.empty()
        if button_container_2.button('add to report ', key='but_' + col):
            st.session_state['report'].loc[len(st.session_state['report'])] = [st.session_state['names'], 'outlier values', text]
