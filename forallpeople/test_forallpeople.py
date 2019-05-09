import pytest
import forallpeople as si
si.environment("structural")
ftlb = si.lb * si.ft

## Tests of the Physical class ##

def test__get_symbol_by_factor():
    assert si.Physical._get_symbol_by_factor(si.ft.factor, 
                                             si.ft.dimensions) == \
            si.environment.environment["ft"]
    
    assert si.Physical._get_symbol_by_factor(ftlb.factor, ftlb.dimensions) == \
            si.environment.environment["lbft"]
    assert si.Physical._get_symbol_by_factor((ftlb*si.ft).factor, (ftlb*si.ft).dimensions) ==\
            dict()
    
def test__return_symbol():
    assert si.lb._return_symbol() == "lb"
    assert si.ft._return_symbol() == "ft"
    assert si.N._return_symbol() == "N"
    assert si.kg._return_symbol() == ""
    
def test__return_prefix():
    assert "stub" == False

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

def test__get_derived_name():
    assert "stub" == False

def test__dims_quotient():
    assert "stub" == False
    
def test__dims_basis_multiple():
    assert "stub" == False
    
def test__powers_of_derived():
    assert "stub" == False
    
def test__dims_original():
    assert "stub" == False
    
def test__unit_data_from_dims():
    assert "stub" == False
    
def test__auto_value():
    assert "stub" == False
    
def test__auto_prefix():
    assert "stub" == False
    
def test__auto_prefix_kg():
    assert "stub" == False
    
def test__auto_prefix_value():
    assert "stub" == False
    
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
