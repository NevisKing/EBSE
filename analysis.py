import pandas as pd  # For data handling
import seaborn as sns  # For visualizations
import matplotlib.pyplot as plt  # For plotting
import scipy.stats as stats  # For correlation

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

#correlation and plotting
def analyze_correlation(independent_vars, independent_label):
    for independent in independent_vars:
        for popularity in popularity_metrics:
            corr, p_value = stats.pearsonr(data[independent], data[popularity])
            print(f"Correlation between {independent} ({independent_label}) and {popularity}: {corr:.3f} (p={p_value:.3f})")

            # Create scatterplot with regression line
            sns.lmplot(x=independent, y=popularity, data=data)
            plt.title(f"{independent} vs. {popularity}")
            plt.xlabel(independent)
            plt.ylabel(popularity)
            plt.show()

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
                corr, p_value = stats.pearsonr(data[metric], data[popularity])
                correlation_results.append((category, metric, popularity, corr, p_value))

    # Convert results into a DataFrame for easy viewing
    correlation_df = pd.DataFrame(correlation_results, columns=["Category", "Metadata", "Popularity Metric", "Correlation", "P-value"])
    print(correlation_df)

else:
    print("Invalid choice. Please run the script again and enter a number between 1 and 4.")