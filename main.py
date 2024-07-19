# importing needed modules
import sys
import numpy as np
import math
import matplotlib.pyplot as plt
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
import pytest

# a class for the mathematical expression (function entered)
class FunctionPlotter():
    # static attribute
    __valid_expressions = ["log10(", "sqrt("]  # a list with the supported operators or functions (sqrt and log10() in our case)

    # ------------------------------------------- Constructor -------------------------------------------
    def __init__(self, expression, min_x, max_x):
        # initializations
        self.__expression = expression                    # a variable to hold the mathematical expression as a string
        self.__remove_extra_zeros()                       # removing all the unnecessary zeros e.g. 00011*x^2 --> 11*x^2
        self.__add_needed_multiplications()               # adding all the needed multiplication signs
        self.__remove_spaces()                            # removing the spaces to start the expression
        self.__const_type, self.__constant = self.__is_const_expression()       # determining if it's a constant expression or not
                                                                        # if it's we get the type and the constant value
        self.__min_x, self.__max_x = min_x, max_x           # variables to hold the domain max & min values
        self.__valid = False                              # a variable to tell if the expression is valid (no errors in it)

    def is_valid(self):
        return self.__valid

    # ------------------------------------------- Helper Methods -------------------------------------------
    # a method to remove spaces as our program operates only on expressions with no spaces
    def __remove_spaces(self):
        self.__expression = self.__expression.replace(" ", "")

    # a method to remove the unnecessary zeros from the expression
    def __remove_extra_zeros(self):
        i, end_point = 0, len(self.__expression) - 1

        while i < end_point:
            # the zeroes after the decimal points will not be removed as they are important e.g. 0.000001 can't be 0.1
            if self.__expression[i] == ".":
                i += 1                                      # moving to the next digit
                # navigating to the last digit in the expression
                while self.__is_digit(self.__expression[i] and i < len(self.__expression)):
                    i += 1

            # the zeros will be removed in case they are followed by digits e.g. 000001 --> 1
            if self.__expression[i] == '0' and self.__is_digit(self.__expression[i+1]):
                self.__expression = self.__expression[:i] + self.__expression[i+1:]           # removing the unnecessary zero
                i -= 1
                end_point -= 1                        # since one letter is remove, we increment the chars counter
            i += 1

    # method that checks if a character is a digit (0:9)
    def __is_digit(self, char):
        return str(char) in "0123456789"

    # method that returns the position of the item before the new right bracket
    def __find_right_bracket_index(self, start):
        # if the starting item is "(" that means we need to find its closing ")"
        if not self.__is_digit(self.__expression[start]):
            return self.__expression.index(')', start)

        # otherwise, this start digit is part of a number and we need to find the position of the last digit of that number
        for i in range(start, len(self.__expression)-1):
            if self.__is_digit(self.__expression[i]) and not self.__is_digit(self.__expression[i+1]):
                if(self.__expression[i+1]) == ")":
                    return i + 1
                else:
                    return i
        return len(self.__expression) - 1                     # the last digit is the last item in the expression

    # determining if it's a constant expression
    def __is_const_expression(self):
        # in case it's y = a, we change the type to constant y expression and we get rid of the unnecessary y =
        if self.__expression[:2] == "y=" or self.__expression[-2:] == "=y":
            self.__expression = self.__expression.replace("y=", "").replace("=y", "")
            const_type = "y"
        # in case it's y = a, we change the type to constant y expression
        elif self.__expression[:2] == "x=" or self.__expression[-2:] == "=x":
            const_type = "x"

        else:
            # otherwise it can be just number maybe the user entered something like 5 which also means y = 5
            try:
                return "y", eval(self.__expression)
            # if not, an exception will happen and this can be valid or invalid based on other checkers
            except:
                return "None", 0

        # if it's a constant expression we get rid of the x=, =x, y=, or =y part and just leave the constant
        new_expression = self.__expression.replace("x=", "").replace("=x", "")
        try:
            # if after the remove the function is evaluation successfully, that means the expression is a valid constant expression
            return const_type, eval(new_expression)

        except:
            # if it gives an error that means there is another letter in the expression and it's invalid
            # e.g. y = 4m --> 4m (invalid)
            return "None", 0

    # a method to add the needed multiplication signs in order not to give error when passed to eval
    # e.g. 5(x) [gives error when passed to eval] --> 5*(x) [doesn't give an error when passed to eval]
    def __add_needed_multiplications(self):
        # we have to do this because in the end of the method we replace log10*( by log10( if they are mistakenly made
        # but what if that's what the user entered? It will be evaluated as a valid expression so we have to precheck for it
        if "log10*(" in self.__expression:
            return

        for i in range(0, len(self.__expression)-1):
            # if found a number or x or a closing bracket before an opening bracket, l which is part of log10, or
            # s which is part of sqrt(, that means they are multiplied by each other
            # so we will add multiplication operator between them to make it obvious for eval
            if (self.__expression[i] in "x)" or self.__is_digit(self.__expression[i])) and self.__expression[i+1] in "ls(" \
                    or self.__is_digit(self.__expression[i]) and self.__expression[i+1] == "x":
                self.__expression = self.__expression[:i+1] + "*" + self.__expression[i+1:]
        # the above process will replace every "10(" with "10*(". this can be a part of "log10(" and hence result in
        # invalid expression even if it's valid. so we have to replace it
        self.__expression = self.__expression.replace("log10*(", "log10(")




    # ------------------------------------------- Validation Methods -------------------------------------------
    # method that checks the division by zero
    def __check_division_by_zero(self):
        self.__expression = self.__expression.replace("(-0)", "0")              # this line will help detect division by zero
        self.__expression = self.__expression.replace("(0)", "0")
        return "/0" in self.__expression

    def __check_operator(self, letter):
        return letter in "+-*/^"

    # each expression can't contain any of these operators at the beginning, hence returning True "invalid expression"
    def __check_start(self):
        return self.__expression[0] in "*/^"

    # each expression can't end with any of these operators, hence returning True (if found)
    def __check_end(self):
        return self.__expression[-1] in "*/^-+"

    # checking if our expression has more two or more "x" next to each other, which is invalid e.g. xx (invalid)
    def __check_successive_x(self):
        for i in range(0, len(self.__expression) - 1):
            if self.__expression[i] == "x" and self.__expression[i+1] == "x":
                return True     # if there is at least one next Xs, then it's invalid
        return False            # will return false if there is no next Xs

    # some neighboring operators are forbidden and hence make the expression invalid
    # valid: "++", "--", "-+", "+-", "*+", "/+", "*-", and "/-"
    # invalid: "**", "//", "^^", and the rest
    def __check_successive_operators(self):
        index, end_point = 0, len(self.__expression) - 1
        while index < end_point:
            # if both of them operators, then we need to make sure this is a valid succession
            if self.__check_operator(self.__expression[index]) and self.__check_operator(self.__expression[index+1]):
                # if both operators are the same
                if self.__expression[index] == self.__expression[index+1]:
                    # if both are **, // or ^^, then we return False "invalid"
                    if self.__expression[index] in '*/^':
                        return False

                    # if both are ++, -- then we can reduce them to just +
                    elif self.__expression[index] == "+" or self.__expression[index] == "-":
                        self.__expression = self.__expression[:index] + "+" + self.__expression[index+2:]
                        end_point -= 1                      # two chars replaced by one char (-1 change)
                        index -= 1                          # starting from the same position again to check validity
                                                            # because the next char can be another operator

                # "-+" or "+-" --> "-"
                elif self.__expression[index] + self.__expression[index+1] == "+-" or \
                     self.__expression[index] + self.__expression[index+1] == "-+":
                    self.__expression = self.__expression[:index] + "-" + self.__expression[index+2:]
                    end_point -= 1
                    index -= 1

                # "*+" --> "*" and "/+" --> "/"
                elif self.__expression[index] + self.__expression[index+1] == "*+" or \
                        self.__expression[index] + self.__expression[index+1] == "/+":
                    self.__expression = self.__expression[:index+1] + self.__expression[index+2:]
                    end_point -= 1
                    index -= 1

                # "*-....." --> "*(-...)..." and "/-....." --> "/(-...)..."
                # if the expression is one of those then we need to enclose that expression that starts with -
                # e.g. 3*x^2*-log10(x)*4 --> 3*x^2*(-log10(x))*4
                elif self.__expression[index] + self.__expression[index+1] == "*-" or \
                        self.__expression[index] + self.__expression[index + 1] == "/-":
                    right_bracket_index = self.__find_right_bracket_index(index+2)
                    self.__expression = self.__expression[:index+1] + "(" + self.__expression[index+1:right_bracket_index+1] + ")" \
                    + self.__expression[right_bracket_index+1:]

                # other unaddressed expressions are invalid
                else:
                    return False

            index += 1

        return True                 # returning true if we finish processing all the characters successfully

    # method that checks if there is a number just after a closed parentheses and will return True if found (invalid)
    # e.g. (5)1 is invalid (5)x is also invalid because x in the end will be replaced by numbers and when this happens
    # it will be invalid so we have to treat it as a number
    def __digit_after_bracket(self):
        for i in range(0, len(self.__expression)-1):
            if self.__expression[i] == ")" and (self.__is_digit(self.__expression[i+1]) or self.__expression[i+1] == "x"):
                return True
        return False

    def __digit_after_x(self):
        for i in range(0, len(self.__expression) - 1):
            if self.__expression[i] == "x" and self.__is_digit(self.__expression[i + 1]):
                return True
        return False

    # a method that checks if the expression has balanced parentheses
    def __check_parentheses(self):
        stack = []
        for char in self.__expression:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        return len(stack) == 0

    # part of the checking the validity of our expression is to check if the functions we have in the expression
    # are one of our supported functions or expressions (log10 and sqrt in this case)
    def __check_function(self, start_index):
        # iterating over each expression of our supported expressions
        for exp in self.__valid_expressions:
            # if the initial letter of each expression match then there is a possibility that this expression is valid
            if self.__expression[start_index] == exp[0]:
                # checking if this expression is the same as our current expression (exp)
                if start_index + len(exp) - 1 < len(self.__expression):
                    if self.__expression[start_index: start_index + len(exp)] == exp:
                        return len(exp)
        return 0                 # invalid character or expression

    # a method to check if there are invalid characters ($, &, etc..) and invalid functions or
    # expressions (cos, sin, etc.)
    def __check_false_expressions(self):
        i, end_point = 0, len(self.__expression)

        while i < end_point:
            current_char = self.__expression[i]
            # x is a valid character
            if current_char == "x":
                i += 1
                continue

            # if the currently investigated character is not x then it might be an operator or a bracket (if not a digit)
            if not self.__is_digit(current_char):
                if current_char in "+-*/^()":
                    i += 1
                    continue

                # if none of the following, then it can be function (e.g. log10(x))
                characters_skipped = self.__check_function(i)
                # if it's a function then we have already checked some of the next characters so will directly jump to
                # the first unchecked char e.g. ----log10(x) here we started with l in log10(x) and if our checker method
                # recognizes this expression then it already checked og10( as well so we move directly to the inside of
                # our function which x in this case, if the inside expression is valid then the whhole function is also valid
                if characters_skipped:
                    i += characters_skipped

                # otherwise, it's a foreign character and we return True (invalid)
                else:
                    return True
            else:
                i += 1
        # if all the characters are familiar and valid, we return False (valid expression)
        return False

    # to have a valid expression, we need that we don't have empty parentheses
    def __check_empty_brackets(self):
        return "()" in self.__expression





    # ------------------------------------------- Validation Process -------------------------------------------
    # a method that does all the previously described checkers one after another
    def check_validity(self):
        # if the expression is a constant expression
        if self.__const_type != "None":
            # we have to check if the evaluated expression is () or not because eval successfully evaluates it
            if self.__check_empty_brackets():
                return "Expression Contains Empty Brackets"
            else:
                self.__valid = True
                return "Valid Expression"

        if self.__check_start():
            return "Invalid Operators at The Beginning"

        if self.__check_end():
            return "Invalid Operators at The End"

        if not self.__check_parentheses():
            return "Brackets Are NOT Balanced"

        if self.__check_empty_brackets():
            return "Expression Contains Empty Brackets"

        if self.__digit_after_bracket():
            return "Digits After Brackets Without Operators"

        if self.__digit_after_x():
            return "Digits After X Without Operators"

        if self.__check_successive_x():
            return "Two or More X variable Next to Each Other"

        if not self.__check_successive_operators():
            return "Invalid Successive Operators"

        if self.__check_division_by_zero():
            return "Cannot Divide by Zero"

        if self.__check_false_expressions():
            return "Invalid Characters Entered"

        self.__valid = True                      # our expression is valid if we none of the above methods return something
        return "Valid Expression"





    # ------------------------------------------- Calculation Method -------------------------------------------
    # a function that uses numpy to evaluate our valid expression
    def __alternative_eval(self, x):
        # replacing ^ with ** because that's how eval recognizes the power in python
        # replacing sqrt with np.sqrt (as text) and log10 with np.log10 (as text)
        expression = self.__expression.replace('^', '**').replace('sqrt', 'np.sqrt').replace('log10', 'np.log10')

        # calculating the value of our function at x (some value or array)
        try:
            return eval(expression, {"__builtins__": None, "x": x, "math": math, "np": np})
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")





    # ------------------------------------------- Plotting Method -------------------------------------------
    def plot_function(self, ax):
        # in case it's a y = a expression that means that all the 400 y values accross the whole domain will be "self.constant"
        if self.__const_type == "y":
            x_vals = np.linspace(self.__min_x, self.__max_x, 400)
            y_vals = np.array([self.__constant] * 400)

        # in case it's an x = a expression that means that all the 400 x values will be (self.constant)
        # and will choose an arbitrary y range [-10, 10] because the user doesn't have the option to enter them
        elif self.__const_type == "x":
            x_vals = np.array([self.__constant] * 400)
            y_vals = np.linspace(-10, 10, 400)
        # otherwise, it's a valid non-constant expression and will be plotted as usual
        else:
            x_vals = np.linspace(self.__min_x, self.__max_x, 400)
            y_vals = self.__alternative_eval(x_vals)

        ax.plot(x_vals, y_vals)
        ax.set_title("Function's Graph")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")




# ------------------------------------------- GUI Class -------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        # inheriting all other processes from the parent class (QMainWindow)
        super().__init__()

        # setting the title of the window
        self.setWindowTitle("Function Plotter")
        # Set the geometry (top_left_x, top_left_y, window size) of the window
        self.setGeometry(100, 100, 1000, 800)

        # creating a vertical layout to arrange widgets in a vertical order
        layout = QVBoxLayout()

        # creating an input field for the mathematical expression
        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("Enter function of x (e.g., 5*x^3 + 2*x)")  # the text inside it if it's empty
        layout.addWidget(self.expression_input)                 # adding it to our layout

        # creating a horizontal layout for min and max x values input fields to be next to each other in the same line
        min_max_layout = QHBoxLayout()
        self.min_x_input = QLineEdit()
        self.min_x_input.setPlaceholderText("Enter min value of x")
        self.max_x_input = QLineEdit()
        self.max_x_input.setPlaceholderText("Enter max value of x")
        # adding the input fields to the horizontal layout
        min_max_layout.addWidget(self.min_x_input)
        min_max_layout.addWidget(self.max_x_input)
        # adding the horizontal layout
        layout.addLayout(min_max_layout)

        # creating a button to trigger the plotting of the function
        self.plot_button = QPushButton("Plot Function")
        # connecting the button's click event to the plot_function method so that it starts graphing once it's clicked
        self.plot_button.clicked.connect(self.__plot_function)
        # adding the button to the vertical layout
        layout.addWidget(self.plot_button)

        # creating a label to display messages
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignCenter)  # centering the text in the label
        # adjusting the font of the label
        font = QFont("Arial", 14, QFont.Bold)
        self.message_label.setFont(font)
        # applying text color and style for the label
        self.message_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.message_label)

        # create a matplotlib figure and canvas for plotting
        self.figure = plt.figure()                  # figure
        self.canvas = FigureCanvas(self.figure)     # canvas

        # setting the canvas size policy to expand with the window size
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # setting a minimum height for the canvas to ensure it is always visible
        self.canvas.setMinimumHeight(400)
        layout.addWidget(self.canvas)               # adding the canvas to the layout

        # creating a container widget to hold the layout
        container = QWidget()
        container.setLayout(layout)
        # setting the container as the central widget of the window
        self.setCentralWidget(container)

    def __plot_function(self):
        # getting the mathematical expression from the input field
        expression = self.expression_input.text()
        if not expression:
            # displaying a message if the expression input is empty
            self.message_label.setText("Please Enter an Expression")
            return

        try:
            # getting and convert min and max x values to floats
            min_x = float(self.min_x_input.text())
            max_x = float(self.max_x_input.text())
        except ValueError:
            # displaying a message if min or max x values are not valid numbers
            self.message_label.setText("Min and Max Values Must Be Valid Numbers.")
            return

        # checking if min_x is less than max_x
        if min_x >= max_x:
            self.message_label.setText("Min Value Must Be Less Than Max Value.")
            return

        # creating a FunctionPlotter instance with the provided expression and x values
        plotter = FunctionPlotter(expression, min_x, max_x)
        # checking the validity of the expression
        validity_message = plotter.check_validity()
        if plotter.is_valid():
            # clearing the previous plot in order to prevent multiple graphs being displayed above each other
            self.figure.clear()
            # adding a new subplot for the function plot
            ax = self.figure.add_subplot(111)
            # plotting the function on the new subplot
            plotter.plot_function(ax)
            # redrawing the canvas to show the updated plot
            self.canvas.draw()
            # displaying a success message
            self.message_label.setText("Function plotted successfully.")
        else:
            # displaying an error message if the expression is invalid
            self.message_label.setText(f"Invalid Expression: {validity_message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())