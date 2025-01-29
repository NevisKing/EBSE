import pandas as pd  # For data handling
import seaborn as sns  # For visualizations
import matplotlib.pyplot as plt  # For plotting
import scipy.stats as stats  # For correlation
import numpy as np  # For numerical operations

# Load the dataset
file_path = "dataset.xlsx"
data = pd.read_excel(file_path, skiprows=3)  
data.columns = [col.strip() for col in data.columns]

activity_metrics = [
    "commits", "events", "frequency_commits_first_100",
    "frequency_commits_last_100", "frequency_events_last_100"
]

community_metrics = ["contributors", "pull_requests", "open_issues"]

update_metrics = [
    "releases", "average_time_close_pull_requests_first_100",
    "average_time_close_pull_requests_last_100",
    "average_time_close_issues_first_100", "average_time_close_issues_last_100"
]

popularity_metrics = ["watchers", "forks", "stars"]

all_metrics = activity_metrics + community_metrics + update_metrics + popularity_metrics

#remove rows with a zero
filtered = data[(data[all_metrics] != 0).all(axis=1)]

#check for outliers
def detect_outliers(data, columns):
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=data[columns])
    plt.title("Boxplot of numeric variables")
    plt.show()

    #Calculate z-scores(<-3 or >3 are outliers)
    z_scores = np.abs(stats.zscore(data[columns].dropna()))
    outlier_counts = np.sum(z_scores > 3).sum()
    print(f"Number of outliers:\n{outlier_counts}")

#check normality
def check_normality(data, column):
    stat, p_value = stats.shapiro(data[column].dropna())
    return p_value >= 0.5 # If p-value is greater than 0.05, data is normally distributed

#correlation and plotting
def analyze_correlation(independent_vars, independent_label):
    for independent in independent_vars:
        for popularity in popularity_metrics:
            #check normality
            independent_normal = check_normality(filtered, independent)
            popularity_normal = check_normality(filtered, popularity)
            
            #Pearson if both are normal, otherwise Spearman
            if independent_normal and popularity_normal:
                corr, p_value = stats.pearsonr(filtered[independent], filtered[popularity])
                method = "Pearson"
            else:
                corr, p_value = stats.spearmanr(filtered[independent], filtered[popularity])
                method = "Spearman"
            
            print(f"{method} correlation between {independent} ({independent_label}) and {popularity}: {corr:.3f} (p={p_value:.3f})")

            # Create scatterplot with regression line
            sns.lmplot(x=independent, y=popularity, data=data)
            plt.title(f"{independent} vs. {popularity}")
            plt.xlabel(independent)
            plt.ylabel(popularity)
            plt.show()

#outlier detection
detect_outliers(filtered, activity_metrics + community_metrics + update_metrics + popularity_metrics)

#which rq to run
print("Select Research Question (RQ) to analyze:")
print("1 - rq1: Activity Data vs. Popularity")
print("2 - rq2: Community Data vs. Popularity")
print("3 - rq3: Update Data vs. Popularity")
print("4 - rq4: Differences in Metadata Correlation")
choice = input("(1-4): ")

if choice == "1":
    print("\nAnalyzing RQ1: Activity Data vs. Popularity...\n")
    analyze_correlation(activity_metrics, "Activity Data")

elif choice == "2":
    print("\nAnalyzing RQ2: Community Data vs. Popularity...\n")
    analyze_correlation(community_metrics, "Community Data")

elif choice == "3":
    print("\nAnalyzing RQ3: Update Data vs. Popularity...\n")
    analyze_correlation(update_metrics, "Update Data")

elif choice == "4":
    print("\nAnalyzing RQ4: Differences in Metadata Correlation...\n")

    # Compare correlation values for different metadata types
    all_metrics = {
        "Activity Data": activity_metrics,
        "Community Data": community_metrics,
        "Update Data": update_metrics
    }

    correlation_results = []

    for category, metrics in all_metrics.items():
        for metric in metrics:
            for popularity in popularity_metrics:
                independent_normal = check_normality(filtered, metric)
                popularity_normal = check_normality(filtered, popularity)
                
                if independent_normal and popularity_normal:
                    corr, p_value = stats.pearsonr(filtered[metric], filtered[popularity])
                    method = "Pearson"
                else:
                    corr, p_value = stats.spearmanr(filtered[metric], filtered[popularity])
                    method = "Spearman"
                
                correlation_results.append((category, metric, popularity, method, corr, p_value))
    
    # Convert results into a DataFrame for easy viewing
    correlation_df = pd.DataFrame(correlation_results, columns=["Category", "Metadata", "Popularity Metric", "Method","Correlation", "P-value"])
    print(correlation_df)

else:
    print("Invalid choice. Please run the script again and enter a number between 1 and 4.")