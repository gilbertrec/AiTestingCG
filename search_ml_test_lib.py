import concurrent.futures
import gc
import os
import re
import shutil
from threading import Lock

import git
import pandas as pd
from git import Repo

ML_MODELS = {
             'pytorch': 'torch',
             'scipy': 'scipy',
             'scikitlearn': 'sklearn',
             'tensorflow': 'tensorflow',
             'opencv': 'cv2',
             'caffe': 'caffe',
             'keras': 'keras',
             'weka' : 'weka',
             'caffe2' : 'caffe2'
             }

#opencv is for computer vision
#caffe
#keras
#weka

TEST_FRAMEWORK = {'unittest': 'unittest',
                  'pytest': 'pytest'
                  }


def search_import(python_file, dict):
    frameworks = []

    for k in dict.keys():
        v = dict.get(k)

        r = re.compile(f"from .*{v}.* .*import", re.MULTILINE)

        if r.search(python_file):
            if f'{k}' not in frameworks:
                frameworks.append(k)

        r = re.compile(f"import {v}", re.MULTILINE)

        if r.search(python_file):
            if f'{k}' not in frameworks:
                frameworks.append(k)

    return frameworks


def __search(row, lock):
    repo_full_name = row["full_name"]
    repo_url = row["url"]

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

    count = 0
    framework = []
    ml_models = []
    print(f'analyzing {repo_full_name}')
    for root, dirs, files in os.walk(f"repos/{repo_full_name}"):
        if '.git' in root or 'env' in root or 'Lib' in root or 'site-packages' in root or 'venv' in root:
            continue
        for name in files:
            if name.endswith('.py'):
                try:
                    with open(os.path.join(root, name)) as f:
                        try:
                            python_file = f.read()
                            ml_models = list(set(ml_models + search_import(python_file, ML_MODELS)))
                            #TODO: controllare a seconda del framework di test
                            t = re.compile(r'def test.*:$', re.MULTILINE)
                            if name.startswith('test'):
                                framework = list(set(framework + search_import(python_file, TEST_FRAMEWORK)))
                                count += len(t.findall(python_file))
                        except:
                            continue
                except:
                    continue

    print(f'analyzed {repo_full_name}')
    print(f'saving {repo_full_name}')
    to_delete = "repos/" + repo_full_name.split("/")[0]
    shutil.rmtree(to_delete)

    info = f"{repo_full_name},{repo_url},"
    n = len(framework)
    c = 0
    if n > 0:
        for f in framework:
            c += 1
            if c == n:
                break
            info += f"{f}-"
        info += f"{framework[n - 1]},"
    else:
        info += f","

    n = len(ml_models)
    c = 0
    if n > 0:
        for f in ml_models:
            c += 1
            if c == n:
                break
            info += f"{f}-"
        info += f"{ml_models[n - 1]},"
    else:
        info += ","
    info += f"{count}\n"
    with lock:
        with open('results.csv', 'a', encoding='utf-8') as txtwrite:
                txtwrite.writelines(info)
    print(f'saved {repo_full_name}')
    gc.collect()

def start_search(iterable, max_workers=None):
    writer_lock = Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for repo in iterable:
            _ = executor.submit(__search, repo, writer_lock)



if __name__ == '__main__':
    df = pd.read_csv('2021_2022_filtered_ai_projects_complete.csv', delimiter=",")
    already_analyzed = None
    error = None
    if os.path.exists('results.csv') is False:
        header = "repo_name,repo_url,test_framework,ml_libs,count\n"
        with open('results.csv', 'w', encoding='utf-8') as txtwrite:
            txtwrite.writelines(header)
    else:
        already_analyzed = pd.read_csv('results.csv', delimiter=",")
        df = df[~df['full_name'].isin(already_analyzed['repo_name'])]
    if os.path.exists('errors.csv') is False:
        header = "repo_name,url,error_message\n"
        with open('errors.csv', 'w', encoding='utf-8') as txtwrite:
            txtwrite.writelines(header)
    else:
        error = pd.read_csv('errors.csv', delimiter=",", quotechar="'")
        df = df[~df['full_name'].isin(error['repo_name'])]


    os.makedirs('repos', exist_ok=True)

    iterable = [x for y, x in df.iterrows()]
    print(f'to analyze: {len(iterable)} repos')
    start_search(iterable,3)

