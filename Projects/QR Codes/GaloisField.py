# IMPORTS #

from __future__ import annotations

# GALOIS FIELD ELEMENT CLASS #

class GaloisFieldElement:
    """
        A class representing an element in a Galois Field GF(prime^n).

        Attributes:
            galois_field (GaloisField): The Galois Field to which this element belongs.
            value (int): The integer value of the element in the field.
            exp (int): The exponent representation of the element in the field.

        Methods:
            __mul__(self, other): Multiplies two elements in the Galois Field.
            __add__(self, other): Adds two elements in the Galois Field.
            __abs__(self): Returns the absolute value of the element.
            __eq__(self, other): Checks if two elements are equal in the Galois Field.
            __ne__(self, other): Checks if two elements are not equal in the Galois Field.
            __lt__(self, other): Checks if this element is less than another in the Galois Field.
            __le__(self, other): Checks if this element is less than or equal to another in the Galois Field.
            __gt__(self, other): Checks if this element is greater than another in the Galois Field.
            __ge__(self, other): Checks if this element is greater than or equal to another in the Galois Field.

        Returns:
            GaloisFieldElement: An instance of the GaloisFieldElement class.
    """

    def __init__(self, galois_field: GaloisField, value: int, exp: int):
        """
            Initialise a GaloisFieldElement instance.

            Args:
                galois_field (GaloisField): The Galois Field to which this element belongs.
                value (int): The integer value of the element in the field.
                exp (int): The exponent representation of the element in the field.
        """

        self.galois_field = galois_field # The Galois Field to which this element belongs.
        self.value = value # The integer value of the element in the field.
        self.exp = exp # The exponent representation of the element in the field.

    def __mul__(self, other: GaloisFieldElement | int | float) -> GaloisFieldElement:
        """
            Multiply two numbers in GF(prime).

            Args:
                other (GaloisFieldElement | int | float): The other number to multiply with.

            Returns:
                GaloisFieldElement: The result of the multiplication in GF(prime).
        """
        # Convert int or float to GaloisFieldElement.
        if isinstance(other, int) or isinstance(other, float): other = self.galois_field[other]
        # If either value is zero, return zero
        if self.value == 0 or other.value == 0: return self.galois_field[0]
        # Sum of exponents modulo (size - 1)
        return self.galois_field.from_alpha(
            (self.exp + other.exp) % (self.galois_field.size - 1)
        )

    __rmul__ = __mul__ # Reverse multiplication.

    def __add__(self, other: GaloisFieldElement | int) -> GaloisFieldElement:
        """
            Add two numbers in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to add.
            
            Returns:
                GaloisFieldElement: The result of the addition in GF(prime).
        """
        # Convert int to GaloisFieldElement.
        if isinstance(other, int): other = self.galois_field[other]
        return self.galois_field[self.value ^ other.value] # Addition is XOR in GF(2^n).

    __radd__ = __add__ # Reverse addition.
    __sub__ = __add__ # Subtraction is the same as addition in GF(2^n).
    __rsub__ = __add__ # Reverse subtraction.

    def __xor__(self, other: GaloisFieldElement | int | float) -> GaloisFieldElement:
        """
            XOR two numbers in GF(prime).

            Args:
                other (GaloisFieldElement | int | float): The other number to XOR with.

            Returns:
                GaloisFieldElement: The result of the XOR in GF(prime).
        """
        if isinstance(other, int) or isinstance(other, float): # Convert int or float to GaloisFieldElement.
            other = self.galois_field[int(other)] # Convert int or float to GaloisFieldElement.
        return self + other # XOR is addition in GF(2^n).

    __rxor__ = __xor__ # Reverse XOR.

    def __abs__(self) -> GaloisFieldElement:
        """
            Return the absolute value of the element.

            Returns:
                GaloisFieldElement: The absolute value of the element.
        """
        return self # Absolute value is the element itself in GF(prime).

    def __eq__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if two numbers are equal in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if two numbers are equal in GF(prime), False otherwise.
        """
        return self.value == (other.value if isinstance(other, GaloisFieldElement) else other)

    def __ne__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if two numbers are not equal in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if two numbers are not equal in GF(prime), False otherwise.
        """
        return self.value != (other.value if isinstance(other, GaloisFieldElement) else other)

    def __lt__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if less than other in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if less than other in GF(prime), False otherwise.
        """
        return self.value < (other.value if isinstance(other, GaloisFieldElement) else other)

    def __le__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if less than or equal to other in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if less than or equal to other in GF(prime), False otherwise.
        """
        return self.value <= (other.value if isinstance(other, GaloisFieldElement) else other)

    def __gt__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if greater than other in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if greater than other in GF(prime), False otherwise.
        """
        return self.value > (other.value if isinstance(other, GaloisFieldElement) else other)

    def __ge__(self, other: GaloisFieldElement | int) -> bool:
        """
            Check if greater than or equal to other in GF(prime).

            Args:
                other (GaloisFieldElement | int): The other number to compare with.

            Returns:
                bool: True if greater than or equal to other in GF(prime), False otherwise.
        """
        return self.value >= (other.value if isinstance(other, GaloisFieldElement) else other)

    def __repr__(self):
        """
            Return the string representation of the GaloisFieldElement.

            Returns:
                str: The string representation of the GaloisFieldElement.
        """
        return f'GF(a={self.exp},v={self.value})'

    def __hash__(self) -> int:
        """
            Return the hash of the GaloisFieldElement, so that it can be used in sets and as dictionary keys.

            Returns:
                int: The hash of the GaloisFieldElement.
        """
        return hash((id(self.galois_field), self.value))

# GALOIS FIELD CLASS #

class GaloisField:
    """
        A class representing a simplified Galois Field GF(prime^n).

        Attributes:
            prime (int): The prime polynomial used to construct the field.
            size (int): The size of the field (number of elements).
            generator (int): The generator element of the field.
            log_table (list[int]): The logarithm table for the field.
            antilog_table (list[int]): The antilogarithm table for the field.
            elements_by_value (list[GaloisFieldElement]): The elements of the field indexed by their integer values.
        
        Methods:
            
    """

    def __init__(self, prime: int = 0x11D, size: int = 0x100, generator: int = 0x02):
        """
            Initialise a GaloisField instance.

            Args:
                prime (int): The prime polynomial used to construct the field.
                size (int): The size of the field (number of elements).
                generator (int): The generator element of the field.
        """
        self.prime = prime # The prime polynomial used to construct the field.
        self.size = size # The size of the field (number of elements).
        self.generator = generator # The generator element of the field.

        log_table = [0] * self.size # Initialise logarithm table.
        antilog_table = [0] * (self.size - 1) # Initialise antilogarithm table.

        value = 1 # Start with alpha^0 = 1.
        for i in range(self.size - 1): # Iterate over the size of the field.
            log_table[value] = i # Set log table entry.
            antilog_table[i] = value # Set antilog table entry.
            value *= self.generator # Multiply by generator to get next power.
            if value & self.size: value ^= self.prime # If value exceeds field size, reduce modulo prime.
            value &= (self.size - 1) # Ensure value is within field size.

        self.log_table = log_table # Set logarithm table.
        self.antilog_table = antilog_table # Set antilogarithm table.
        # Create elements indexed by their integer values.
        self.elements_by_value = [GaloisFieldElement(self, value, self.log_table[value] if value != 0 else None) for value in range(self.size)]

    def from_alpha(self, exp: int) -> GaloisFieldElement:
        """
            Create a GaloisFieldElement from its exponent representation.

            Args:
                exp (int): The exponent representation of the element.

            Returns:
                GaloisFieldElement: The corresponding GaloisFieldElement.
        """
        # Return element from antilog table.
        return self[self.antilog_table[exp % (self.size - 1)]]

    def __getitem__(self, i: int) -> GaloisFieldElement:
        """
            Get a GaloisFieldElement by its integer value.

            Args:
                i (int): The integer value of the element.
            
            Returns:
                GaloisFieldElement: The corresponding GaloisFieldElement.
        """
        # Return element by value, modulo field size.
        return self.elements_by_value[i % self.size]
