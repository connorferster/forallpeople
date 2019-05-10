import pytest
import forallpeople as si

si.environment("test_definitions")
env_dims = si.environment.units_by_dimension
env_fact = si.environment.units_by_factor
ftlb = si.lb * si.ft

## Tests of the Physical class ##

def test__get_units_by_factor():
    func = si.Physical._get_units_by_factor
    assert func(si.ft.factor, si.ft.dimensions, env_fact) == \
            si.environment.environment["ft"]
    assert func(ftlb.factor, ftlb.dimensions, env_fact) == \
            si.environment.environment["lbft"]
    assert func((ftlb*si.ft).factor, (ftlb*si.ft).dimensions, env_fact) == dict()
    
def test__return_symbol():
    assert si.lb._return_symbol() == "lb"
    assert si.ft._return_symbol() == "ft"
    assert si.N._return_symbol() == "N"
    assert si.kg._return_symbol() == ""
    
def test__return_prefix():
    assert (si.N*1000)._return_prefix() == "k"
    assert (si.N*0.001)._return_prefix() == "m"
    assert si.kg._return_prefix() == "k"
    assert (si.kg*1e-6)._return_prefix() == "m"
    assert si.N._return_prefix() == ""
    assert (si.m * 1e6)._return_prefix() == "M"
    
def test_get_unit_components_from_dims():
    func = si.Physical._get_unit_components_from_dims
    assert func(si.Dimensions(1,1,-2,0,0,0,0)) == \
            [("kg", 1), ("m", 1), ("s", -2)]
    assert func(si.Dimensions(1,2,3,4,5,6,7)) == \
        [('kg', 1), ('m', 2), ('s', 3), ('A', 4),
         ('cd', 5), ('K', 6), ('mol', 7)]
    assert func(si.Dimensions(0,0,0,0,0,0,0)) == []

def test__get_unit_string():
    assert "stub" == False

def test__get_superscript_string():
    assert "stub" == False

def test__return_value():
    assert "stub" == False

def test__return_units():
    assert "stub" == False

def test__return_exponent():
    assert "stub" == False

def test_latex():
    assert "stub" == False

def test_components():
    assert "stub" == False

def test_in_units():
    assert "stub" == False

def test_si():
    assert "stub" == False

def test__get_derived_unit():
    func = si.Physical._get_derived_unit
    assert "stub" == False

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
    assert func(si.Dimensions(0,1,0,0,0,0,0), env_dims) == 1
    assert func(si.Dimensions(1,1,-2,0,0,0,0), env_dims) == 1
    assert func(si.Dimensions(3,3,-6,0,0,0,0), env_dims) == 3
    assert func(si.Dimensions(1,2,-2,0,0,0,0), env_dims) == 1
    assert func(si.Dimensions(0,4,0,0,0,0,0), env_dims) == 4
    assert func(si.Dimensions(0,0,2.5,0,0,0,0), env_dims) == 2.5
    assert func(si.Dimensions(3.6,3.6,-7.2, 0,0,0,0), env_dims) == 3.6
    
def test__dims_original():
    func = si.Physical._dims_original
    assert func(si.Dimensions(0,1,0,0,0,0,0), env_dims) == si.Dimensions(0,1,0,0,0,0,0)
    assert func(si.Dimensions(1,1,-2,0,0,0,0), env_dims) == si.Dimensions(1,1,-2,0,0,0,0)
    assert func(si.Dimensions(3,3,-6,0,0,0,0), env_dims) == si.Dimensions(1,1,-2,0,0,0,0)
    assert func(si.Dimensions(1,2,-2,0,0,0,0), env_dims) == si.Dimensions(1,2,-2,0,0,0,0)
    
def test__auto_value():
    func = si.Physical._auto_value
    assert func(1500, si.Dimensions(0,1,0,0,0,0,0), 1, env_dims) == 1500
    assert func(500, si.Dimensions(2,2,-4,0,0,0,0), 1, env_dims) == 500
    assert func(500, si.Dimensions(2,2,-4,0,0,0,0), 1/0.3048, env_dims) == 5381.95520835486
    
def test__auto_prefix():
    func = si.Physical._auto_prefix
    assert func(1500, si.Dimensions(0,1,0,0,0,0,0), env_dims) == "k"
    assert func(1500000, si.Dimensions(0,1,0,0,0,0,0), env_dims) == "M"
    assert func(15, si.Dimensions(0,1,0,0,0,0,0), env_dims) == ""
    assert func(1500000, si.Dimensions(1,1,-2,0,0,0,0), env_dims) == "M"
    assert func(25000000, si.Dimensions(2,2,-4,0,0,0,0), env_dims) == "k"
    
def test__auto_prefix_kg():
    func = si.Physical._auto_prefix_kg
    assert func(1500, si.Dimensions(1,0,0,0,0,0,0), env_dims) == "M"
    assert func(.015, si.Dimensions(1,0,0,0,0,0,0), env_dims) == ""
    
def test__auto_prefix_value():
    func = si.Physical._auto_prefix_value
    assert func(1500, si.Dimensions(0,1,0,0,0,0,0), 1, env_dims) == 1.5
    assert func(1500000, si.Dimensions(0,1,0,0,0,0,0), 1, env_dims) == 1.5
    assert func(15, si.Dimensions(0,1,0,0,0,0,0), 1, env_dims) == 15
    assert func(0.15, si.Dimensions(1,1,-2,0,0,0,0), 1, env_dims) == 150
    assert func(0.00015, si.Dimensions(2,2,-4,0,0,0,0), 1, env_dims) == 150
    
def test___eq__():
    assert "stub" == False
    
def test___gt__():
    assert "stub" == False
    
def test___ge__():
    assert "stub" == False
    
def test___lt__():
    assert "stub" == False
    
def test___le__():
    assert "stub" == False
    
def test___add__():
    assert "stub" == False
    
def test___iadd__():
    assert "stub" == False
    
def test___sub__():
    assert "stub" == False
    
def test___rsub__():
    assert "stub" == False
    
def test___isub__():
    assert "stub" == False
    
def test___mul__():
    assert "stub" == False
    
def test___imul__():
    assert "stub" == False
    
def test___truediv__():
    assert "stub" == False
    
def test___rtruediv__():
    assert "stub" == False
    
def test___pow__():
    assert "stub" == False
    
def test___abs__():
    assert "stub" == False
    
## Test of Environment Class ##
    
def test_load_environment():
    assert "stub" == False
    
def test_instantiator():
    assert "stub" == False
    
    
## Tests of supplementary math functions ##

def test_fsqrt():
    assert "stub" == False
