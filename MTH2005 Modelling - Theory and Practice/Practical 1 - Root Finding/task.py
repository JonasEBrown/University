'''
Python script for MTH2005, practical 1
'''

def f(x):
    '''
    Defines the function f(x) used in the practical
    '''
    return (x**3) - (2 * x**2) - 3 # GAP1 implement function f(x) given in tutorial sheet

a = 2 # GAP2 left hand limit
b = 4 # GAP3 right hand limit
err = 1e-3 # desired accuracy of root
n=0 # counter of number of steps
interval_width = b-a

# Check that root exists in chosen interval using IVT
if f(a) * f(b) > 0: # GAP4
    print('Cannot detect a root')

else:
    while interval_width/2 > err:
        c = (a + b) / 2 # GAP5 let c equal the mid point of the interval

        print (f'n = {n}, interval_with = {interval_width}, c = {c}')  
        
        if f(a) * f(c) < 0: # GAP6 IVT test on [a,c], success --> root in [a,c]
            b=c
        else:
            a=c

        interval_width = b-a
        n += 1

        

        
