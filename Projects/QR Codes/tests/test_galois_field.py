import unittest
from GaloisField import GaloisField, GaloisFieldElement

class TestGaloisField(unittest.TestCase):
    def setUp(self):
        self.gf = GaloisField(0x11D, 0x100, 0x02)

    def test_size_and_tables(self):
        # size is 256 and antilog table size is 255
        self.assertEqual(self.gf.size, 256)
        self.assertEqual(len(self.gf.antilog_table), 255)
        self.assertEqual(len(self.gf.log_table), 256)

    def test_getitem_wraps(self):
        self.assertEqual(self.gf[0].value, 0)
        # index wraps modulo size
        self.assertEqual(self.gf[256].value, 0)
        self.assertEqual(self.gf[257].value, 1)

    def test_from_alpha_cycle(self):
        # alpha^0 == 1
        self.assertEqual(self.gf.from_alpha(0).value, 1)
        # alpha^(size-1) cycles
        self.assertEqual(self.gf.from_alpha(255 - 1).value, self.gf.antilog_table[(255 - 1) % (self.gf.size - 1)])
        self.assertEqual(self.gf.from_alpha(255).value, self.gf.antilog_table[(255) % (self.gf.size - 1)])

    def test_addition_xor(self):
        a = self.gf[5]
        b = self.gf[7]
        # in GF(2^n), addition is XOR of values
        self.assertEqual((a + b).value, 5 ^ 7)
        # subtraction is same as addition
        self.assertEqual((a - b).value, 5 ^ 7)

    def test_multiplication_rules(self):
        zero = self.gf[0]
        one = self.gf[1]
        a = self.gf[37]
        b = self.gf[99]
        # zero times anything is zero
        self.assertEqual((zero * a).value, 0)
        self.assertEqual((a * zero).value, 0)
        # one is multiplicative identity
        self.assertEqual((one * a).value, a.value)
        # exponent addition modulo size-1 (255)
        if a.value != 0 and b.value != 0:
            expected_exp = (a.exp + b.exp) % (self.gf.size - 1)
            self.assertEqual((a * b).exp, expected_exp)

    def test_eq_ne_and_ordering(self):
        a = self.gf[10]
        b = self.gf[10]
        c = self.gf[11]
        self.assertTrue(a == b)
        self.assertTrue(a != c)
        self.assertTrue(a < c)
        self.assertTrue(c > a)
        self.assertTrue(a <= b)
        self.assertTrue(c >= b)

    def test_xor_operator(self):
        a = self.gf[12]
        b = self.gf[3]
        self.assertEqual((a ^ b).value, 12 ^ 3)
        # int/float auto-conversion
        self.assertEqual((a ^ 3).value, 12 ^ 3)
        self.assertEqual((a ^ 3.0).value, 12 ^ 3)

    def test_repr_and_hash(self):
        a = self.gf[42]
        self.assertIn('GF', repr(a))
        # hash is based on (id(field), value); two separate fields produce different hashes
        gf2 = GaloisField(0x11D, 0x100, 0x02)
        a2 = gf2[42]
        self.assertNotEqual(hash(a), hash(a2))

if __name__ == '__main__':
    unittest.main()
