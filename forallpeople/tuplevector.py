"""
tuplevector: Treat tuples of any kind (e.g. namedtuple, NamedTuple) 
like one dimensional vectors!
by Connor Ferster 03/2019
"""

# TODO: Explore idea of removing all checks entirely and using a decorator
# function to wrap all vector functions (with try/excepts) to capture errors
# such as tuples of different lengths, elements that do not do math, or
# other type errors. Could vastly speed performance.

from math import pi, acos, sqrt
from numbers import Number
from typing import Union, Any, Optional


def same_shape(t1: tuple, t2: tuple) -> bool:
    """
    Returns True if t1 and t2 are the same shape.
    False, otherwise."""
    try:
        return len(t1) == len(t2)
    except:
        return False


def valid_for_arithmetic(other: Any) -> bool:
    """
    Returns True if object 'other' is valid for arithmetic operations.
    Returns False otherwise.
    """
    try:
        sum(other)  # This not a strong check but efficient for collections
        return True
    except TypeError:
        if isinstance(other, Number):
            return True
        return False


def tuple_check(t1: tuple, other: Any = None) -> Optional[bool]:
    """
    Returns None. Raises error if any of the tuple validation tests fail.
    """
    is_t1_tuple = isinstance(t1, tuple)
    is_other_tuple = isinstance(other, tuple)
    is_t1_valid = valid_for_arithmetic(t1)
    is_other_valid = valid_for_arithmetic(other)
    if is_t1_tuple and is_t1_valid and other is None:
        return True
    if is_t1_tuple and is_t1_valid and is_other_valid and is_other_tuple:
        return (True, True)
    elif is_t1_tuple and is_t1_valid and is_other_valid and not is_other_tuple:
        return (True, False)
    elif not is_t1_tuple:
        raise ValueError(
            f"Input object, {t1}, is not a valid tuple: first arg must be tuple."
        )
    elif not is_t1_valid:
        raise ValueError(f"Input tuple {t1} is not valid for arithmetic operations.")
    elif other is not None:
        if is_other_tuple and not same_shape(t1, other):
            raise ValueError(
                f"Input tuples must be same shape, not {len(t1)} and {len(other)}."
            )
        if is_other_tuple and not is_other_valid:
            raise ValueError(
                f"Input tuple, {other}, is not valid for arithmetic operations."
            )
        if not is_other_tuple and not valid_for_arithmetic(other):
            raise ValueError(
                f"Input object, {other}, is not valid for arithmetic operations."
            )


def dot(t1: tuple, t2: tuple) -> float:
    """
    Returns the dot product of the tuples, 't1' and 't2'.
    """
    _, t2_tup = tuple_check(t1, t2)
    if t2_tup:
        return sum([elem * t2[idx] for idx, elem in enumerate(t1)])
    else:
        raise ValueError(f"Input tuples must be the same length. Got: {t1}, {t2}")


def cross(t1: tuple, t2: tuple) -> tuple:
    """
    Returns the cross product of two 3-dimensional tuples, 't1' and 't2'.
    (Raises error if tuples are not 3-dimensional). Maintains the tuple type
    't1' (e.g. if it is a namedtuple).
    """
    t1_tup, other_tup = tuple_check(t1, t2)
    if len(t1) == len(t2) == 3:
        i = t1[1] * t2[2] - t2[1] * t1[2]
        j = -(t1[0] * t2[2] - t2[0] * t1[2])
        k = t1[0] * t2[1] - t2[0] * t1[1]
        result = (i, j, k)
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)
    else:
        raise TypeError(
            "Input tuples must be 3-dimensional. Got: {t1}, {t2}".format(t1=t1, t2=t2)
        )


def add(t1: tuple, other: Union[tuple, int, float]) -> tuple:
    """
    Returns a tuple of element-wise multiplication of 't1' and 'other'
    """
    _, other_tup = tuple_check(t1, other)
    if other_tup:
        result = tuple(elem + other[idx] for idx, elem in enumerate(t1))
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)
    else:
        result = (elem + other for elem in t1)
        try:
            print("3")
            return type(t1)(*result)
        except TypeError:
            print("4")
            return type(t1)(result)


def subtract(t1: tuple, other: Union[tuple, int, float]) -> tuple:
    """
    Returns a tuple of element-wise multiplication of 't1' and other
    """
    _, other_tup = tuple_check(t1, other)
    if other_tup:
        result = tuple(elem - other[idx] for idx, elem in enumerate(t1))
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)
    else:
        result = (elem - other for elem in t1)
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)


def multiply(t1: tuple, other: Union[tuple, int, float]) -> tuple:
    """
    Returns a tuple of element-wise multiplication of 't1' and other
    """
    _, other_tup = tuple_check(t1, other)
    if other_tup:
        result = tuple(elem * other[idx] for idx, elem in enumerate(t1))
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)
    else:
        result = (elem * other for elem in t1)
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)


def divide(
    t1: tuple, other: Union[tuple, int, float], ignore_zeros: bool = False
) -> tuple:
    """
    Returns a tuple of element-wise division of 't1' and 't2'.
    If 'ignore_empty' is set to False, then the division will
    ignore elements of 0/0 and will return zero for those
    elements instead.
    """
    t1_tup, other_tup = tuple_check(t1, other)
    if other_tup:
        if ignore_zeros:
            result = tuple(
                elem / other[idx] if other[idx] != 0 else 0
                for idx, elem in enumerate(t1)
            )
        else:
            result = tuple(
                elem / other[idx] if other[idx] != 0 else float("nan")
                for idx, elem in enumerate(t1)
            )
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)
    else:
        if ignore_zeros:
            result = tuple(
                elem / other if other != 0 else 0 for idx, elem in enumerate(t1)
            )
        else:
            result = tuple(
                elem / other if other != 0 else 0 for idx, elem in enumerate(t1)
            )
        try:
            return type(t1)(*result)
        except TypeError:
            return type(t1)(result)

    # acc = {}
    # if valid_for_arithmetic(other) and not isinstance(other, tuple):
    #     tuple_check(t1)
    #     for idx, val in enumerate(t1):
    #         if val == 0 and other == 0:
    #             acc.update({idx: float("nan")})
    #         elif other == 0:
    #             acc.update({idx: float("inf")})
    #         else:
    #             acc.update({idx: val/other})
    # else:
    #     tuple_check(t1, other)
    #     for idx, val in enumerate(t1):
    #         if val == 0 and other[idx] == 0:
    #             if ignore_zeros:
    #                 acc.update({idx: 0})
    #             else:
    #                 acc.update({idx: float("nan")})
    #         elif other[idx] == 0:
    #             acc.update({idx: float("inf")})
    #         else:
    #             acc.update({idx: val/other[idx]})
    # return collapse_to_tuple(acc, type(t1))


def vround(t: tuple, precision: int = 0) -> tuple:
    """
    Returns a tuple with elements rounded to 'precision'.
    """
    t_tup = tuple_check(t)
    if t_tup:
        result = tuple(round(elem, precision) for elem in t)
        try:
            return type(t)(*result)
        except TypeError:
            return type(t)(result)


def mean(t: tuple, ignore_empty: bool = False) -> float:
    """
    Returns the average of the values in the tuple, 't'. If 'ignore_empty'
    is True, then only the values that are not either 0 or None are averaged.
    If 'ignore_empty' is False, all values are used and None is taken as 0.
    """
    tuple_check(t)
    count = 0
    total = 0
    for val in t:
        if ignore_empty:
            if val == 0 or val == None:
                continue
            else:
                total += val
                count += 1
        else:
            total += val
            count += 1
    count = count or 1  # in case t is an empty vector
    return total / count


def magnitude(t: tuple) -> float:
    """
    Returns the vector magnitude of the tuple, 't' using the
    Pythagorean method.
    """
    tuple_check(t)
    mag_sqr = 0
    for val in t:
        mag_sqr += val**2
    return sqrt(mag_sqr)


def normalize(t: tuple) -> tuple:
    """
    Returns the normalized unit vector of the vector tuple, 't'.
    """
    return divide(t, magnitude(t))


def _clip(n: float) -> float:
    """
    Helper function to emulate numpy.clip for the specific
    use case of preventing math domain errors on the
    acos function by "clipping" values that are > abs(1).
    e.g. _clip(1.001) == 1
         _clip(-1.5) == -1
         _clip(0.80) == 0.80
    """
    sign = n / abs(n)
    if abs(n) > 1:
        return 1 * sign
    else:
        return n


def angle(t1: tuple, t2: tuple, degrees: bool = False) -> float:
    """
    Returns the angle between two vector tuples, 't1' and 't2',
    in rads. If 'degrees' = True, then returned in degrees.
    """
    tuple_check(t1, t2)
    rad2deg = 1.0
    if degrees:
        rad2deg = 180 / pi
    denom = magnitude(t1) * magnitude(t2)
    if denom == 0:
        return pi / 4 * rad2deg
    else:
        return acos(_clip(dot(t1, t2) / (magnitude(t1) * magnitude(t2)))) * rad2deg
