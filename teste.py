import matplotlib.pyplot as plt
from sympy import symbols, Eq
from sympy.plotting import plot

# Define symbols
x, y = symbols('x y')

# Define equations
equation1 = Eq(x*2 + y*2, 1)
equation2 = Eq(x - y, 1)

# Create a plot
fig, ax = plt.subplots()
ax.text(0.1, 0.8, f'Equation 1: ${equation1}$', fontsize=12)
ax.text(0.1, 0.6, f'Equation 2: ${equation2}$', fontsize=12)

# Hide axes
ax.axis('off')

# Display plot
plt.show()