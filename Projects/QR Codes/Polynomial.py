# IMPORTS #

from __future__ import annotations

from GaloisField import GaloisFieldElement

# POLYNOMIAL CLASS #

class Polynomial:
    """
        A class representing a polynomial with various operations.

        Attributes:
            coefficients (list[int | float | GaloisFieldElement]): List of coefficients, where the index represents the degree of the term (power increasing from left to right).
            degree (int): The degree of the polynomial (number of coefficients).

        Methods:
            __add__(self, other): Adds two Polynomial objects.
            __sub__(self, other): Subtracts two Polynomial objects.
            __mul__(self, other): Multiplies a Polynomial by another Polynomial or a constant value.
            __xor__(self, other): XORs two Polynomial objects or a Polynomial with a constant value.
            copy(self): Creates a copy of the Polynomial object.
            shift(self, degrees): Shifts the polynomial by a specified number of degrees (adds leading zeros).
            __str__(self): Returns a string representation of the Polynomial object.
    """

    EXPONENTIAL_STRINGS = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"
    } # For pretty-printing exponents.

    def __init__(self, coefficients: list[int | float | GaloisFieldElement]):
        """
            Initialise a Polynomial object.
            
            Args:
                coefficients (list[int | float | GaloisFieldElement]): List of coefficients, where the index represents the degree of the term (power increasing from left to right).
            
            Raises:
                ValueError: If coefficients are not provided.
        """
        # Validate input.
        if not coefficients:
            raise ValueError("Coefficients must be provided") # Cannot create a polynomial without coefficients.

        self.coefficients = coefficients # List of coefficients.
        self.degree = len(coefficients) # Degree of the polynomial (number of coefficients).

    def __add__(self, other: Polynomial) -> Polynomial:
        """
            Add two Polynomial objects.

            Args:
                other (Polynomial): The other Polynomial object to add.

            Returns:
                Polynomial: Result of adding two Polynomial objects.
        """
        max_degree = max(self.degree, other.degree) # Maximum degree of the two polynomials.
        result = [0] * max_degree # Initialise result coefficients.

        for degree in range(max_degree): # Iterate through each degree.
            a = self.coefficients[degree] if degree < self.degree else 0 # Coefficient from self or 0 if degree exceeds.
            b = other.coefficients[degree] if degree < other.degree else 0 # Coefficient from other or 0 if degree exceeds.
            result[degree] = a + b # Sum the coefficients.

        return Polynomial(result) # Return new Polynomial object with result coefficients.

    def __sub__(self, other: Polynomial) -> Polynomial:
        """
            Subtract two Polynomial objects.

            Args:
                other (Polynomial): The other Polynomial object to subtract.

            Returns:
                Polynomial: Result of subtracting two Polynomial objects.
        """
        return self + (other * -1)

    def __mul__(self, other: Polynomial | int | float) -> Polynomial:
        """
            Multiply a Polynomial by another Polynomial or a constant value.

            Args:
                other (Polynomial | int |  float): The other Polynomial object or constant value to multiply by.

            Returns:
                Polynomial: Result of the multiplication.
        """
        if isinstance(other, Polynomial): # Multiply two Polynomial objects.
            result = [0] * (self.degree + other.degree - 1) # Initialise result coefficients.
            for i in range(self.degree): # Iterate through each coefficient.
                for j in range(other.degree): # Iterate through each coefficient of other.
                    degree = i + j # Degree of the resulting term.
                    if degree < len(result): # Ensure degree is within bounds.
                        result[degree] += self.coefficients[i] * other.coefficients[j] # Multiply and add to result.
            return Polynomial(result) # Return new Polynomial object with result coefficients.

        return Polynomial([coefficient * other for coefficient in self.coefficients]) # Multiply by constant value.

    def __xor__(self, other: Polynomial | int | float) -> Polynomial:
        """
            XOR two Polynomial objects or a Polynomial with a constant value.

            Args:
                other (Polynomial | int | float): The other Polynomial object or constant value to XOR with.

            Returns:
                Polynomial: Result of the XOR operation.
        """
        if isinstance(other, Polynomial): # XOR two Polynomial objects.
            result = [0] * self.degree # Initialise result coefficients.
            for i in range(self.degree): # Iterate through each coefficient.
                a = self.coefficients[i] if i < self.degree else 0
                b = other.coefficients[i] if i < other.degree else 0 # XOR the coefficients.
                result[i] = a ^ b
            while result[-1] == 0: # Remove leading zeros if in Galois Field.
                del result[-1] # Remove last element.
            return Polynomial(result) # Return new Polynomial object with result coefficients.

        return Polynomial([coefficient ^ other for coefficient in self.coefficients]) # XOR with constant value.

    def copy(self) -> Polynomial:
        """
            Creates a copy of the Polynomial object.

            Returns:
                Polynomial: A copy of the Polynomial object.
        """
        return Polynomial(self.coefficients.copy())

    def shift(self, degrees: int = 1) -> Polynomial:
        """
            Shifts the polynomial by a specified number of degrees (adds leading zeros).

            Args:
                degrees (int): Number of degrees to shift the polynomial by. Defaults to 1.

            Returns:
                Polynomial: The shifted Polynomial object.
        """
        return Polynomial(([0] * degrees) + self.coefficients)

    def __str__(self) -> str:
        """
            Returns a string representation of the Polynomial object.

            Returns:
                str: String representation of the Polynomial.
        """
        out = "" # Output string.
        first_term = True # Flag for the first term.

        for degree, coefficient in enumerate(self.coefficients): # Iterate through each coefficient.
            if coefficient == 0: continue # Skip zero coefficients.

            if not first_term: # Not the first term.
                out += " + " if coefficient > 0 else " - " # Add appropriate sign.
            elif coefficient < 0: # First term and negative.
                out += "-" # Add negative sign.

            if abs(coefficient) != 1 or degree == 0: # Only add coefficient if it's not 1 or -1, or if it's the constant term.
                out += str(abs(coefficient)) # Add absolute value of coefficient.
                first_term = False # No longer the first term.

            if degree > 0: # Add x term.
                out += "x" # Append 'x'.
                if degree > 1: # Add exponent if degree > 1.
                    out += ''.join([self.EXPONENTIAL_STRINGS[n] for n in str(degree)]) # Append exponent.

        return out or "0" # Return "0" if polynomial is zero.