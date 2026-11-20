# Week 6: Debugging and common errors

Error messages are information, not judgement. Read the last line first: it names the error type and describes the problem. The lines above it (the traceback) show which line of your file was running.

## Common error types

- **SyntaxError**: Python cannot read the code. Look for a missing colon, an unclosed bracket or quote, or `=` used where `==` was meant. The real mistake is often on the line before the one reported.
- **NameError**: a name is not defined. Check spelling and capitalisation, and make sure the variable was assigned before this line runs.
- **TypeError**: an operation got the wrong type, such as adding a string and an int (`"Age: " + 18`). Convert with `str()` or `int()`.
- **IndexError**: a list position does not exist. See the Week 4 notes on indexing.
- **ZeroDivisionError**: dividing by zero, often when averaging an empty list.

## A debugging strategy

1. Read the whole error message, especially the last line.
2. Predict what the variables should contain at the failing line.
3. Add a `print()` to check what they actually contain.
4. Change one thing at a time, then run again.

Resubmitting quickly with random changes usually takes longer than reading the error. Slowing down to form a hypothesis is the fastest way to fix a bug.
