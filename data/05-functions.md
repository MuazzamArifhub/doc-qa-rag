# Week 5: Functions

A function is a named block of code you can reuse. Define it with `def`:

```python
def average(numbers):
    return sum(numbers) / len(numbers)
```

`numbers` is a parameter: a name for the value passed in. When you call `average([70, 80])`, the argument `[70, 80]` is assigned to `numbers`.

## Return vs print

`return` sends a value back to the code that called the function, so it can be stored or used: `result = average(scores)`. `print` only shows text on the screen. A function without a `return` statement returns `None`, which is a common source of `TypeError` when the result is used in arithmetic later.

## Scope

Variables created inside a function exist only inside it. Using such a variable outside the function gives a `NameError`. Pass values in as parameters and send results out with `return` instead of relying on global variables.

## Why use functions

Functions break a problem into smaller pieces, avoid repeated code and make testing easier, because you can check each function on its own.
