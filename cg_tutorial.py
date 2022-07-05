from scalpel.call_graph.pycg import CallGraphGenerator
from scalpel.call_graph.pycg import formats
import json
import glob
import os
#entry point e package da analizzare


path = "repos_filtered/"
output_path = "Results/"


def generate_callgraph(filename_list,project_name):
    cg_generator = CallGraphGenerator(filename_list, project_name)
    try:
        cg = cg_generator.analyze()
        print("------CallGraph------")
        print(cg)
        formatter = formats.Simple(cg_generator)
        print("------Formatter------")
        print(formatter.generate())
        with open(output_path + project_name + ".json", "w+") as f:
            f.write(json.dumps(formatter.generate()))
    except:
        with open('analyze_error.csv', 'a')as error_log:
            error_log.write(project_name + '\n')



def analyze_project(project_name):
        filename_list = glob.glob(path+project_name+"/**/*test*.py", recursive=True)
        generate_callgraph(filename_list,project_name)

def scan_projects():
    for project in os.listdir(path):
        print(project)
        analyze_project(project)
        filter_call_graph(project)

def filter_call_graph(project_name):
    filename_list = glob.glob(output_path + project_name + '.json', recursive=True)
    for filename in filename_list:
        file_input = open(filename)
        json_obj = json.load(file_input)
        print(filename)
        filtered_json = remove_empty(json_obj)
        filename_filtered = filename.replace(".json","")
        out_file = open(filename_filtered+"_filtered.json","w")
        json.dump(filtered_json, out_file)

def remove_empty(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""
    def empty(x):
        return x is None or x == {} or x == []
    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty(v)) for k, v in d.items()) if not empty(v)}


def clean_results():
    filename_list = glob.glob(output_path + '*.json', recursive=True)
    #os.remove('analyze_error.csv')
    for filename in filename_list:
        os.remove(filename)

if __name__ == "__main__":
    clean_results()
    scan_projects()
