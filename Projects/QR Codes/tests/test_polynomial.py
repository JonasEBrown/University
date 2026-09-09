import unittest
from Polynomial import Polynomial
from GaloisField import GaloisField

class TestPolynomial(unittest.TestCase):
    def setUp(self):
        self.gf = GaloisField()

    def test_init_requires_coefficients(self):
        with self.assertRaises(ValueError):
            Polynomial([])
        p = Polynomial([1, 0, -3])
        self.assertEqual(p.degree, 3)
        self.assertEqual(p.coefficients, [1, 0, -3])

    def test_add_same_length(self):
        p = Polynomial([1, 2, 3])
        q = Polynomial([4, 5, 6])
        r = p + q
        self.assertEqual(r.coefficients, [5, 7, 9])

    def test_add_different_length(self):
        p = Polynomial([1, 2])
        q = Polynomial([3, 4, 5, 6])
        r = p + q
        self.assertEqual(r.coefficients, [4, 6, 5, 6])

    def test_sub_is_add_mul_neg_one(self):
        p = Polynomial([1, -2, 3])
        q = Polynomial([3, 1, -1])
        r = p - q
        # p - q == p + (q * -1)
        expected = (p + (q * -1)).coefficients
        self.assertEqual(r.coefficients, expected)

    def test_mul_by_scalar(self):
        p = Polynomial([1, 2, 3])
        r = p * 2
        self.assertEqual(r.coefficients, [2, 4, 6])

    def test_mul_by_polynomial(self):
        # (1 + 2x + 3x^2) * (4 + 5x) = 4 + 13x + 22x^2 + 15x^3
        p = Polynomial([1, 2, 3])
        q = Polynomial([4, 5])
        r = p * q
        self.assertEqual(r.coefficients, [4, 13, 22, 15])

    def test_xor_scalar(self):
        p = Polynomial([1, 2, 3])
        r = p ^ 1
        self.assertEqual(r.coefficients, [0, 3, 2])

    def test_xor_polynomial_galois(self):
        # In GF, XOR is coefficient-wise and removes trailing zero GF elements
        a = self.gf[5]
        b = self.gf[5]
        c = self.gf[0]
        p = Polynomial([a, b, c])
        q = Polynomial([self.gf[1], self.gf[2], self.gf[0]])
        r = p ^ q
        # (5^1, 5^2) = (4, 7), trailing zero GF element removed
        self.assertEqual([e.value for e in r.coefficients], [4, 7])

    def test_copy_and_shift(self):
        p = Polynomial([1, 2, 3])
        c = p.copy()
        self.assertIsNot(p, c)
        self.assertEqual(c.coefficients, [1, 2, 3])
        s = p.shift(2)
        self.assertEqual(s.coefficients, [0, 0, 1, 2, 3])

    def test_str_pretty_print(self):
        self.assertEqual(str(Polynomial([0, 0, 0])), '0')
        self.assertEqual(str(Polynomial([5])), '5')
        self.assertEqual(str(Polynomial([1, 0, 1])), '1 + x²')
        self.assertEqual(str(Polynomial([-1, 2, 0, -3])), '-1 + 2x - 3x³')

if __name__ == '__main__':
    unittest.main()
