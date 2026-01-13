# Python Style: When to Use (and Not Use) Functional Patterns

## What We Learned

This experiment briefly explored forcing functional/stream patterns in Python, then **reverted back to idiomatic Python** with simple loops. Here's what we learned about Python performance and style.

---

## ✅ Keep These (Good Python)

### 1. Generators for Lazy Iteration

**Good:**
```python
class EntityNode:
    def stream(self) -> Iterator[Entity]:
        """Stream entities from linked list as generator."""
        current = self
        while current:
            yield current.entity
            current = current.next

# Usage:
for entity in node.stream():
    process(entity)
```

**Why:** Generators are memory-efficient and provide clean abstraction over linked list traversal.

---

### 2. List Comprehensions (When Clear)

**Good:**
```python
# Clear transformation
visible_items = [item for item in items if item.visible]
```

**Avoid:**
```python
# Too complex, use loop instead
complex_data = [
    (x, y, z, compute(x, y), transform(z))
    for x in range(a)
    for y in range(b)
    for z in nested[x][y]
    if predicate(x, y, z)
]
```

**Rule:** If comprehension is > 2 lines or hard to read, use a loop.

---

### 3. Built-in Functions (map, filter, zip)

**Good:**
```python
# When natural and clear
colors = list(map(entity_to_color, entities))
active = list(filter(lambda e: e.active, entities))
pairs = list(zip(entities, positions))
```

**Bad:**
```python
# Side effects in map/filter
tuple(map(draw_entity, entities))  # Creating tuple just to discard!
```

**Rule:** Use `map`/`filter` for **pure transformations**, not side effects.

---

### 4. itertools for Specific Use Cases

**Good:**
```python
from itertools import chain

# Flatten nested iterables
all_entities = chain.from_iterable(
    node.stream() if node else []
    for node in buckets
)
```

**When:** Chaining, grouping, zipping with specific patterns. But prefer simple loops if clarity suffers.

---

## ❌ Avoid These (Bad Python)

### 1. reduce() for Side Effects

**Bad:**
```python
from functools import reduce

reduce(
    lambda _, entity: self.buffer[lag].__setitem__(entity.temporal_lag, entity),
    entities,
    None
)
```

**Good:**
```python
for entity in entities:
    lag = entity.temporal_lag
    self.buffer[lag][self.head] = EntityNode(entity, next=self.buffer[lag][self.head])
```

**Why:** `reduce` is for **accumulation**, not side effects. Loops are clearer and faster.

---

### 2. tuple(map(...)) for Side Effects

**Bad:**
```python
# Creating tuple just to execute side effects
tuple(map(render_cell, visible_cells))
```

**Good:**
```python
for cell in visible_cells:
    render_cell(cell)
```

**Why:** Python is not lazy like Haskell. `map` returns an iterator that needs forcing. Using `tuple()` to force evaluation is wasteful.

---

### 3. Overly Nested Comprehensions

**Bad:**
```python
entity_stream = (
    (offset, lag, entity, 1.0 - offset / max_trail)
    for offset, frame in valid_frames
    for lag in reversed(range(len(frame)))
    for entity in (frame[lag].stream() if frame[lag] else [])
)
```

**Good:**
```python
for trail_offset in range(max_trail):
    frame = sliding_window.get_frame(base_offset + trail_offset)
    if not frame:
        break

    fade = 1.0 - (trail_offset / max_trail)

    for lag in reversed(range(len(frame))):
        node = frame[lag]
        if node:
            for entity in node.stream():
                render_entity(entity, lag, fade=fade)
```

**Why:** Readability matters more than cleverness. Nested loops are easier to debug and understand.

---

### 4. Forcing Functional Style Everywhere

**Bad Philosophy:**
> "Let's make everything functional with map/reduce/generators!"

**Good Philosophy:**
> "Use the right tool for the job. Loops are often clearest."

---

## Performance Reality in Python

### CPython Loop Performance

**Simple for loops are FAST in Python:**
```python
# ~Fast (CPython optimized)
for item in items:
    process(item)

# ~Same speed or slower
list(map(process, items))

# Slower (function call overhead)
from functools import reduce
reduce(lambda acc, item: process(item), items, None)
```

**Why:**
- `for` loops are implemented in C in CPython
- Function calls (lambda, map, reduce) add overhead
- Python isn't lazy by default (not Haskell!)

---

### When Functional Patterns Win

**1. Avoiding Intermediate Lists**

```python
# Bad: creates 3 intermediate lists
filtered = [x for x in items if predicate(x)]
transformed = [transform(x) for x in filtered]
result = [finalize(x) for x in transformed]

# Good: single pass with generator
result = list(finalize(transform(x)) for x in items if predicate(x))
```

**2. Composable Pipelines**

```python
# Good: clear data flow
from itertools import chain, islice

pipeline = (
    chain.from_iterable(buckets),      # Flatten
    filter(is_visible, entities),       # Filter
    map(apply_transform, entities),     # Transform
    islice(entities, 100)               # Limit
)

for entity in pipeline:
    render(entity)
```

**When:** Building reusable transformation pipelines. But only if clearer than loops!

---

## Idiomatic Python Style

### The Zen of Python (PEP 20)

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Flat is better than nested.
Readability counts.
```

**Applied to our code:**

✅ **Simple loops** are explicit and readable
✅ **Generators** for linked lists are clean abstraction
✅ **List comprehensions** for simple transformations
❌ **Forced functional patterns** sacrifice readability

---

## Final Code Style

### Entity Iteration (Good)

```python
# Using generator from linked list
for entity in node.stream():
    self.draw_entity(entity, lag)
```

### Entity Collection (Good)

```python
# Clean extraction with generator + extend
entities = []
for lag in range(self.max_history):
    node = self.buffer[lag][index]
    if node:
        entities.extend(node.stream())
return entities
```

### Bucketing (Good)

```python
# Clear loop with prepending
for entity in entities:
    lag = entity.temporal_lag
    self.buffer[lag][self.head] = EntityNode(entity, next=self.buffer[lag][self.head])
```

### Rendering (Good)

```python
# Nested loops are clear
for trail_offset in range(max_trail):
    frame = sliding_window.get_frame(base_offset + trail_offset)
    if not frame:
        break

    fade = 1.0 - (trail_offset / max_trail)

    for lag in reversed(range(len(frame))):
        node = frame[lag]
        if node:
            for entity in node.stream():
                self.draw_entity(entity, lag, alpha=alpha, scale=fade)
```

---

## Lessons Learned

### 1. **Python is Not Haskell**
Functional patterns in Haskell are optimized by the compiler. In Python, they often add overhead.

### 2. **Loops are NOT Evil**
Simple `for` loops are Pythonic, fast, and readable. Don't be afraid to use them!

### 3. **Generators are Your Friend**
Lazy iteration with `yield` is powerful. Use for:
- Traversing data structures (linked lists, trees)
- Large datasets that don't fit in memory
- Pipeline transformations

### 4. **Comprehensions Have Limits**
List/dict/set comprehensions are great for simple cases. When they get complex (nested, multi-line), use loops.

### 5. **Side Effects Belong in Loops**
Don't force `map`/`reduce` for operations with side effects (rendering, mutation, I/O). Use loops.

---

## Recommended Reading

- **PEP 8:** Python style guide
- **PEP 20:** The Zen of Python
- **Effective Python** by Brett Slatkin (Item 27: Prefer map/filter over comprehensions for simple cases)
- **Fluent Python** by Luciano Ramalho (Chapter 5: Generators)

---

## TL;DR

**What we did:**
1. ❌ Forced functional patterns (map, reduce, nested comprehensions)
2. ❌ Sacrificed readability for "cleverness"
3. ✅ Reverted to idiomatic Python with simple loops
4. ✅ Kept useful abstractions (generators for linked lists)

**What we learned:**
- Python is not a functional language at heart
- Simple loops are fast, clear, and Pythonic
- Use functional patterns where they add clarity, not everywhere
- Readability > cleverness

**Final style:**
- ✅ Simple `for` loops for iteration with side effects
- ✅ Generators for lazy iteration (linked lists, data structures)
- ✅ List comprehensions for simple transformations
- ✅ `chain.from_iterable` for flattening when clear
- ❌ No `reduce` for side effects
- ❌ No `tuple(map(...))` for forcing evaluation
- ❌ No overly nested comprehensions

**Bottom line:** Write Python like Python, not like Haskell.

---

**Last Updated:** 2026-01-13
**Status:** Style guide complete - idiomatic Python restored
