package graphs;

import graphs.GraphAdjacencyList2.Graph;

public class DepthFirstSearchMain {

	public static void main(String[] args) {
		int v =6;
		Graph graph = new Graph(v);
		// create an GraphAdjacencyList2 object to access the methods
		GraphAdjacencyList2 graphAdj = new GraphAdjacencyList2();
		
		graphAdj.addEdge(graph, 1, 0);
		graphAdj.addEdge(graph, 1, 3);
		graphAdj.addEdge(graph, 0, 2);
		graphAdj.addEdge(graph, 2, 3);
		graphAdj.addEdge(graph, 3, 0);
		graphAdj.addEdge(graph, 4, 2);
		graphAdj.addEdge(graph, 4, 5);
		graphAdj.addEdge(graph, 5, 5);
		
		//print the graph 
		graphAdj.showGraph(graph);
		DepthFirstSearch dfs = new DepthFirstSearch();
		dfs.DepthFirst(graph, 0);
	}
}
