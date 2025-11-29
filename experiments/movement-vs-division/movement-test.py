# --- Parameters ---
k = 1.0                 # invariant ratio E/C at birth
C_move_base = 1.0       # base movement cost
C_division = 1.0        # cost of a division act
alpha = 0.8             # forward child movement cost multiplier
beta = 1.1              # lateral child movement cost multiplier
lambda_viscosity = 0.0  # time viscosity factor (0 = disabled)
ticks_to_divide = 26    # how many ticks to accumulate before division
N_children = 26         # target number of children

# --- Accumulate energy over ticks ---
E_birth = k * C_move_base
E = E_birth
for t in range(1, ticks_to_divide + 1):
    # accumulate 1 energy per tick deterministically
    E += 1
    # optional: increase movement cost with time
    C_move_base_t = C_move_base * (1 + lambda_viscosity * t)

# --- Division step ---
children = []
for i in range(N_children):
    if i == 0:
        # forward child inherits lower cost
        C_move_child = alpha * C_move_base
    else:
        # lateral children have higher cost
        C_move_child = beta * C_move_base
    E_child = k * C_move_child
    children.append({"id": i, "C_move": C_move_child, "E_birth": E_child})

# --- Energy accounting ---
E_used = sum(c["E_birth"] for c in children) + C_division
E_parent_after = E - E_used

# --- Results ---
print("Energy before division:", E)
print("Energy used for children + division:", E_used)
print("Energy remaining for parent:", E_parent_after)
print("Children summary:")
for c in children:
    print(c)
