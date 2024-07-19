import pytest
from PySide2.QtCore import Qt  # Importing Qt for mouse button reference
from main import MainWindow  # Adjust the import based on your file structure


# creating a fixture for the window that will be used across all methods
@pytest.fixture
def app(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


# -------------------------testing our qt application-------------------------
def test_empty_expression(app, qtbot):
    app.expression_input.setText("")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert app.message_label.text() == "Please Enter an Expression"


def test_invalid_expression(app, qtbot):
    app.expression_input.setText("5**")
    app.min_x_input.setText("-10")
    app.max_x_input.setText("10")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert app.message_label.text().startswith("Invalid Expression")


def test_valid_expression(app, qtbot):
    app.expression_input.setText("5*x^3 + 2*x")
    app.min_x_input.setText("-10")
    app.max_x_input.setText("10")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert app.message_label.text() == "Function plotted successfully."


def test_min_max_values(app, qtbot):
    app.expression_input.setText("5*x")
    app.min_x_input.setText("10")
    app.max_x_input.setText("5")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert app.message_label.text() == "Min Value Must Be Less Than Max Value."


def test_invalid_min_max(app, qtbot):
    app.expression_input.setText("5*x")
    app.min_x_input.setText("invalid")
    app.max_x_input.setText("10")
    qtbot.mouseClick(app.plot_button, Qt.LeftButton)
    assert app.message_label.text() == "Min and Max Values Must Be Valid Numbers."

# pytest test_function_plotter_qt.py