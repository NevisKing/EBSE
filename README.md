# Predictors of C++ GitHub Repository Popularity: An Empirical Study

This repository contains the codebase for the analyssi of C++ GitHub repository popularity. As metrics, we define the following:

1. Popularity Metrics
    - stars
    - forks
    - watchers

2. Activity Metrics
    - number of commits
    - commit frequency (first and last 100)
    - number of open issues
    - average issue closing time (first and last 100)
    - number of open pull requests
    - average pull request merge time (first and last 100)
    - size

3. Community Metrics
    - number of contributors

4. Update Metrics
    - number of releases
    - event frequency (last 100)
    - creation date

We further define the research questions:
1. How does the activity data of C++ repositories correlate with their popularity?
2. Is there a correlation between the community data and repository popularity
metrics?
3. How does the update data correlate to popularity metrics?
4. s there a difference in how metadata correlates with each popularity metric?

For our investigation, we develop automated tools for two steps: data mining and data analysis, further detailed below.

## Data Mining
We gather data from C++ GitHup public repositories using the GitHub API library. The script *mining/mining.py* provides the functionality to automaticaly mine repositories.

### Requirements
1. create a venv *python -m venv env*
2. open the env *.\env\Scripts\activate*
3. install the requirements *pip install -r requiements.txt*
4. add the GitHub token in the GITHUB_ACCESS_TOKEN variable
5. change the desired time intervals for mining if desired
6. run the script *python mining.py*

### Behavior
The script will start running and provide logs in the *output.txt* file. Firstly, the script makes a search query to GitHub with the selected filters and receives 1.000 repositories. Then, several more criteria are checked for each repository and the ones that do not correspond are diascarded in *discarded_links.txt*. The script proceedes to gather base and advanced metrics for each repository and saves it in *chosen_links.txt*.

## Data Analysis
Several statistical analysis activities are performed for the dataset of mined repositories from the *dataset.csv* file.

### Requirements
1. create a venv *python -m venv env*
2. open the env *.\env\Scripts\activate*
3. install the requirements *pip install -r requiements.txt*
4. run the script *python analysis.py*

### Behavior
The script performs the following tasks:
1. clean data
    - remove entries with zero-values and save in *cleaned_dataset.csv*
    - remove outliers and save in *no_outliers_dataset.csv*
2. compute correlations
    - compute wether each metric is normally distributed
    - compute correlation and save in *correlation.csv*
3. plot relationships and save them in the *plots* directory
4. plot heatmap and display
4. compute one-way ANOVA for the correlation results for each popularity metric and display