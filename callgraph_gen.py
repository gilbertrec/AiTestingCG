import pandas as pd
from threading import Lock
import concurrent.futures
import git
from git import Repo

TEST_THRESHOLD = 5



def clone_project(row,lock):
    repo_full_name = row["repo_name"]
    repo_url = row["repo_url"]

    try:
        print(f'cloning {repo_full_name}')
        Repo.clone_from(repo_url, f'repos_filtered/{repo_full_name}')
        print(f'cloned {repo_full_name}')
    except git.exc.GitError as e:
        print(f'error cloning  {repo_full_name}')
        with lock:
            with open('errors.csv', 'a', encoding='utf-8') as error_log:
                error = e.__str__().replace("'", "").replace("\n", "")
                str = f"{repo_full_name},{repo_url},'{error}'"
                error_log.write(str + '\n')
            return

def start_search(iterable, max_workers=None):
    writer_lock = Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for repo in iterable:
            _ = executor.submit(clone_project, repo, writer_lock)

def scan_projects(df):
    iterable = [x for y, x in df.iterrows()]
    start_search(iterable,3)

if __name__ == '__main__':
    input_file = pd.read_csv('results.csv', delimiter=",")
    df = input_file[input_file['count'] <= TEST_THRESHOLD]
    scan_projects(df)
