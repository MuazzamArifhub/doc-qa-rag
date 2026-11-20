# Week 4: Lists and indexing

A list holds several values in order: `scores = [72, 88, 95]`. Lists can grow and change.

## Indexing

Each item has a position called an index. Indexing starts at 0, not 1, so `scores[0]` is `72` and `scores[2]` is `95`. Negative indexes count from the end: `scores[-1]` is the last item.

## IndexError: list index out of range

An `IndexError` means you asked for a position that does not exist. A list with 3 items has valid indexes 0, 1 and 2, so `scores[3]` fails. This often happens in loops written as `for i in range(len(scores) + 1)`, or when you forget that indexing starts at 0. To fix it, print `len(your_list)` and the index you are using just before the line that fails.

## Useful list operations

- `scores.append(80)` adds an item to the end.
- `len(scores)` gives the number of items.
- `scores[1:3]` is a slice: items at index 1 and 2.
- `for s in scores:` loops over the items directly, which avoids most index mistakes.
- `sum(scores) / len(scores)` computes the average.
