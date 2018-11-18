package queues;

/*
 * This class implements queue using Array 
 */
public class Queue {
	int front ,rear ,size,capacity,array[];
	
	//Queue constructor 
	public Queue(int capacity) {
		this.capacity=capacity;
		front =this.size=0 ;
		rear=capacity-1;
		array = new int[this.capacity];
	}
	
	//function to see queue full
	//Queue is full when size equals capacity 
	boolean isFull(Queue que) {
		return(que.size == que.capacity);
	}
	
	//function to see queue is empty 
	//queue is empty when size is 0
	boolean isEmpty(Queue que) {
		return (que.size == 0);
	}
	
	//function to add an item to the queue 
	public void enqueue(int item) {
		if (isFull(this))
			return ;
		//this is to handle circular queue cases,enqueue rear should move  
		this.rear= (this.rear+1) % this.capacity;
		this.array[this.rear]=item;
		this.size=size+1;
		System.out.println("item - "+item +" enqueud to the queue");
	}
	
	public int dequeue() {
		if (isEmpty(this)) {
			System.out.println("Queue is Empty returning Integer.MIN_VALUE");
			return Integer.MIN_VALUE;
		}
		// take the item to be removed from the queue 
		int item = this.array[this.front];
		//during dequeue front should move 
		this.front =(this.front+1) % this.capacity;
		this.size=size-1;
		return item;	
	}
	
	//function to get front of the queue 
	public int front() {
		if (isEmpty(this))
			return Integer.MIN_VALUE;
		return this.array[this.front];
	}
	//function to get rear of the queue 
	public int rear() {
		if (isFull(this))
			return Integer.MIN_VALUE;;
			return this.array[this.rear];
	}
	int size() {
		if(isEmpty(this))
			return 0;
		else if(isFull(this))
			return this.capacity;
		else
			return (this.rear-this.front) +1;
	}
	
}
