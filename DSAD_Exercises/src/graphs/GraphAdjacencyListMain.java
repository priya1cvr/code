package graphs;

import java.util.InputMismatchException;
import java.util.List;
import java.util.Scanner;

public class GraphAdjacencyListMain {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int source,destination;
		int num_edges,num_vertices;
		int count=1;
		Scanner scan = new Scanner(System.in);
		
		try {
			System.out.println("Enter the number of vertices and edges in graph");
			num_vertices = scan.nextInt();
			num_edges = scan.nextInt();
			GraphAdjacencyList adjacencyList = new GraphAdjacencyList(num_vertices);
			/* Reads the edges present in the graph */
            System.out.println("Enter the edges in graph Format : <source index> <destination index>");
            
            while(count <= num_edges) {
            		source = scan.nextInt();
            		destination = scan.nextInt();
            		adjacencyList.setEdge(source, destination);
            		count++;
            }
            //prints the adjacency List representing the graph 
            System.out.println ("the given Adjacency List for the graph \n");
            for(int i =1 ; i<num_vertices;i++) {
            		System.out.print(i+"->");
            		List<Integer> edgeList = adjacencyList.getEdge(i);
            		for(int j=1; ;j++) {
            			if(j != edgeList.size()) {
            				System.out.print(edgeList.get(j - 1 )+"->");
            			}else {
            				System.out.print(edgeList.get(j - 1 ));
                         break;
            			}	
            		}
            		System.out.println();
            }
		}
		catch(InputMismatchException inputMismatch){
            System.out.println("Error in Input Format. \nFormat : <source index> <destination index>");
		}
		scan.close();
	}

}
