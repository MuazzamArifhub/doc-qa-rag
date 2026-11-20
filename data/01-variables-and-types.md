# Week 1: Variables and types

A variable is a name that refers to a value. You create one with assignment: `count = 3`. The name goes on the left of the equals sign and the value on the right. Assignment does not mean "equals" in the maths sense; it means "make this name refer to this value".

Python has several basic types:

- `int` for whole numbers, such as `42`
- `float` for decimal numbers, such as `3.14`
- `str` for text, written in quotes, such as `"hello"`
- `bool` for truth values, `True` or `False`

Use `type(x)` to check the type of a value. Types matter because operations depend on them. `3 + 4` gives `7`, but `"3" + "4"` gives `"34"`, because adding two strings joins them.

## Converting between types

`input()` always returns a string, even when the user types a number. Convert it before doing arithmetic: `age = int(input("Age: "))`. Use `float()` for decimals and `str()` to turn a number into text.

## Naming rules

Variable names can contain letters, digits and underscores, but cannot start with a digit. Names are case-sensitive, so `Total` and `total` are different variables. Choose descriptive names such as `average_score` rather than `x`.
