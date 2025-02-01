import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import zscore, shapiro, pearsonr, spearmanr

def clean_data():
    data = pd.read_csv('dataset.csv')
    data = data[(data.T != 0).all()]
    data.to_csv('cleaned_dataset.csv', index=False)
    return data

def remove_outliers_data(data):
    data.drop(['No.', 'repo_name', 'repo_url'], axis=1, inplace=True)
    data['creation_date'] = pd.to_datetime(data['creation_date']).astype(int) / 10**9
    data = remove_outliers(data)
    data.to_csv('no_outliers_dataset.csv', index=False)
    return data

def plot_data(x, y, title, x_label, y_label):
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, s=100, c='blue', alpha=0.6, edgecolors='black', marker='o')  # 's' controls circle size
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    
    # Save the plot
    plt.savefig(f'plots/{x_label}_vs_{y_label}.png')
    plt.close()

def remove_outliers(data):
    z_scores = zscore(data)
    abs_z_scores = abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    return data[filtered_entries]

def drop_columns(data, columns):
    return data.drop(columns, axis=1)

def check_normality_shapiro(column, alpha=0.01):
    stat, p_value = shapiro(column)
    return (p_value > alpha, p_value)

def calculate_correlation(column_a, column_b, csv):
    # Check if the columns are normally distributed
    normality_column_a, p_value_column_a = check_normality_shapiro(column_a)
    normality_column_b, p_value_column_b = check_normality_shapiro(column_b)
    if normality_column_a and normality_column_b:
        correlation = 'pearson'
        # If both columns are normally distributed, use Pearson correlation
        print(f"Calculating Pearson correlation between {column_a.name} and {column_b.name}")
        corr, p_value = pearsonr(column_a, column_b)
        print(f"\tPearson Correlation: {corr:.3f}")
        print(f"\tP-value: {p_value:.3e}")
    else:
        correlation = 'spearman'
        # If not, use Spearman correlation
        print(f"Calculating Spearman correlation between {column_a.name} and {column_b.name}")
        corr, p_value = spearmanr(column_a, column_b)
        print(f"\tSpearman Correlation: {corr:.3f}")
        print(f"\tP-value: {p_value:.3e}")
    print()
    csv.append([column_a.name, normality_column_a, f"{p_value_column_a:.3e}", column_b.name, normality_column_b, f"{p_value_column_b:.3e}", correlation, f"{corr:.3f}", f"{p_value:.3e}"])
    
    return corr, p_value


if __name__ == '__main__':
    data = clean_data()
    data = remove_outliers_data(data)

    popularity_metrics = ['watchers', 'stars', 'forks']
    metrics = ['contributors', 'size', 'open_issues', 'pull_requests', 'releases', 'commits', 'events', 'average_time_close_pull_requests_first_100', 'average_time_close_pull_requests_last_100', 'average_time_close_issues_first_100', 'average_time_close_issues_last_100', 'frequency_commits_first_100', 'frequency_commits_last_100', 'frequency_events_last_100', 'creation_date']

    if not os.path.exists('plots'):
        os.makedirs('plots')

    csv = []
    for metric in metrics:
        for popularity_metric in popularity_metrics:
            plot_data(data[metric], data[popularity_metric], f'{metric} vs {popularity_metric}', metric, popularity_metric)
            calculate_correlation(data[metric], data[popularity_metric], csv)
    
    df = pd.DataFrame(csv, columns=['Metric A', 'Normality A', 'P-value A', 'Metric B', 'Normality B', 'P-value B', 'Correlation', 'Correlation Value', 'P-value Correlation'])
    df.to_csv('correlation.csv', index=False)
