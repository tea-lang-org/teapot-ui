import os
import sys
import traceback
import matplotlib.pyplot as plt
import numpy
import pandas
import six
import tea

class StatisticalTests:

    def __init__(self, data_frame, target,target_category_dictionary,numeric_variables, categorical_variables):
        self.data_frame = data_frame
        self.target = target
        self.target_category_dictionary=target_category_dictionary
        self.numeric_variables=numeric_variables
        self.categorical_variables=categorical_variables
    def set_study_design(self,variable_definitions,study_design):
        self.study_design = study_design
        self.variable_definitions = variable_definitions


    def get_relation_status(self,string_value):
        if "no" in string_value.lower():
            return 'False'
        return 'True'


    def blockPrint(self):
        sys.stdout = open(os.devnull, 'w')
        # Restore

    def enablePrint(self):
        sys.stdout = sys.__stdout__

    def get_all_statistics_tests(self):
        results = []
        #
        self.blockPrint()
        for current_variable in self.numeric_variables:
            # current_variable='Total_Revolving_Consumer_Credit_Owned_and_Securitized_number_crossing_m_m_minus1_h36'
            tea.data(self.data_frame)
            variables = [
                {
                    'name': current_variable,
                    'data type': 'interval'  # Options: 'nominal', 'ordinal', 'interval', 'ratio'
                },
                self.target_category_dictionary
            ]

            tea.define_variables(variables)
            experimental_design = {
                'study type': 'observational study',  # 'study type' could be 'experiment'
                'contributor variables': current_variable,  # 'experiment's have 'independent variables'
                'outcome variables': self.target,  # 'experiment's have 'dependent variables'
            }
            tea.define_study_design(experimental_design)
            test_part = [current_variable + ' ~ ' + self.target]
            try:
                results.append(tea.hypothesize([current_variable, self.target], test_part))
            except:
                pass

        for current_variable in self.categorical_variables:
            # current_variable='Total_Revolving_Consumer_Credit_Owned_and_Securitized_number_crossing_m_m_minus1_h36'

            tea.data(self.data_frame)
            variables = [
                {
                    'name': current_variable,
                    'data type': 'nominal',  # Options: 'nominal', 'ordinal', 'interval', 'ratio'
                    'categories': self.data_frame[current_variable].unique()
                },
                self.target_category_dictionary
            ]
            tea.define_variables(variables)
            experimental_design = {
                'study type': 'observational study',  # 'study type' could be 'experiment'
                'contributor variables': current_variable,  # 'experiment's have 'independent variables'
                'outcome variables': self.target,  # 'experiment's have 'dependent variables'
            }
            tea.define_study_design(experimental_design)
            test_part = [current_variable + ' ~ ' + self.target]
            try:
                results.append(tea.hypothesize([current_variable, self.target], test_part))
            except:
                pass
            test_part = [current_variable + ' ~ -' + self.target]
            try:
                results.append(tea.hypothesize([current_variable, self.target], test_part))
            except:
                pass
        results_frame = pandas.DataFrame()
        for i in range(len(results)):
            for test_result in results[i].get_all_test_results():
                print (test_result)
                for i in test_result.interpretation.split('.'):
                    result_dict = dict()
                    null_hypothesis = test_result.get_null_hypothesis()
                    feature_name = null_hypothesis[
                                   null_hypothesis.find('between ') + len('between '):null_hypothesis.rfind(
                                       ' and ')]
                    feature_name = feature_name.split(' or ')[0]
                    feature_name = feature_name.split(' on ')[0]
                    feature_name = feature_name.split(' = ')[0]

                    feature_name = feature_name.strip()
                    result_dict['feature'] = feature_name
                    if 'There' in i:
                        result_dict['test_name'] = test_result.name
                        result_dict['result'] = i.split('between')[0]
                        result_dict['Adjusted P Value'] = round(test_result.adjusted_p_value, 4)
                        result_dict['Test statistic'] = test_result.test_statistic
                        results_frame = results_frame.append(result_dict, ignore_index=True)
        #self.enablePrint()

        if results_frame.shape[0]<=0:
            return results_frame
        try:
            print(results_frame.head())
            results_frame.sort_values(by='Adjusted P Value',inplace=True)
            results_frame['Test statistic'] = results_frame['Test statistic'].apply(lambda x: round(x,2))
            result_relation_column='Relation with '+self.target
            results_frame[result_relation_column]=results_frame.result.apply(lambda x: self.get_relation_status(x))
            if results_frame.shape[0]<=0:
                return False
            self.result_frame=results_frame[['feature', 'test_name', 'Test statistic', 'Adjusted P Value',result_relation_column]].copy()
            self.result_frame.drop_duplicates(inplace=True)
            return self.result_frame
        except:
            traceback.print_exc()
            return results_frame
        return self.result_frame

    def get_one_two_sided_permutation_tests(self,experimental_design,variables):
        self.results=[]
        independent_variable=variables[0]['name']
        target_variable=variables[1]['name']
        if variables[0]['data type'] in ['nominal','ordinal']:
            import itertools
            pairs = list(itertools.permutations(list(self.data_frame[independent_variable].unique()), 2))
            print(len(pairs) ," pairs generated ")
            for pair in pairs:
                tea.data(self.data_frame)
                tea.define_variables(variables)
                tea.define_study_design(experimental_design)
                hypothesis=[independent_variable+':'+str(pair[0])+' > '+str(pair[1])]
                print([independent_variable,target_variable ], hypothesis)
                self.enablePrint()
                #tea.hypothesize([independent_variable,target_variable ], hypothesis)
                #self.blockPrint()

                try:
                    #self.results.append(tea.hypothesize(['drug', 'wedsBDI'], ['drug:Ecstasy > Alcohol']))
                    #print('result inside hypothesis test' ,len(self.results))
                    self.results.append(tea.hypothesize([independent_variable,target_variable ], hypothesis))
                except:
                    print ('exception in ', hypothesis)
                    traceback.print_exc()

                    #traceback.print_exc()
                    continue
                #self.enablePrint()
        print (len(self.results))
        results_frame = pandas.DataFrame()
        if len(self.results)==0:
            return results_frame
        for i in range(len(self.results)):
            for test_result in self.results[i].get_all_test_results():
                result_dict = dict()
                #print (test_result.interpretation)
                result_dict['test_name'] = test_result.name
                result_dict['Adjusted P Value'] = round(test_result.adjusted_p_value, 4)
                result_dict['Test statistic'] = test_result.test_statistic
                results_frame = results_frame.append(result_dict, ignore_index=True)
                result_relation_column = 'Relation with ' + self.target
                if 'Reject' in test_result.interpretation:
                    results_frame[result_relation_column] =True
                else:
                    results_frame[result_relation_column] = False
        results_frame.drop_duplicates(inplace=True)
        results_frame.sort_values(by='Adjusted P Value', inplace=True)
        results_frame['Test statistic'] = results_frame['Test statistic'].apply(lambda x: round(x, 2))
        results_frame['feature']=independent_variable
        results_frame = results_frame[
            ['feature', 'test_name', 'Test statistic', 'Adjusted P Value', result_relation_column]]
        return results_frame