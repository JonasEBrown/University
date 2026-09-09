'''
Python script for MTH2005, practical 2
'''

# import some necessary libraries for this practical
import numpy as np
import matplotlib.pyplot as plt


def rhs(x, rhs_coeff):
    '''
    Function to return the RHS of the ODE
    '''
    return rhs_coeff * x


# Switch to 'exp' or 'osc' for exponential decay or oscillation cases
case = 'exp'

n_tot = 100 # number of time steps

x_fe = np.zeros(n_tot, dtype=np.complex128) # Array for FE solution (note setting as complex numbers)
x_lf = np.zeros(n_tot, dtype=np.complex128) # Array for LF solution

x_ie = np.zeros(n_tot, dtype=np.complex128) # Array for IE solution

dt = 0.1 # time step
time = np.arange(0,n_tot,1)*dt # time array

# Initial values of x
x_fe[0] = 1 + 0j
x_lf[0] = 1 + 0j

# I-E
x_ie[0] = 1 + 0j

# Set RHS of function depending on the case chosen

if case == 'exp':
    print('Exponential decay case')
    lamb = 4
    rhs_coeff = -lamb

elif case == 'osc':
    print('Oscillation case')
    omega = 11
    rhs_coeff = complex(0, omega)

else:
    print('Wrong value for case')

# Forward Euler solution
for n in range(0,n_tot-1):
    x_fe[n+1] = x_fe[n] + rhs(x_fe[n], rhs_coeff)*dt

# Leapfrog solution. Set first value using FE step   
x_lf[1] = x_fe[1]  
for n in range(1, n_tot-1):
    x_lf[n+1] = x_lf[n-1] + 2*rhs(x_lf[n], rhs_coeff)*dt

#################################
## ADD THE IMPLICIT-EULER CASE ##
#################################

for n in range(0,n_tot-1):
    x_ie[n+1] = x_ie[n] / (1 - rhs_coeff*dt)

# Plot the results
plt.plot(time, np.real(x_fe), label='FE')
plt.plot(time, np.real(x_lf), label='LF')
plt.plot(time, np.real(x_ie), label='IE') # Plot IE.
if case == 'exp':
    plt.ylim(-2,2)
    plt.plot(time, np.exp(-lamb*time), color='k', label='$x*$')
elif case == 'osc':
    plt.ylim(-12,12)
    plt.plot(time, np.cos(omega*time), color='k', label='$x*$')
plt.xlim(0,4)
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.show()
    
    
