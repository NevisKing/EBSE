from decouple import config
from github import Github
import time
import datetime
import sys
import os

GITHUB_ACCESS_TOKEN = ""

START_DATE = "2010-01-01"
END_DATE = "2020-12-31"
MIN_STARS = 10
MIN_FORKS = 10
MIN_SIZE = 10000 # 10MB

def githubLimit(github_client):
    core_rate_limit = github_client.get_rate_limit().core
    print("Remaining requests:", core_rate_limit.remaining)
    # If the rate limit is 0, time out until the rate limit is reset
    if core_rate_limit.remaining <= 250:
        reset_time = core_rate_limit.reset.timestamp() - datetime.datetime.now().timestamp()
        # Sleep until the rate limit is reset
        print("Rate limit exceeded. Sleeping for ", int(reset_time), " seconds")
        time.sleep(reset_time)

def githubConnect():
    try:
        github_client = Github(login_or_token=GITHUB_ACCESS_TOKEN, per_page=100)

        user = github_client.get_user()
        print("Connected to GitHub as:", user.login)
        return github_client
    
    except Exception as e:
        print("Error connecting to GitHub:", e)
        print("Exiting...")
        sys.exit(1)

def preprocessRepos(unique_repos):
    discared_repos = []
    selected_repos = []
    for repo in unique_repos:
        print("Preprocessing repo:", repo.full_name)

        sub_count = repo.subscribers_count

        # Check the number of watchers the repo has
        if sub_count < 10:
            print("\tRepo has less than 10 watchers")
            # Add the repo link and "watchers" argument to the checked_repos list
            discared_repos.append((repo, "watchers"))

        # Check the number of contributors the repo has
        try:
            contributors = repo.get_contributors(anon="true").totalCount
            if contributors < 5:
                print("\tRepo has less than 5 contributors")
                # Add the repo link and "contributors" argument to the checked_repos list
                discared_repos.append((repo, "contributors"))
                continue
        except Exception as e:
            if "The history or contributor list is too large to list contributors" in str(e):
                contributors = -1
                print("\tRepo has too many contributors")
            else:
                print("\tError getting contributors:", e)
                discared_repos.append(repo, "contributors")
                continue

        selected_repos.append({"repo": repo, "repo_name": repo.full_name, "repo_url": repo.html_url, "contributors": contributors, "watchers": repo.subscribers_count, "forks": repo.forks_count, "stars": repo.stargazers_count, "size": repo.size, "open_issues": repo.open_issues_count, "creation_date": repo.created_at})

    # Add discarded repos to the discared_links.txt file
    with open("repos/discarded_links.txt", "a") as f:
        for repo, reason in discared_repos:
            f.write(repo.html_url + " " + reason + "\n")

    return selected_repos

def advancedRepos(github_client, selected_repos):
    for repo in selected_repos:
        githubLimit(github_client)
        print("Getting advanced repo data for:", repo["repo_name"])
        try:
            commits = repo["repo"].get_commits()
            repo["pull_requests"] = repo["repo"].get_pulls().totalCount
            repo["releases"] = repo["repo"].get_releases().totalCount
            repo["commits"] = commits.totalCount

            closed_pull_requests_first = repo["repo"].get_pulls(state="closed", sort="created", direction="asc")
            time_zone = datetime.timezone(datetime.timedelta(hours=0))
            default_date = datetime.datetime(1970, 1, 2, 0, 0, 0, 0, time_zone)
            if (closed_pull_requests_first[0].created_at < default_date):
                print("\tDiscarding repo:", repo["repo_name"], "Pull request date:", closed_pull_requests_first[0].created_at)
                with open("repos/discarded_links.txt", "a") as f:
                    f.write(repo["repo_url"] + " " + "pull request date: " + str(closed_pull_requests_first[0].created_at) + "\n")
                continue

            closed_issues_first = repo["repo"].get_issues(state="closed", sort="created", direction="asc")
            if (closed_issues_first[0].created_at < default_date):
                print("\tDiscarding repo:", repo["repo_name"], "Issue date:", closed_issues_first[0].created_at)
                with open("repos/discarded_links.txt", "a") as f:
                    f.write(repo["repo_url"] + " " + "issue date: " + str(closed_issues_first[0].created_at) + "\n")
                continue

            if (commits.totalCount > 100):
                commits_last_page = commits.get_page((repo["commits"] - 1) // 100)
            else:
                commits_last_page = commits
            
            last_commit_date = commits_last_page[0].commit.author.date
            if (last_commit_date < default_date):
                print("\tDiscarding repo:", repo["repo_name"], "Commit date:", last_commit_date)
                with open("repos/discarded_links.txt", "a") as f:
                    f.write(repo["repo_url"] + " " + "commit date: " + str(last_commit_date) + "\n")
                continue

            date_2010 = datetime.datetime(2010, 1, 1, 0, 0, 0, 0, time_zone)
            if (closed_pull_requests_first[0].created_at < date_2010):
                print("\tPull request before 2010:", repo["repo_name"], "Pull request date:", closed_pull_requests_first[0].created_at)
            if (closed_issues_first[0].created_at < date_2010):
                print("\tIssue before 2010:", repo["repo_name"], "Issue date:", closed_issues_first[0].created_at)
            if (last_commit_date < date_2010):
                print("\tCommit before 2010:", repo["repo_name"], "Commit date:", last_commit_date)

            repo["closed_pull_requests"] = closed_pull_requests_first.totalCount
            if (repo["closed_pull_requests"] == 0):
                repo["average_time_close_pull_requests_first_100"] = 0
                repo["average_time_close_pull_requests_last_100"] = 0
            elif (repo["closed_pull_requests"] < 100):
                average_time_close_pull_requests_first = 0
                for pull_request in closed_pull_requests_first:
                    average_time_close_pull_requests_first += (pull_request.closed_at - pull_request.created_at).total_seconds()
                average_time_close_pull_requests_first /= repo["closed_pull_requests"]
                repo["average_time_close_pull_requests_first_100"] = average_time_close_pull_requests_first

                repo["average_time_close_pull_requests_last_100"] = repo["average_time_close_pull_requests_first_100"]
            else:
                average_time_close_pull_requests_first = 0
                for pull_request in closed_pull_requests_first[0:100]:
                    average_time_close_pull_requests_first += (pull_request.closed_at - pull_request.created_at).total_seconds()
                average_time_close_pull_requests_first /= 100
                repo["average_time_close_pull_requests_first_100"] = average_time_close_pull_requests_first

                closed_pull_requests_last = repo["repo"].get_pulls(state="closed", sort="created", direction="desc")
                average_time_close_pull_requests_last = 0
                for pull_request in closed_pull_requests_last[0:100]:
                    average_time_close_pull_requests_last += (pull_request.closed_at - pull_request.created_at).total_seconds()
                average_time_close_pull_requests_last /= 100
                repo["average_time_close_pull_requests_last_100"] = average_time_close_pull_requests_last

            repo["open_issues"] = repo["repo"].get_issues(state="open").totalCount - repo["pull_requests"]

            repo["closed_issues"] = closed_issues_first.totalCount - repo["closed_pull_requests"]
            if (repo["closed_issues"] == 0):
                repo["average_time_close_issues_first_100"] = 0
                repo["average_time_close_issues_last_100"] = 0
            elif (repo["closed_issues"] < 100):
                average_time_close_issues_first = 0
                for issue in closed_issues_first:
                    if issue.pull_request is not None:
                        continue
                    average_time_close_issues_first += (issue.closed_at - issue.created_at).total_seconds()
                average_time_close_issues_first /= repo["closed_issues"]
                repo["average_time_close_issues_first_100"] = average_time_close_issues_first

                repo["average_time_close_issues_last_100"] = repo["average_time_close_issues_first_100"]
            else:
                average_time_close_issues_first = 0
                counter = 0
                for issue in closed_issues_first:
                    if issue.pull_request is not None:
                        continue
                    average_time_close_issues_first += (issue.closed_at - issue.created_at).total_seconds()
                    counter += 1
                    if counter == 100:
                        break
                average_time_close_issues_first /= 100
                repo["average_time_close_issues_first_100"] = average_time_close_issues_first

                closed_issues_last = repo["repo"].get_issues(state="closed", sort="created", direction="desc")
                average_time_close_issues_last = 0
                counter = 0
                for issue in closed_issues_last:
                    if issue.pull_request is not None:
                        continue
                    average_time_close_issues_last += (issue.closed_at - issue.created_at).total_seconds()
                    counter += 1
                    if counter == 100:
                        break
                average_time_close_issues_last /= 100
                repo["average_time_close_issues_last_100"] = average_time_close_issues_last

            if (repo["commits"] == 0):
                repo["commits_frequency_first_100"] = 0
                repo["commits_frequency_last_100"] = 0
            elif (repo["commits"] < 100):
                repo["commits_frequency_first_100"] = (commits[0].commit.author.date - commits[repo["commits"] - 1].commit.author.date).total_seconds() / repo["commits"]
                repo["commits_frequency_last_100"] = repo["commits_frequency_first_100"]
            else:
                first_commit_date = commits_last_page[len(commits_last_page) - 1].commit.author.date
                if (len(commits_last_page) < 100):
                    commits_second_last_page = commits.get_page((repo["commits"] - 1) // 100 - 1)
                    first_commit_date_100 = commits_second_last_page[100 - (100 - len(commits_last_page))].commit.author.date
                else:
                    first_commit_date_100 = commits_last_page[0].commit.author.date
                repo["commits_frequency_first_100"] = (first_commit_date_100 - first_commit_date).total_seconds() / 100
                
                repo["commits_frequency_last_100"] = (commits[0].commit.author.date - commits[99].commit.author.date).total_seconds() / 100
            
            events = repo["repo"].get_events()
            repo["events"] = events.totalCount
            if (repo["events"] == 0):
                repo["events_frequency_last_100"] = 0
            elif (repo["events"] < 100):
                repo["events_frequency_last_100"] = (events[0].created_at - events[repo["events"] - 1].created_at).total_seconds() / repo["events"]
            else:
                repo["events_frequency_last_100"] = (events[0].created_at - events[99].created_at).total_seconds() / 100

        except Exception as e:
            print("Error getting advanced repo data:", e)
            continue
        with open("repos/chosen_links.txt", "a") as f:
            f.write(repo["repo_name"] + "," + str(repo["repo_url"]) + "," + str(repo["contributors"]) + "," + str(repo["watchers"]) + "," + str(repo["forks"]) + "," + str(repo["stars"]) + "," + str(repo["size"]) + "," + str(repo["open_issues"]) + "," + str(repo["closed_issues"]) + "," + str(repo["pull_requests"]) + "," + str(repo["releases"]) + "," + str(repo["commits"]) + "," + str(repo["closed_pull_requests"]) + "," + str(repo["events"]) + "," + str(repo["average_time_close_pull_requests_first_100"]) + "," + str(repo["average_time_close_pull_requests_last_100"]) + "," + str(repo["average_time_close_issues_first_100"]) + "," + str(repo["average_time_close_issues_last_100"]) + "," + str(repo["commits_frequency_first_100"]) + "," + str(repo["commits_frequency_last_100"]) + "," + str(repo["events_frequency_last_100"]) + "," + str(repo["creation_date"]) + "\n")
    return selected_repos

def checkUniqueRepos(repos):
    print("Checking for unique repos...")
    unique_repos = []
    if not os.path.exists("repos"):
        os.makedirs("repos")
    
    if os.path.exists("repos/discarded_links.txt"):
        with open("repos/discarded_links.txt", "r") as f:
            discarded_links = f.readlines()
            discarded_links = [link.strip().split(" ")[0] for link in discarded_links]
    else:
        discarded_links = []
        open("repos/discarded_links.txt", "w").close()
    
    if os.path.exists("repos/chosen_links.txt"):
        # read csv file
        with open("repos/chosen_links.txt", "r") as f:
            chosen_links = f.readlines()
            chosen_links = [link.strip().split(",")[1] for link in chosen_links]
    else:
        chosen_links = []
        open("repos/chosen_links.txt", "w").close()

    for repo in repos:
        if repo.html_url in discarded_links:
            time.sleep(0.001)
            continue
        if repo.html_url not in chosen_links:
            unique_repos.append(repo)
        time.sleep(0.001)

    print("Found", len(unique_repos), "unique repos")
    return unique_repos

def get_cpp_repos(github_client, date_range):
    githubLimit(github_client)
    repos = github_client.search_repositories(query='language:cpp fork:false created:' + date_range + ' stars:>=' + str(MIN_STARS) + ' forks:>=' + str(MIN_FORKS) + ' size:>=' + str(MIN_SIZE))

    return repos


if __name__ == "__main__":
    github_client = githubConnect()
    repos = get_cpp_repos(github_client, START_DATE + ".." + END_DATE)
    unique_repos = checkUniqueRepos(repos)
    selected_repos = preprocessRepos(unique_repos)
    print("Selected repos:", len(selected_repos))
    advanced_repos = advancedRepos(github_client, selected_repos)