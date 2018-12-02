package graphs;

import graphs.GraphAdjacencyList2.Graph;

public class GraphAdjacencyList2Main {
	
	public static void main(String[] args) {
	int v =5;
	Graph graph = new Graph(v);
	// create an GraphAdjacencyList2 object to access the methods
	GraphAdjacencyList2 graphAdj = new GraphAdjacencyList2(); 
	graphAdj.addEdge(graph, 0, 1);
	graphAdj.addEdge(graph, 0, 4);
	graphAdj.addEdge(graph, 1, 2);
	graphAdj.addEdge(graph, 1, 3);
	graphAdj.addEdge(graph, 1, 4);
	graphAdj.addEdge(graph, 2, 3);
	graphAdj.addEdge(graph, 3, 4);
	
	//print the graph 
	graphAdj.showGraph(graph);
	}	
}
