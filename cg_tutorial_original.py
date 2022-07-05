from scalpel.call_graph.pycg import CallGraphGenerator
from scalpel.call_graph.pycg import formats
import json

cg_generator = CallGraphGenerator(["./cg_example_pkg/main.py"], "cg_example_pkg")
cg_generator.analyze()
cg_edges = cg_generator.cg.get_edges()
cg = cg_generator.output_functions()
print(cg_edges)
formatter = formats.Simple(cg_generator)
with open("example_results.json", "w+") as f:
    f.write(json.dumps(formatter.generate()))
