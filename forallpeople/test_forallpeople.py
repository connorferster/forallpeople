import pytest
import forallpeople as si
si.environment("test_definitions")



### TODO: add Ohms to definitions for testing
        # add energy modelling units to definitions for testing

### Testing parameters ###
env_dims = si.environment.units_by_dimension
env_fact = si.environment.units_by_factor
units = {"A": 0.05*si.kg,
         "B": 3.2e-3*si.m,
         "C": 1000*si.ft,
         "D": 1e6*si.N,
         "E": 0.2*si.kip,
         "F": 5*si.N*1e3*si.kip}
parameters = [(value,
               si.Physical._powers_of_derived(value.dimensions, env_dims))\
              for value in units.values()]

### Tests of the Physical class ###

## Testing "._repr_" methods in order of appearance in ._repr_template_() ##
def test__evaluate_dims_and_factor():
    func = si.Physical._evaluate_dims_and_factor
    assert func(si.Dimensions(1,1,-2,0,0,0,0), 
                1/0.45359237/9.80665, 
                1, env_fact, env_dims) == ("lb", False)
    assert func(si.Dimensions(1,1,-2,0,0,0,0), 
                1, 2, env_fact, env_dims) == ("N", True)
    assert func(si.Dimensions(1,1,-2,0,0,0,0), 
                1, 1, env_fact, env_dims) == ("N", True)
    assert func(si.Dimensions(0,1,0,0,0,0,0), 1/0.3048,
                1, env_fact, env_dims)
    assert func(si.Dimensions(1,0,0,0,0,0,0), 1, 
                3, env_fact, env_dims) == ("", True)
    assert func(si.Dimensions(1,1,1,0,0,0,0), 1, 
                1, env_fact, env_dims) == ("", False)
    
def test__format_symbol():
    pass
    
def test__get_units_by_factor():
    ftlb = si.lb * si.ft
    ft2 = si.ft**2
    func = si.Physical._get_units_by_factor
    assert func(si.ft.factor, si.ft.dimensions, env_fact, 1) == \
            {'ft': {'Dimension': si.Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0),
                    'Symbol': 'ft',
                    'Factor': 3.280839895013123}}
    assert func(ft2.factor, si.ft.dimensions, env_fact, 2) == \
            {'ft': {'Dimension': si.Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0),
                    'Symbol': 'ft',
                    'Factor': 3.280839895013123}}
    assert func(ftlb.factor, ftlb.dimensions, env_fact, 1) == \
            {'lbft': {'Dimension': si.Dimensions(kg=1, m=2, s=-2, A=0, cd=0, K=0, mol=0),
                      'Symbol': 'lb·ft',
                      'Factor': 0.7375621492772653}}
    assert func((ftlb*si.ft).factor,(ftlb*si.ft).dimensions, env_fact, 1) == dict()
    
def test_get_unit_components_from_dims():
    func = si.Physical._get_unit_components_from_dims
    assert func(si.Dimensions(1,1,-2,0,0,0,0)) == \
            [("kg", 1), ("m", 1), ("s", -2)]
    assert func(si.Dimensions(1,2,3,4,5,6,7)) == \
        [('kg', 1), ('m', 2), ('s', 3), ('A', 4),
         ('cd', 5), ('K', 6), ('mol', 7)]
    assert func(si.Dimensions(0,0,0,0,0,0,0)) == []

def test__get_unit_string():
    func = si.Physical._get_unit_string
    assert func([("kg", 1), ("m", 1), ("s", -2)], '') == 'kg⋅m⋅s⁻²'
    assert func([("kg", 1), ("m", 1), ("s", -2)], 'html') == \
           'kg&#8901;m&#8901;s<sup>-2</sup>'
    assert func([("kg", 1), ("m", 1), ("s", -2)], 'latex') == \
           r'\text{kg} \cdot \text{m} \cdot \text{s}^{-2}'
    assert func([('m', 2)], 'html') == 'm<sup>2</sup>'

def test__get_superscript_string():
    func = si.Physical._get_superscript_string
    assert func("-2") == '⁻²'
    assert func("1.39") == "¹'³⁹"
    assert func("-0.10") == "⁻⁰'¹⁰"

def test_latex():
    assert si.MPa.latex == r"1.000\ \text{MPa}"
    assert (2.5*si.kg*si.m**2.5).latex == r"2.500\ \text{kg} \cdot \text{m}^{2.5}"


def test_data():
    assert si.MPa.data == "Physical(value=1000000.0, dimensions=" +\
                                "Dimensions(kg=1, m=-1, s=-2, A=0, cd=0, K=0, mol=0), "+\
                                "factor=1, _precision=3)"
    assert si.ft.data == 'Physical(value=0.3048, dimensions=' +\
                               'Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0), ' +\
                               'factor=3.280839895013123, _precision=3)'

def test_in_units():
    ft = 1*si.ft
    m = 1*si.m
    kip = 1*si.kip
    lb = 1*si.lb
    assert ft.in_units("m").factor == 1.0
    assert m.in_units("ft").factor == 1/0.3048
    assert kip.in_units("lb").factor == (1000*si.lb).factor
    assert ((10*lb)**2).in_units("kip").factor == (0.1*si.kip*si.kip).factor

def test__get_derived_unit():
    func = si.Physical._get_derived_unit
    assert func(si.Dimensions(1,1,-2,0,0,0,0), env_dims) == \
    {'N': 
         {'Dimension': si.Dimensions(kg=1, m=1, s=-2, A=0, cd=0, K=0, mol=0),
          'Factor': 1}}
    assert func(si.Dimensions(1,0,0,0,0,0,0), env_dims) == {}
    assert func(si.Dimensions(1,0,-2,0,0,0,0), env_dims) == \
        {'N_m': 
            {'Dimension': si.Dimensions(kg=1, m=0, s=-2, A=0, cd=0, K=0, mol=0),
             'Factor': 1,
             'Symbol': 'N/m'}}
    assert func(si.Dimensions(1,1,1,1,1,1,1), env_dims) == {}

def test__dims_quotient():
    func = si.Physical._dims_quotient
    assert func(si.Dimensions(1,1,-2,0,0,0,0), env_dims) == si.Dimensions(1,1,1,0,0,0,0)
    assert func(si.Dimensions(3,3,-6,0,0,0,0), env_dims) == si.Dimensions(3,3,3,0,0,0,0)
    assert func(si.Dimensions(1,2,-2,0,0,0,0), env_dims) == si.Dimensions(1,1,1,0,0,0,0)
    
def test__dims_basis_multiple():
    func = si.Physical._dims_basis_multiple
    assert func(si.Dimensions(0,1,0,0,0,0,0)) == si.Dimensions(0,1,0,0,0,0,0)
    assert func(si.Dimensions(0,4,0,0,0,0,0)) == si.Dimensions(0,4,0,0,0,0,0)
    assert func(si.Dimensions(0,0,2.5,0,0,0,0)) == si.Dimensions(0,0,2.5,0,0,0,0)
    assert func(si.Dimensions(0,1,2.5,0,0,0,0)) == None
    assert func(si.Dimensions(1,1,-2,0,0,0,0)) == None
    
def test__powers_of_derived():
    func = si.Physical._powers_of_derived
    dims = si.Dimensions
    assert func(dims(0,1,0,0,0,0,0), env_dims) == (1, dims(0,1,0,0,0,0,0))
    assert func(dims(1,1,-2,0,0,0,0), env_dims) == (1, dims(1,1,-2,0,0,0,0))
    assert func(dims(3,3,-6,0,0,0,0), env_dims) == (3, dims(1,1,-2,0,0,0,0))
    assert func(dims(1,2,-2,0,0,0,0), env_dims) == (1, dims(1,2,-2,0,0,0,0))
    assert func(dims(0,4,0,0,0,0,0), env_dims) == (4, dims(0,1,0,0,0,0,0))
    assert func(dims(0,0,2.5,0,0,0,0), env_dims) == (2.5, dims(0,0,1,0,0,0,0))
    assert func(dims(3.6,3.6,-7.2, 0,0,0,0), env_dims) == (3.6, dims(1,1,-2,0,0,0,0))
    
    
def test__auto_prefix():
    func = si.Physical._auto_prefix
    assert func(1500, 1) == "k"
    assert func(1500, 2) == ""
    assert func(1.5e6, 2) == "k"
    assert func(1.5e6, 1) == "M"
    assert func(1.5e-3, 1) == "m"
    assert func(1.5e-6, 2) == "m"
    
def test__auto_prefix_kg():
    func = si.Physical._auto_prefix_kg
    assert func(1500, 1) == "M"
    assert func(1500, 2) == "k"
    assert func(1.5e6, 2) == "M"
    assert func(1.5e6, 1) == "G"
    assert func(1.5e-3, 1) == ""
    assert func(1.5e-6, 2) == ""
    assert func(1.5e-6, 1) == "m"
    
def test__auto_prefix_value():
    func = si.Physical._auto_prefix_value
    assert func(1500, 1) == 1.5
    assert func(1500, 2) == 1500
    assert func(52500, 1) == 52.5
    assert func(1.5e6, 2) == 1.5
    assert func(1.5e6, 1) == 1.5
    assert func(1.5e-6, 2) == 1.5
    assert func(1.5e-5, 1) == pytest.approx(15)
    assert func(1.5e-5, 2) == pytest.approx(15)
    
def test___eq__():
    assert si.m == si.m
    assert si.m == 1
    assert si.N == 1
    assert si.Pa == 1
    assert si.kg == 1
    with pytest.raises(ValueError):
        si.kg == si.m
        si.N == si.Pa
    
def test___gt__():
    assert si.m > si.ft
    assert si.MPa > si.Pa
    assert (5*si.m > 5*si.m) == False
    assert 5*si.kip > 30*si.N
    with pytest.raises(ValueError):
        5*si.kg > 3*si.m

def test___ge__():
    assert si.m >= si.ft
    assert si.MPa >= si.Pa
    assert 5*si.m >= 5*si.m
    assert 5*si.kN >= 5000*si.N
    with pytest.raises(ValueError):
        5*si.kg >= 5*si.m
    
def test___lt__():
    assert si.ft < si.m
    assert si.Pa < si.MPa
    assert (5*si.m < 5*si.m) == False
    assert 5*si.N < 5001*si.kN
    with pytest.raises(ValueError):
        5*si.kg < 5*si.m
    
def test___le__():
    assert si.ft <= si.m
    assert si.Pa <= si.MPa
    assert 5*si.m <= 5*si.m
    assert 5000*si.N <= 5*si.kN
    with pytest.raises(ValueError):
        5*si.kg <= 5*si.m
    
def test___add__():
    assert si.kg + si.kg == si.Physical(2, si.Dimensions(1,0,0,0,0,0,0), 1)
    assert si.m + si.ft == si.Physical(1.3048, si.Dimensions(0,1,0,0,0,0,0), 1)
    assert si.ft + si.m == si.Physical(1.3048, si.Dimensions(0,1,0,0,0,0,0), 1/0.3048)
    assert si.N + si.lb == si.Physical(5.4482216152605005, 
                                       si.Dimensions(1,1,-2,0,0,0,0), 
                                       1)
    assert si.lb + si.N == si.Physical(5.4482216152605005, 
                                       si.Dimensions(1,1,-2,0,0,0,0), 
                                       0.22480894309971047)
    assert si.ft + 3 == si.Physical(1.2192, si.Dimensions(0,1,0,0,0,0,0), 1/0.3048)
    with pytest.raises(ValueError):
        si.kg + si.m
        si.N + si.psf
    
    
def test___iadd__():
    with pytest.raises(ValueError):
        si.m += 3
    
def test___sub__():
    assert si.kg - si.kg == 0.
    assert si.m - si.ft == si.Physical(0.6952, si.Dimensions(0,1,0,0,0,0,0), 1)
    assert si.ft - si.m == si.Physical(-0.6952, si.Dimensions(0,1,0,0,0,0,0), 
                                       1/0.3048)
    assert si.N - si.lb == si.Physical(-3.4482216152605005, 
                                       si.Dimensions(1,1,-2,0,0,0,0),
                                       1)
    assert si.lb - si.N == si.Physical(3.4482216152605005, 
                                       si.Dimensions(1,1,-2,0,0,0,0), 
                                       0.22480894309971047)
    assert (si.ft - 3).value == pytest.approx(si.Physical(-0.6096, 
                                              si.Dimensions(0,1,0,0,0,0,0), 
                                              1/0.3048).value)
    with pytest.raises(ValueError):
        si.kg - si.m
        si.N - si.psf
    
def test___rsub__():
    assert 2 - si.ft == si.Physical(0.3048, si.Dimensions(0,1,0,0,0,0,0), 1/0.3048)
    assert 10 - si.N == si.Physical(9, si.Dimensions(1,1,-2,0,0,0,0), 1)
    
def test___isub__():
    with pytest.raises(ValueError):
        si.m -= 3
    
def test___mul__():
    assert si.m * si.m == si.Physical(1, si.Dimensions(0,2,0,0,0,0,0), 1)
    assert si.m * si.kg == si.Physical(1, si.Dimensions(1,1,0,0,0,0,0), 1)
    assert si.ft * si.m == si.Physical(0.3048, si.Dimensions(0,2,0,0,0,0,0), 1/0.3048)
    assert si.N * si.m == si.Physical(1, si.Dimensions(1,2,-2,0,0,0,0), 1)
    assert si.psf * si.m * si.m == si.Physical(47.88025898033584, 
                                               si.Dimensions(1,1,-2,0,0,0,0), 
                                               0.02088543423315013)
    assert 2 * si.ft == si.Physical(0.6096, si.Dimensions(0,1,0,0,0,0,0), 1/0.3048)
    assert (si.Physical(10, si.Dimensions(-1,-1,0,0,0,0,0), 1) 
            * si.Physical(2, si.Dimensions(1,1,0,0,0,0,0), 1)) == 20
    #assert (10*si.ksf) * (5*si.ft) * (2*si.ft) == 100*si.kip # TODO: Fix this gotcha
    assert ((10*si.ksf) * ((5*si.ft) * (2*si.ft))).value == \
            pytest.approx((100*si.kip).value)
    assert si.m * si.ft == si.Physical(.3048, si.Dimensions(0,2,0,0,0,0,0), 1.0)
    
def test___imul__():
    with pytest.raises(ValueError):
        si.m *= 3
    
def test___truediv__():
    assert si.m / si.m == 1
    assert si.m / si.s == si.Physical(1, si.Dimensions(0,1,-1,0,0,0,0), 1)
    assert si.kN / si.m / si.m == si.kPa
    assert (5*si.kN) / 2 == 2.5*si.kN
    assert (si.kip / (2*si.ft * 5*si.ft)).value == pytest.approx((0.100*si.ksf).value)

    
def test___rtruediv__():
    assert 2 / si.m == si.Physical(2, si.Dimensions(0,-1,0,0,0,0,0), 1)
    assert 10 / si.N == si.Physical(10, si.Dimensions(-1,-1,2,0,0,0,0), 1)
    
def test___pow__():
    assert si.N**2 == si.Physical(1, si.Dimensions(2,2,-4,0,0,0,0), 1)
    assert si.ft**3 == si.Physical(0.3048**3, si.Dimensions(0,3,0,0,0,0,0), (1/0.3048)**3)
    
def test___abs__():
    assert abs(-1*si.m) == si.m
    assert abs(-10*si.ft**2) == 10*si.ft**2
    assert abs(1*si.kip) == 1*si.kip
    
def test___float__():
    assert float(6.7*si.ft) == pytest.approx(6.7)
    assert float((52.5*si.kN)) == pytest.approx(52.5)
    assert float(34*si.kg*si.A*si.m) == pytest.approx(34)
    
## Test of Environment Class ##
    
#def test_load_environment():
#    assert "stub" == False
#    
#def test_instantiator():
#    assert "stub" == False
    
    
## Tests of supplementary math functions ##

def test_fsqrt():
    assert si.fsqrt(9*si.kPa) == 3*si.kPa
    assert si.fsqrt(9*si.MPa) == 3*si.MPa

## General arithmetic tests ##
def test_calc_mixed_units():
    pass