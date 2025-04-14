import pandas as pd
from pandas import DataFrame
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier
from src.data_service_request import fetch_animals

def _remove_outliers_iqr(df: DataFrame) -> DataFrame:
    """
    Removes outliers from numeric columns using the IQR (InterQuartile Range) method, grouped by animal type.

    :param df: Input DataFrame containing animal features and labels.
    :return: Filtered DataFrame with outliers removed.
    """

    df_filtered = pd.DataFrame()
    cols_to_filter = ['height', 'weight']

    for name, group in df.groupby('animal_type'):
        original_count = len(group)
        group_filtered = group.copy()

        for col in cols_to_filter:
            Q1 = group[col].quantile(0.25)
            Q3 = group[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            group_filtered = group_filtered[
                (group_filtered[col] >= lower) & (group_filtered[col] <= upper)
            ]

        filtered_count = len(group_filtered)
        removed = original_count - filtered_count

        print(f"[{name}] Removed {removed} outlier(s) (kept {filtered_count} of {original_count})")

        df_filtered = pd.concat([df_filtered, group_filtered], ignore_index=True)

    return df_filtered


def prepare_animal_data_for_training(datapoints: int, seed: int=42) -> DataFrame:
    """
    Generates and preprocesses animal data for training, including cleaning and labeling.

    :param datapoints: Number of datapoints to fetch.
    :param seed: Seed for random generation.
    :return: Cleaned and labeled training DataFrame.
    """

    df = pd.DataFrame(fetch_animals(datapoints=datapoints, seed=seed)[0])
    df['animal_type'] = None

    # Filter out impossible data combinations
    df = df[df['walks_on_n_legs'].isin([2, 4])]
    df = df[~(df['walks_on_n_legs'] == 4) | (df['has_wings'] == False)]
    df = df[df['has_tail'] == True]

    # Set animal_type based on the conditions
    df.loc[(df['walks_on_n_legs'] == 2) & (df['has_wings'] == True), 'animal_type'] = 'chicken'
    df.loc[(df['walks_on_n_legs'] == 2) & (df['has_wings'] == False), 'animal_type'] = 'kangaroo'
    df.loc[(df['weight'] >= 1500) & (df['animal_type'].isnull()), 'animal_type'] = 'elephant'
    df.loc[(df['weight'] < 1500) & (df['animal_type'].isnull()), 'animal_type'] = 'dog'

    df_cleaned = _remove_outliers_iqr(df)

    return df_cleaned


def train_animal_desicion_tree(df_cleaned: DataFrame) -> tuple[BaseEstimator, dict]:
    """
    Trains a Decision Tree classifier using grid search and evaluates it.

    :param df_cleaned: Preprocessed and labeled training data.
    :return: Tuple with the best model (DesicionTree) and performance metrics.
    """

    # Split data for training and testing
    X = df_cleaned[['height', 'weight', 'walks_on_n_legs', 'has_wings', 'has_tail']]
    y = df_cleaned['animal_type']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Create a grid serch to optimize a Desicion Tree Classifier
    param_grid = {
        'max_depth': [None, 3, 5, 10],
        'min_samples_split': [2, 5, 10],
        'criterion': ['gini', 'entropy']
    }

    grid_search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=42),
        param_grid=param_grid,
        scoring='f1_macro',
        cv=5,
        n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    model = grid_search.best_estimator_

    y_predict = model.predict(X_test)

    # Check several performance metrics
    acc = accuracy_score(y_test, y_predict)
    precision = precision_score(y_test, y_predict, average='macro')
    recall = recall_score(y_test, y_predict, average='macro')
    f1 = f1_score(y_test, y_predict, average='macro')

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }

    return model, metrics
