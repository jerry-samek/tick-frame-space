# **📐 1. Coordinate System: Axial Hex Coordinates**

Use **axial coordinates**:

```
(q, r)
```

Each hex cell is identified by a pair of integers.

There is an implicit third coordinate:

```
s = -q - r
```

…but you never need to store it.

---

# **🧭 2. Direction Vectors (6 neighbors)**

Define the 6 canonical directions:

| dir | dq | dr | angle |
|-----|----|----|--------|
| 0 | +1 |  0 |   0° |
| 1 | +1 | -1 |  60° |
| 2 |  0 | -1 | 120° |
| 3 | -1 |  0 | 180° |
| 4 | -1 | +1 | 240° |
| 5 |  0 | +1 | 300° |

Movement is simply:

```
(q, r) ← (q + dq[dir], r + dr[dir])
```

This is the hex equivalent of your current `(x+dx, y+dy)`.

---

# **🔄 3. Chirality (rotation)**

Chirality becomes **rotation in direction index space**.

Clockwise:

```
dir = (dir + 1) % 6
```

Counterclockwise:

```
dir = (dir + 5) % 6
```

This is clean, stable, and perfectly symmetric.

---

# **📏 4. Distance (hex radius)**

Hex distance between two cells:

```
dq = q1 - q2
dr = r1 - r2
ds = -dq - dr

dist = max(|dq|, |dr|, |ds|)
```

This gives you **perfect circles** in hex space.

---

# **📉 5. Gamma Field (gradient estimation)**

For each cell:

1. Sample the 6 neighbors’ heights:  
   `h0, h1, h2, h3, h4, h5`

2. Compute differences relative to center height `hc`:

```
d[i] = h[i] - hc
```

3. Choose gamma direction:

### Option A — steepest descent (simple, stable)
```
dir = argmin(d[i])
```

### Option B — weighted vector sum (smooth)
```
gamma = Σ ( -d[i] * direction_vector[i] )
dir = direction_of(gamma)
```

Both work beautifully.

---

# **🧠 6. Navigation Rule (entity movement)**

Each tick:

1. Entity reads gamma direction at its current cell.
2. Entity optionally rotates based on chirality/memory.
3. Entity moves one step in its current direction.

Pseudocode:

```
gamma_dir = compute_gamma(q, r)
dir = blend(dir, gamma_dir, memory, chirality)
(q, r) += direction[dir]
```

This is the cleanest formulation of your current behavior.

---

# **🌀 7. Imprinting (optional but natural)**

Each cell stores an imprint value:

```
imprint[q][r] += f(entity_state)
```

Or directional imprint:

```
imprint[q][r][dir] += f(...)
```

Hex grids make directional imprinting trivial because directions are discrete and symmetric.

---

# **🎨 8. Rendering (if needed)**

To map axial coords to screen (pointy‑top hexes):

```
x = size * (sqrt(3) * q + sqrt(3)/2 * r)
y = size * (3/2 * r)
```

This is purely visual — the simulation stays in axial space.

---

# **🌟 Summary: Your 2D Hex Grid Specification**

### **Coordinates**
- Axial `(q, r)`

### **Neighbors**
- 6 directions with fixed vectors

### **Movement**
- Add direction vector to position

### **Chirality**
- Rotate direction index mod 6

### **Distance**
- `max(|dq|, |dr|, |ds|)`

### **Gamma**
- Compute from 6 neighbors
- Choose steepest descent or weighted sum

### **Navigation**
- Blend gamma + chirality + memory
- Move one hex per tick

### **Imprinting**
- Store scalar or directional values per hex

This is the cleanest, most symmetric, most physically honest 2D geometry you can use.
