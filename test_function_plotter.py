from main import FunctionPlotter
import pytest


@pytest.mark.parametrize("expression,expected_output", [
        ("@ + 3", "Invalid Characters Entered"),
        ("x^y", "Invalid Characters Entered"),
        ("sqr(x)", "Invalid Characters Entered"),
        ("$ = 3", "Invalid Characters Entered"),
        ("m^2", "Invalid Characters Entered"),
        ("log(x)", "Invalid Characters Entered"),
    ])
def test_invalid_characters(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("((log10()))", "Expression Contains Empty Brackets"),
        ("()", "Expression Contains Empty Brackets"),
        ("sqrt()", "Expression Contains Empty Brackets"),
    ])
def test_empty_brackets(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("(log10(x))(x)(((sqrt(x))", "Brackets Are NOT Balanced"),
        ("(x)", "Valid Expression"),
        ("(x+(1))", "Valid Expression"),
    ])
def test_parentheses_balance(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("-x", "Valid Expression"),
        ("+x", "Valid Expression"),
        ("^x", "Invalid Operators at The Beginning"),
        ("*x", "Invalid Operators at The Beginning"),
        ("/x", "Invalid Operators at The Beginning"),
    ])
def test_initial_char(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("x-1-", "Invalid Operators at The End"),
        ("x+", "Invalid Operators at The End"),
        ("2x^", "Invalid Operators at The End"),
        ("x^2", "Valid Expression"),
        ("x-1/", "Invalid Operators at The End"),
        ("x+1*", "Invalid Operators at The End"),
    ])
def test_last_char(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("(x^2)5", "Digits After Brackets Without Operators"),
        ("(x)6", "Digits After Brackets Without Operators"),
        ("xlog10(x)*4", "Valid Expression"),
    ])
def test_existent_digits_after_brackets(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression, expected_output", [
        ("x5", "Digits After X Without Operators"),
        ("x*5", "Valid Expression"),
        ("5x", "Valid Expression"),
    ])
def test_digits_after_x(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("xx+1", "Two or More X variable Next to Each Other"),
        ("x*x+1", "Valid Expression"),
        ("x^x", "Valid Expression"),
        ("log10(xx)", "Two or More X variable Next to Each Other"),
    ])
def test_successive_x(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("1------3+x", "Valid Expression"),
        ("1++++++3+x", "Valid Expression"),
        ("1******3+x", "Invalid Successive Operators"),
        ("1//////3+x", "Invalid Successive Operators"),
        ("x^^2", "Invalid Successive Operators"),
        ("x/+3", "Valid Expression"),
        ("x/-5", "Valid Expression"),
        ("x", "Valid Expression"),
    ])
def test_successive_operators(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("5/-0", "Cannot Divide by Zero"),
        ("x/(0)", "Cannot Divide by Zero"),
        ("log10(x)/0+0.5", "Cannot Divide by Zero"),
        ("x/(0+1)", "Valid Expression"),
    ])
def test_division_by_zero(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output


@pytest.mark.parametrize("expression,expected_output", [
        ("y = 1", "Valid Expression"),
        ("3 = y", "Valid Expression"),
        ("2 = x", "Valid Expression"),
        ("4", "Valid Expression"),
        ("x = 1", "Valid Expression"),
        ("-2", "Valid Expression"),
        ("y = x", "Valid Expression"),
        ("y = 2m", "Invalid Characters Entered")
    ])
def test_constant_expression(expression, expected_output):
    test = FunctionPlotter(expression, 1, 20)
    assert test.check_validity() == expected_output