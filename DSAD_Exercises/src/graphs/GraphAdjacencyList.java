package graphs;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class GraphAdjacencyList {
	
 	//Map collection to store the adjacency list for each vertex
	private Map<Integer,List<Integer>> Adjacency_List;
	
	/*
	 * Initializes the map to size equal to number of vertices in a graph 
	 * Maps each vertex to a given List Object 
	 */
	public GraphAdjacencyList(int num_vertices) {
		Adjacency_List = new HashMap<Integer,List<Integer>>();
		for(int i =1 ;i<=num_vertices;i++) {
			Adjacency_List.put(i,new LinkedList<Integer>());
		}
	}
	
	//Adds nodes in Adjacency List for corresponding vertex  
	public void setEdge(int source,int destination) {
		if(source > Adjacency_List.size() || destination > Adjacency_List.size()) {
			System.out.println("the vertex entered is not present");
			return;
		}
		List<Integer> slist = Adjacency_List.get(source);
		slist.add(destination);
		List<Integer> dlist = Adjacency_List.get(destination);
		dlist.add(source);
	}
	
   /* Returns the List containing the vertex joining the source vertex */		
	public List<Integer> getEdge(int source){
		if (source > Adjacency_List.size()) {
			System.out.println("the vertex entered is not present");
			return null;
		}
		return Adjacency_List.get(source);
	}
	
}
