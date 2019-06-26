# Graph Visual Rhythm for Vehicular Networks 

This framework generates Graph Visual Rhythm (GVR) for vehicular networks, considering temporal graphs. 

### Dependencies:

Before the execution, you need to check these following dependencies: SUMO 1.2, python, python3, networkx, and matplotlib 2.1.0, seaborn.


### Dataset:

TAPASCologne is used, but you can use other traces.
You can download it in this link http://kolntrace.project.citi-lab.fr/ 

![Interface](Selection_127.png)

### Colecting data:

`python runner.py <cologne6to8>.sumocfg <tripinfo>.xml`

### Complex network measures:

`python graph.py`

#### List of measures available:

- Degree centrality
- Closeness centrality
- Betweenness centrality
- Local efficiency
- Harmonic centrality
- PageRank

### Interface:

`python3 interface.py`

![Interface](Selection_126.png)

### Output:

![Interface](Selection_128.png)

### Citation:

```
@misc{git-gvr,
  title = {Graph Visual Rhythm for Vehicular Networks},
  author = {Trindade, Silvana},
  howpublished = {\url{https://github.com/Trindad/graph-visual-rhythm}},
  month = {June},
  year = {2019}
}
```
