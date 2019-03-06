package integerMultiplication;

import java.lang.Math;
public class IntegerMultiply {
	

	public static String[] stringCopy(long index, String string) {
		String	first = "",
				last = "";
		long actualIndex = string.length() - index;
		for (int i = 0; i<actualIndex; i++) {
			first+=string.charAt(i);
		}
		for (int i = (int)actualIndex; i<string.length(); i++) {
			last+=string.charAt(i);
		}
		return new String[] {first, last};
	}
	
	public static int max(int x, int y) {
		return (x>y)? x:y;
	}
	
	public static long power(long x, long y) {
		if (y == 0)
			return 1;
		else {
			long answer = 1;
			for (int i = 1; i<=y; i++) {
				answer *= x;
			}
			return answer;
		}
	}
	
	public static long multiplyValues(long x, long y) {
		// Base case: single digit multiplication
		if (x<10 || y<10) {
			return x * y;
		}
		// Recursive case: Decompose the problem by splitting the integers and applying the algorithm on the parts.
		else {
			// Convert the numbers to strings so we can compute the # of digits of each number.
			// Note: We could also use floor(log10(n) + 1) to compute the #digits, but remember that we need to split the numbers too.
			String xString = Integer.toString((int)x);
			String yString = Integer.toString((int)y);
			// Local variables
			long 	m = max(xString.length(), yString.length()), // the maximum # of digits
					m2 = m/2, // the middle; if the number is odd, it will floor the fraction
					high1 = Integer.parseInt(stringCopy(m2, xString)[0]), 
					// the most significant digits. this is the scalar multiplier for b^m2
					low1 = Integer.parseInt(stringCopy(m2, xString)[1]), 
					// the least significant digits. this is what is added on to high1*b^m2
					high2 = Integer.parseInt(stringCopy(m2, yString)[0]), 
					// same for y
					low2 = Integer.parseInt(stringCopy(m2, yString)[1]), 
					// same for y
					// Three recursive calls
					z0 = multiplyValues(low1, low2), // z0 = x0y0
					z2 = multiplyValues(high1, high2), // z2 = x1y1
					z1 = multiplyValues((low1 + high1), (low2 + high2)) - z2 - z0; // z1 = (x0 + y1)*(x1 + y0) - z2 - z0, courtesy of Karatsuba

			System.out.println("intermediate values are :" +high1 + ""+ low1 +"" + high2 +"" + low2);
			System.out.println("z values are :" +z0 + ""+ z2 +"" + z1 );
			
			return (z2 * power(10, 2*m2) + (z1 * power(10, m2)) + z0);
		}
	
}
}