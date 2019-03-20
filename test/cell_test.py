
import unittest
from unittest import TestCase
from model.cell import Cell


class CellTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(CellTest, self).__init__(*args, **kwargs)
        self.__test_maxes = [2, 4, 9, 16, 25]

    def test_square_val(self):

        with self.assertRaises(ValueError):
            Cell(None, 0, 0, 1)
        with self.assertRaises(ValueError):
            Cell(0, 0, 0, 1)

        Cell(2, 0, 0, 1)
        Cell(4, 0, 0, 1)
        Cell(9, 0, 0, 1)
        Cell(16, 0, 0, 1)

        with self.assertRaises(ValueError):
            Cell(3, 0, 0, 1)
        with self.assertRaises(ValueError):
            Cell(5, 0, 0, 1)

    def test_xy_range(self):

        with self.assertRaises(ValueError):
            Cell(9, -1, 0, 1)
        with self.assertRaises(ValueError):
            Cell(9, 0, -1, 1)

        with self.assertRaises(ValueError):
            Cell(9, 9, 0, 1)
        with self.assertRaises(ValueError):
            Cell(9, 0, 9, 1)
        with self.assertRaises(ValueError):
            Cell(16, 16, 0, 1)
        with self.assertRaises(ValueError):
            Cell(16, 0, 16, 1)

    def test_value_range(self):

        with self.assertRaises(ValueError):
            Cell(9, 0, 0, 0)
        with self.assertRaises(ValueError):
            Cell(9, 0, 0, -1)
        with self.assertRaises(ValueError):
            Cell(9, 0, 0, 10)

        with self.assertRaises(ValueError):
            Cell(4, 0, 0, 5)
        with self.assertRaises(ValueError):
            Cell(16, 0, 0, 17)

    def test_xy_value(self):

        for x in self.__test_maxes:
            self.__test_xy_value_helper(x)

    def __test_xy_value_helper(self, val):
        for i in range(val):
            c = Cell(val, i, 0, 1)
            self.assertEqual(i, c.x())
            self.assertEqual(0, c.y())
            self.assertEqual(1, c.value())

            c = Cell(val, 0, i, 1)
            self.assertEqual(0, c.x())
            self.assertEqual(i, c.y())
            self.assertEqual(1, c.value())

            c = Cell(val, i, i, 1)
            self.assertEqual(i, c.x())
            self.assertEqual(i, c.y())
            self.assertEqual(1, c.value())

            c = Cell(val, 0, 0, i + 1)
            self.assertEqual(i + 1, c.value())

    def test_both_set(self):
        with self.assertRaises(ValueError):
            Cell(9, 0, 0, cur_val=1, poss_vals=set())
        with self.assertRaises(ValueError):
            Cell(9, 0, 0, cur_val=1, poss_vals=set(), is_initial=True)

    def test_neither_set(self):
        c = Cell(9, 0, 0)
        self.assertIsNone(c.value())
        self.assertIsNotNone(c.possible_vals())
        self.assertEqual(9, c.possible_count())

        for x in self.__test_maxes:
            s = set(range(1, x+1))
            c = Cell(x, 0, 0)
            self.assertEqual(s, c.possible_vals())

    def test_initial_value(self):

        with self.assertRaises(ValueError):
            Cell(9, 0, 0, is_initial=True)
        with self.assertRaises(ValueError):
            Cell(9, 0, 0, poss_vals=set(), is_initial=True)

        c = Cell(9, 0, 0, 1, is_initial=True)
        self.assertTrue(c.is_initial())

        c = Cell(9, 0, 0, 1)
        self.assertFalse(c.is_initial())

    def test_possible_values(self):

        for x in self.__test_maxes:
            vals = set(range(1, x + 1))
            Cell(x, 0, 0, poss_vals=vals)

            with self.assertRaises(ValueError):
                vals = set(range(0, x + 1))
                Cell(x, 0, 0, poss_vals=vals)

            with self.assertRaises(ValueError):
                vals = set(range(1, x + 2))
                Cell(x, 0, 0, poss_vals=vals)

        s = {2, 3, 4}
        c = Cell(9, 0, 0, poss_vals=s)
        self.assertEqual(s, c.possible_vals())

        s = {4, 2, 9}
        c = Cell(9, 0, 0, poss_vals=s)
        self.assertEqual(s, c.possible_vals())

    def test_max_sqrt(self):

        expected_vals = [1,2,3,4,5]

        for i in range(len(self.__test_maxes)):

            test_val = self.__test_maxes[i]
            expected = expected_vals[i]

            c = Cell(test_val, 0, 0)

            self.assertEqual(test_val, c.max_val())
            self.assertEqual(expected, c.max_sqrt())

    def test_value_poss_exclusive(self):

        c = Cell(9, 0, 0, 4)

        self.assertEqual(4, c.value())
        self.assertEqual(-1, c.possible_count())
        self.assertIsNone(c.possible_vals())

        c = Cell(9, 0, 0, poss_vals={2,3,4})

        self.assertIsNone(c.value())
        self.assertEqual({2,3,4}, c.possible_vals())
        self.assertEqual(3, c.possible_count())

    def test_possible_val_mod(self):
        # Change the set returned by the possible val method, make sure it stays the same.

        c = Cell(9, 0, 0, poss_vals={2,3,4})

        ret_set = c.possible_vals()
        ret_set.add(5)

        self.assertEqual(4, len(ret_set))
        self.assertEqual(3, len(c.possible_vals()))

        self.assertEqual(3, c.possible_count())

    def test_has_possible_val(self):

        test_set = {2,3,4}
        c = Cell(9, 0, 0, poss_vals=test_set)

        for i in range(1, 10):
            self.assertEqual(i in test_set, c.has_possible_val(i))

        test_set = {1,2,3,4,5,6,7,8,9}
        c = Cell(9, 0, 0)

        for i in range(1, 10):
            self.assertEqual(i in test_set, c.has_possible_val(i))

        # Test outside of range.
        self.assertFalse(c.has_possible_val(0))
        self.assertFalse(c.has_possible_val(-1))
        self.assertFalse(c.has_possible_val(10))

    def test_set_possible_value(self):

        c = Cell(9, 0, 0, poss_vals={1})

        c2 = c.set_possible_value(2)
        self.assertEqual({1}, c.possible_vals())
        self.assertEqual({1,2}, c2.possible_vals())

        # Out of range checks
        with self.assertRaises(ValueError):
            c.set_possible_value(0)

        with self.assertRaises(ValueError):
            c.set_possible_value(-1)

        with self.assertRaises(ValueError):
            c.set_possible_value(10)

        # Make sure setting a possible value on a set value doesn't change the value.
        c = Cell(9, 0, 0, 4)
        c2 = c.set_possible_value(5)

        self.assertFalse(c2.has_possible_val(5))
        self.assertEqual(-1, c2.possible_count())
        self.assertEqual(4, c2.value())

    def test_clear_possible_value(self):

        c = Cell(9, 0, 0, poss_vals={2, 3, 4})

        c2 = c

        for i in range(1, 10):
            c2 = c2.clear_possible_value(i)

        self.assertEqual({2,3,4}, c.possible_vals())
        self.assertEqual(set(), c2.possible_vals())

        c2 = c.clear_possible_value(5)
        self.assertEqual(c, c2)

        c2 = c.clear_possible_value(4)
        self.assertEqual({2,3}, c2.possible_vals())
        self.assertEqual({2,3,4}, c.possible_vals())

        c = Cell(9, 0, 0, 4)

    def test_set_value(self):

        c = Cell(9, 0, 0)

        c2 = c.set_value(0)

    def test_modify_initial_cell(self):

        c = Cell(9, 0, 0, 4, is_initial=True)

        with self.assertRaises(ValueError):
            c.set_possible_value(3)

        with self.assertRaises(ValueError):
            c.set_value(5)

        with self.assertRaises(ValueError):
            c.clear_value(6)

        with self.assertRaises(ValueError):
            c.clear_possible_value(2)

    

