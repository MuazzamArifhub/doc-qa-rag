# Week 3: Loops

A `for` loop repeats code once for each item in a sequence:

```python
for name in ["Ana", "Ben", "Chen"]:
    print("Hello", name)
```

`range(n)` produces the numbers 0 to n - 1, so `for i in range(5):` runs five times with `i` equal to 0, 1, 2, 3 and 4. `range(1, 6)` starts at 1 and stops before 6.

## While loops

A `while` loop repeats as long as its condition stays true:

```python
guess = ""
while guess != "yes":
    guess = input("Done? ")
```

If the condition never becomes false, the loop runs forever. This is called an infinite loop. Press Ctrl+C to stop a program stuck in one, then check that something inside the loop changes the condition.

## Break and continue

`break` leaves the loop immediately. `continue` skips the rest of the current pass and moves on to the next item.

## Off-by-one errors

A common bug is looping one time too many or too few. If you need the numbers 1 to 10, use `range(1, 11)`, because the stop value is not included.
