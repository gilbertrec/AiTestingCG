import git
import pandas as pd
from git import Repo
import shutil
import concurrent.futures
from threading import Lock
import os

def __search(row,lock):
    repo_full_name = row["repo_name"]
    repo_url = row["repo_url"]

    try:
        print(f'cloning {repo_full_name}')
        Repo.clone_from(repo_url, f'repos/{repo_full_name}')
        print(f'cloned {repo_full_name}')
    except git.exc.GitError as e:
        print(f'error cloning  {repo_full_name}')
        with lock:
            with open('errors.csv', 'a', encoding='utf-8') as error_log:
                error = e.__str__().replace("'", "").replace("\n", "")
                str= f"{repo_full_name},{repo_url},'{error}'"
                error_log.write(str + '\n')
            return
    print(f'analyzed {repo_full_name}')
    print(f'saving {repo_full_name}')
    with lock:
        try:
            cloned_log = pd.read_csv('cloned_log.csv')
            cloned_log = cloned_log.append(row, ignore_index=True)
            cloned_log.to_csv('cloned_log.csv', index=False)
        except:
            print(f'error saving {repo_full_name}')
    print(f'saved {repo_full_name}')
    to_delete = "repos/" + repo_full_name.split("/")[0]
    return to_delete


def delete_repos(to_delete):
    shutil.rmtree(to_delete)
    print(f'deleted {to_delete}')



def start_search(iterable, max_workers=None):
    writer_lock = Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for repo in iterable:
            _ = executor.submit(__search, repo, writer_lock)



if __name__ == '__main__':
    df = pd.read_csv('results.csv', delimiter=",")
    #filter
    df = df[df['count'] > 0]
    if(os.path.exists('cloned_log.csv')):
        cloned_log = pd.read_csv('cloned_log.csv', delimiter=",")
        df = df[~df['repo_name'].isin(cloned_log['repo_name'])]
        print(len(df))
    else:
        cloned_log = pd.DataFrame(columns=['repo_name', 'repo_url','test_framework','ml_libs','count'])
        cloned_log.to_csv('cloned_log.csv', index=False)
    print("The size of results is "+str(len(df)))

    already_analyzed = None
    error = None
    os.makedirs('repos', exist_ok=True)

    iterable = [x for y, x in df.iterrows()]
    print(f'to analyze: {len(iterable)} repos')
    start_search(iterable)