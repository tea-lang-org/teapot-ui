import re

import numpy
import pandas


class DataFrameHandler:
    def init(self, stream):
        stream.seek(0)
        self.data_frame = pandas.read_csv(stream)
        self.data_frame.columns = [re.sub("[^0-9a-zA-Z]+", "_", i) for i in self.data_frame.columns]
        self.data_frame.drop_duplicates(inplace=True)
        selected_features, eliminated_features = self.__set_selected_features()
        self.eliminated_values_information = eliminated_features
        self.data_frame = self.data_frame[selected_features]
    def init_from_data_frame(self,data_frame):
        self.data_frame=data_frame
        self.data_frame.columns = [re.sub("[^0-9a-zA-Z]+", "_", i) for i in self.data_frame.columns]
        self.data_frame.drop_duplicates(inplace=True)
        selected_features, eliminated_features = self.__set_selected_features()
        self.eliminated_values_information = eliminated_features
        self.data_frame = self.data_frame[selected_features]

    def get_columns(self):
        return list(self.data_frame.columns).copy()

    def __set_selected_features(self, missing_threshold=0.9, correlation_threshold=0.95):
        feature_matrix = self.data_frame.copy()
        feature_matrix = feature_matrix.iloc[:, ~feature_matrix.columns.duplicated()]
        feature_matrix = feature_matrix.replace({numpy.inf: numpy.nan, -numpy.inf: numpy.nan}).reset_index()

        # Find missing and percentage
        missing = pandas.DataFrame(feature_matrix.isnull().sum())
        missing['fraction'] = missing[0] / feature_matrix.shape[0]
        missing.sort_values('fraction', ascending=False, inplace=True)

        # Missing above threshold
        missing_cols = list(missing[missing['fraction'] > missing_threshold].index)
        n_missing_cols = len(missing_cols)

        # Remove missing columns
        feature_matrix = feature_matrix[[x for x in feature_matrix if x not in missing_cols]]
        message = []
        if n_missing_cols > 0:
            message.append(
                'columns with missing data threshold. ' + str(missing_threshold) + ' are ' + ' '.join(missing_cols))
        # Zero variance
        unique_counts = pandas.DataFrame(feature_matrix.nunique()).sort_values(0, ascending=True)
        zero_variance_cols = list(unique_counts[unique_counts[0] == 1].index)
        n_zero_variance_cols = len(zero_variance_cols)
        # Remove zero variance columns
        feature_matrix = feature_matrix[[x for x in feature_matrix if x not in zero_variance_cols]]
        if n_zero_variance_cols > 0:
            message.append('zero variance columns removed ' + ' '.join(zero_variance_cols))
        # remove id/ maximum occuring columns
        # max occuring id
        id_count_threshold = int(self.data_frame.shape[0] * 0.99)
        identifier_columns = list(unique_counts[unique_counts[0] >= id_count_threshold].index)
        identifier_columns.remove('index')
        if len(identifier_columns) > 0:
            feature_matrix = feature_matrix[[x for x in feature_matrix if x not in identifier_columns]]
            message.append('Identifier  columns removed:' + ' '.join(identifier_columns))
        # Correlations
        corr_matrix = feature_matrix.corr()

        # Extract the upper triangle of the correlation matrix
        upper = corr_matrix.where(numpy.triu(numpy.ones(corr_matrix.shape), k=1).astype(numpy.bool))
        to_drop = [column for column in upper.columns if any(upper[column].abs() > correlation_threshold)]

        n_collinear = len(to_drop)

        feature_matrix = feature_matrix[[x for x in feature_matrix if x not in to_drop]]
        if n_collinear > 0:
            message.append(
                'collinear columns removed with correlation above: ' + str(correlation_threshold) + ': ' + ', '.join(
                    to_drop))
        total_removed = missing_cols + zero_variance_cols + to_drop + ['index']
        columns = set(list(feature_matrix.columns))
        selected_columns = [i for i in columns if i not in total_removed]
        return selected_columns, message

    def set_target(self, target):
        self.target = target
        self.features = [i for i in self.data_frame.columns if i != target]
        self.X = self.data_frame.drop(target, axis=1)
        self.y = self.data_frame[target]
        self.X = pandas.get_dummies(self.X, drop_first=True, dummy_na=True)
        threshold = 0.70
        top_n_values = 10
        likely_categorical = []
        for column in self.data_frame.columns:
            if 1. * self.data_frame[column].value_counts(normalize=True).head(top_n_values).sum() > threshold:
                likely_categorical.append(column)
        self.categorical_features = likely_categorical
        self.numerical_features = [i for i in self.data_frame.columns if i not in self.categorical_features]
