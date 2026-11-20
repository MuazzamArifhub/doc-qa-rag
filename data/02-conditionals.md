# Week 2: Conditionals

An `if` statement runs a block of code only when a condition is true:

```python
if score >= 50:
    print("Pass")
elif score >= 45:
    print("Supplemental exam")
else:
    print("Fail")
```

Python checks the conditions from top to bottom and runs the first block whose condition is true. `elif` means "else if". The `else` block runs when no condition was true.

## Comparison and logic operators

- `==` tests equality. A single `=` is assignment, and using it inside an `if` is a SyntaxError.
- `!=` means not equal; `<`, `>`, `<=`, `>=` compare values.
- `and`, `or` and `not` combine conditions: `if age >= 18 and has_id:`.

## Indentation

The code inside an `if` block must be indented, usually by four spaces. Mixing tabs and spaces, or forgetting to indent, causes an `IndentationError`. The colon at the end of the `if` line is required.
