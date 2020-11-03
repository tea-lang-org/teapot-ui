import streamlit as st

from dataframe_handler import DataFrameHandler
from statistical_module import StatisticalTests
import SessionState


def _max_width():
    max_width_str = f"max-width: 85%;"
    padding_top_str = f"padding-top:1px;"
    padding_bottom_str = f"padding-bottom:1px;"
    padding_right_str = f"padding-right:1px;"
    padding_left_str = f"padding-left:1px;"

    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
        {padding_top_str}  
        {padding_bottom_str}    
        {padding_right_str}
        {padding_left_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<style>body{background-color:#eeeeee;}</style>', unsafe_allow_html=True)

def main():
    dataframe_handler = DataFrameHandler()
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    img{
          height: auto;
          width: 90%;
    }
    </style>

    """
    _max_width()
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.markdown('# TeaPot. A drag and drop statistical test UI')
    st.markdown('## Let us start brewing')
    st.markdown('<hr style="height:5px;border-width:0;color:black;background-color:gray"> ', unsafe_allow_html=True)

    upload_file =SessionState.get(uploaded=False)
    uploaded_file = st.file_uploader("Choose a file", type=['csv'])
    if uploaded_file is not None or upload_file.uploaded:
        dataframe_handler.init(uploaded_file)
        if len(dataframe_handler.eliminated_values_information)>0:
            st.markdown('## Variables/column values removed')
            for value in dataframe_handler.eliminated_values_information:
                st.write(value)

        upload_file.uploaded=True
        st.image('tea1.png', width=200, caption='Let\'s make tea')
        st.dataframe(dataframe_handler.data_frame.head(5))
        st.image('tea2.png', width=200, caption='Select target/outcome variable')
        columns = dataframe_handler.get_columns()


        target_variable = st.selectbox('Target/Outcome', options=columns, index=len(columns) - 1)
        dataframe_handler.set_target(target_variable)

        if dataframe_handler.target in dataframe_handler.numerical_features:
            target_type = st.selectbox('type of variable: outcome', options=['interval', 'ratio','nominal', 'ordinal'])

        else:
            target_type = st.selectbox('type of variable: outcome', options=['nominal', 'ordinal','interval', 'ratio'])
        target_dictionary={'name': target_variable,'data type': target_type  }
        if target_type in ['nominal','ordinal']:
            target_dictionary['categories'] = list(dataframe_handler.data_frame[target_variable].unique())
        statistical_tests = StatisticalTests(dataframe_handler.data_frame, target_variable, target_dictionary,dataframe_handler.numerical_features,dataframe_handler.categorical_features)

        statistical_results_frame=statistical_tests.get_all_statistics_tests()

        if statistical_results_frame.shape[0]>0:
            st.image('tea3.png', width=200, caption='Black Tea is being served')
            st.dataframe(statistical_results_frame)

        independent_variable_flag=SessionState.get(selected=False)
        independent_variable = st.selectbox('Independent variable', options=dataframe_handler.features)

        if independent_variable!=None or independent_variable_flag.selected:
            independent_variable_flag.selected=True
            if independent_variable in dataframe_handler.numerical_features:
                independent_variable_type=st.selectbox('type of variable: independent', options=['interval', 'ratio','nominal', 'ordinal'])
            else:
                independent_variable_type = st.selectbox('type of variable: independent', options=['nominal', 'ordinal','interval', 'ratio'])

        experimental_design = {
            'study type': 'observational study',  # 'study type' could be 'experiment'
            'contributor variables':independent_variable ,  # 'experiment's have 'independent variables'
            'outcome variables': target_variable  # 'experiment's have 'dependent variables'
        }
        variables = [
            {
                'name': independent_variable,
                'data type': independent_variable_type,  # Options: 'nominal', 'ordinal', 'interval', 'ratio'
            },
            target_dictionary
        ]
        if independent_variable_type in ['ordinal','nominal']:
            variables[0]['categories']=list(dataframe_handler.data_frame[independent_variable].unique())
        if target_type in ['ordinal','nominal']:
            variables[1]['categories']=list(dataframe_handler.data_frame[target_variable].unique())
        available_test_types=[]
        if (independent_variable_type in ['nominal', 'ordinal']) and (target_type in ['ordinal','interval', 'ratio']):
            available_test_types.append('one sided')
            available_test_types.append('two sided')
        if len(available_test_types)>0:
            data_frame_results=statistical_tests.get_one_two_sided_permutation_tests(experimental_design,variables)
            if data_frame_results.shape[0]>0:

                st.markdown('### Serving custom tea with two sugar cubes!')
                st.dataframe(data_frame_results)
            else:
                st.markdown('### No custom tea could be served with this data')
        else:
            st.markdown('### No custom tea could be served with this data')
        userdata['custom_test']=experimental_design
    st.markdown('<h4 align = "center"><a href="https://dossiers.page">Visit Dossiers for more demos</a> </h1>', unsafe_allow_html=True)
if __name__ == "__main__":
    main()
