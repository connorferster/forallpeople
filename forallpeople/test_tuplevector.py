import math
import fractions
import decimal
from collections import namedtuple
import forallpeople.tuplevector as vec
import pytest

Point = namedtuple("Point", ["x", "y", "z"])
Dimensions = namedtuple("Dimensions", ["kg", "m", "s", "A", "cd", "K", "mol"])

P1 = Point(2.0, 3.4, 1.0)
P2 = Point(1.5, 2.8, 4.5)
P3 = Point(1, 1, 0)
P4 = Point(1, 0, 0)
P5 = Point(-1, 0, 0)
P6 = Point(3, 4, 0)
P7 = Point(0, 0, 0)
D1 = Dimensions(1.0, 1.0, -2.0, 0, 0, 0, 0)
D2 = Dimensions(2.0, 2.0, -4.0, 0, 0, 0, 0)
D3 = Dimensions(1.0, 2.0, -2.0, 0, 0, 0, 0)
D4 = Dimensions(-1, 1, 0, 0, 0, 0, 0)
T1 = (4.5, 1.1112, 2)
T2 = (1.2, 4, 3.267)
T3 = (3, 4, 0)
T4 = (0, 0, 0)
T5 = (1 / 2, math.sqrt(3) / 2, 0)
T6 = (1 / 2, 0, 0)
NT1 = ("A", 2, 3.4)
NT2 = ("B", "C", "D")
L1 = tuple(range(0, 100))
L2 = tuple(range(1, 101))
LT1 = list(range(0, 100))
LT2 = list(range(1, 101))


def test_valid_for_arithmetic():
    assert vec.valid_for_arithmetic(134) == True
    assert vec.valid_for_arithmetic(23.5) == True
    assert vec.valid_for_arithmetic(complex(3, 4)) == True
    assert vec.valid_for_arithmetic("apple") == False
    assert vec.valid_for_arithmetic(fractions.Fraction(3, 4)) == True
    assert vec.valid_for_arithmetic(decimal.Decimal(3.123145645879)) == True
    assert vec.valid_for_arithmetic(P1) == True
    assert vec.valid_for_arithmetic(T1) == True
    assert vec.valid_for_arithmetic(LT1) == True


def test_tuple_check():
    with pytest.raises(ValueError):
        vec.tuple_check(3, T1)
        vec.tuple_check(LT1, 3)
        vec.tuple_check(NT1)
        vec.tuple_check(D1, NT2)
        vec.tuple_check(T3, NT2)
        vec.tuple_check(T3, "A")
        vec.tuple_check((1,), (2,), (3,))


def test_same_shape():
    assert vec.same_shape(P1, D1) == False
    assert vec.same_shape(T2, L1) == False
    assert vec.same_shape(NT1, NT2) == True
    assert vec.same_shape(T1, P3) == True


def test_dot():
    assert vec.dot(P1, P3) == 5.4
    assert vec.dot(D1, D3) == 7.0
    assert vec.dot(T1, T2) == 16.3788


def test_cross():
    assert vec.cross(P1, P3) == Point(x=-1.0, y=1.0, z=-1.4)
    assert vec.cross(T1, T2) == (-4.3697096, -12.301499999999999, 16.66656)


def test_add():
    assert vec.add(P1, P3) == Point(x=3.0, y=4.4, z=1.0)
    assert vec.add(D2, D3) == Dimensions(
        kg=3.0, m=4.0, s=-6.0, A=0.0, cd=0.0, K=0.0, mol=0.0
    )
    assert vec.add(L1, L2) == tuple(range(1, 200, 2))


def test_subtract():
    assert vec.subtract(P1, P3) == Point(x=1.0, y=2.4, z=1.0)
    assert vec.subtract(D2, D3) == Dimensions(
        kg=1.0, m=0.0, s=-2.0, A=0.0, cd=0.0, K=0.0, mol=0.0
    )
    assert vec.subtract(L1, L2) == tuple(-1 for n in range(0, 100))


def test_multiply():
    assert vec.multiply(P1, P3) == Point(x=2.0, y=3.4, z=0.0)
    assert vec.multiply(D2, D3) == Dimensions(
        kg=2.0, m=4.0, s=8.0, A=0.0, cd=0.0, K=0.0, mol=0.0
    )
    assert vec.multiply(P3, 3.5) == Point(x=3.5, y=3.5, z=0)


def test_divide():
    assert str(vec.divide(P1, P3)) == str(Point(x=2.0, y=3.4, z=float("nan")))
    assert vec.divide(D2, D1, ignore_zeros=True) == Dimensions(*(2, 2, 2, 0, 0, 0, 0))
    assert vec.divide(D2, 2) == D1


def test_magnitude():
    assert vec.magnitude(P6) == 5.0
    assert vec.magnitude(P7) == 0
    assert vec.magnitude(T3) == 5.0
    assert vec.magnitude(P3) == math.sqrt(2)
    assert vec.magnitude(D4) == math.sqrt(2)


def test_vround():
    assert vec.vround(T1, 3) == (4.5, 1.111, 2)
    assert vec.vround(P2, 0) == Point(x=2, y=3, z=4)


def test_mean():
    assert vec.mean(P6) == 2.3333333333333335
    assert vec.mean(D1) == 0
    assert vec.mean(T2) == 2.8223333333333334
    assert vec.mean(P6, True) == 3.5
    assert vec.mean(L1) == 49.5


def test__clip():
    assert vec._clip(-1) == -1
    assert vec._clip(-1.00001) == -1
    assert vec._clip(1.5) == 1
    assert vec._clip(-0.3) == -0.3
    assert vec._clip(0.4) == 0.4


def test_normalize():
    assert vec.normalize(P1) == Point(
        x=0.49147318718299043, y=0.8355044182110838, z=0.24573659359149522
    )
    assert vec.normalize(T1) == (
        0.8913991044053705,
        0.22011615218116617,
        0.39617737973572026,
    )
    assert vec.normalize(D3) == Dimensions(
        kg=0.3333333333333333,
        m=0.6666666666666666,
        s=-0.6666666666666666,
        A=0.0,
        cd=0.0,
        K=0.0,
        mol=0.0,
    )


def test_angle():
    assert vec.angle(P3, P4) == 0.7853981633974484
    assert vec.angle(P3, P4, True) == 45.00000000000001
    assert vec.angle(T5, T6) == 1.0471975511965976
    assert vec.angle(T5, T6, True) == 59.99999999999999
