"""PyWENO discontinuous reconstruction example."""

import math
import numpy
import pyweno.grid
import pyweno.weno

# explicitly define the function f that we will reconstruct ...
def f(x):
    if x < 0.0:
        return math.sin(x)

    return math.cos(x)

uf = numpy.frompyfunc(f, 1, 1)

def fp(x):
    if x < 0.0:
        return math.cos(x)

    return -math.sin(x)

ufp = numpy.frompyfunc(fp, 1, 1)

# load the weno reconstructor from the cache
k = 4
x = numpy.linspace(-4.0, 4.0, 21)

grid = pyweno.grid.Grid(x)
weno = pyweno.weno.WENO(order=k, grid=grid)

weno.precompute_reconstruction('left')
weno.precompute_reconstruction('right')
weno.precompute_reconstruction('dd|left')
weno.precompute_reconstruction('d|gauss_quad3')
weno.precompute_reconstruction('d|left')

#weno.w['d|left'] = numpy.ones(weno.w['d|left'].shape) / 3.0

# average f
f_avg = grid.average(f)

# allocate arrays for reconstruction
f_left = numpy.zeros(grid.N)
f_right = numpy.zeros(grid.N)
f_left_x = numpy.zeros(grid.N)
f_left_xx = numpy.zeros(grid.N)
f_gauss_x = numpy.zeros((grid.N,3))

# compute smoothness indicators
weno.smoothness(f_avg)

# reconstruct!
weno.reconstruct(f_avg, 'left', f_left)
weno.reconstruct(f_avg, 'right', f_right)
weno.reconstruct(f_avg, 'd|left', f_left_x)
weno.reconstruct(f_avg, 'dd|left', f_left_xx)
weno.reconstruct(f_avg, 'd|gauss_quad3', f_gauss_x)

# plot results
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

gauss_points = numpy.array([ -math.sqrt(3.0/5.0), 0.0, math.sqrt(3.0/5.0) ])
def quad3_points(a, b):
    w = (b-a)/2.0
    c = (a+b)/2.0

    return w * gauss_points + c


plt.subplot(2,1,1)

x = numpy.linspace(-4.0, 4.0, 1001);
uf = numpy.frompyfunc(f, 1, 1)
plt.plot(x, uf(x), '-k')

xq = numpy.zeros((grid.N,3))
for i in xrange(grid.N):
    for l, xi in enumerate(quad3_points(grid.x[i], grid.x[i+1])):
        xq[i,l] = xi

plt.plot(grid.x[:-1], f_left, 'or')
plt.plot(grid.x[1:], f_right, 'ob')
plt.plot(grid.x[:-1], f_left_x, 'xk')
plt.plot(grid.x[:-1], f_left_xx, '+k')
plt.plot(xq.flatten(), f_gauss_x.flatten(), '.k')

plt.title('PyWENO reconstruction and smoothness indicators')
plt.ylabel('f')
plt.xlabel('x')
#plt.legend(['actual', 'left', 'right', 'left_x', 'left_xx'])

plt.subplot(2,1,2)

plt.plot(grid.centres(), weno.sigma[:,0], '.r')
plt.plot(grid.centres(), weno.sigma[:,1], '.b')
plt.plot(grid.centres(), weno.sigma[:,2], '.k')
plt.plot(grid.centres(), weno.sigma[:,3], '.m')

plt.ylabel('sigma')
plt.xlabel('x')
plt.legend(['r=0', 'r=1', 'r=2', 'r=3'])

plt.savefig('discontinuous.png', format='png')

