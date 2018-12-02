package graphs;

import java.util.List;

import graphs.GraphAdjacencyList2.Graph;

public class BreadthFirstMain {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int v =8;
		Graph graph = new Graph(v);
		// create an GraphAdjacencyList2 object to access the methods
		GraphAdjacencyList2 graphAdj = new GraphAdjacencyList2(); 
		graphAdj.addEdge(graph, 0, 1);
		graphAdj.addEdge(graph, 0, 3);
		graphAdj.addEdge(graph, 1, 2);
		graphAdj.addEdge(graph, 3, 4);
		graphAdj.addEdge(graph, 3, 5);
		graphAdj.addEdge(graph, 4, 5);
		graphAdj.addEdge(graph, 4, 6);
		graphAdj.addEdge(graph, 5, 6);
		graphAdj.addEdge(graph, 5, 7);
		graphAdj.addEdge(graph, 6, 7);
		
		//print the graph 
		graphAdj.showGraph(graph);
		
		BreadthFirstSearch bfs = new BreadthFirstSearch();
		//bfs.BreadthFirst(graph,0);
		//for (int i=0; i<bfs.restVertices.length ;i++)
			//System.out.println( " "+ bfs.color + " "+ bfs.distance + " " + bfs.parent +" " + bfs.restVertices[i] );
		
		List<Integer> breadthFirst= bfs.BreadthFirst(graph, 0);
		System.out.println(breadthFirst);
	}

}
