#!/usr/bin/env python
# --*-- coding:UTF-8 --*--
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from scipy.optimize import leastsq
from lmfit import minimize, Parameters, Parameter, report_fit
#
'''
文件格式说明
直接使用粒度软件导出的文本文件
eg:
        0.1	0.10964782	0.12022644	0.13182567	0.14454398	0.15848932	0.17378008 ......
PL-2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0.032365	0.094076 ......
.
.
.
'''
#get the x y values from data file
path = '/home/jiabo/google_drive/硕士资料/普鲁/粒度2/'  #文件路径
sample = '分粒级'          #文件名

l = []
with open(path + sample) as dat:
    data = dat.readlines()
    for lines in data:
        var = lines.split()
        l.append(var)
print l[2][0]
smaplenum = str(l[1][0])                    #样品号
x = np.array(l[0], dtype=np.float64)        #粒级
y = np.array(l[2][1:101], dtype=np.float64) #含量
y_df = np.gradient(y)
y_df2 = np.gradient(y_df)

#
#func and residuals is used for scipy leatsq results
def func(x_fit, para):
#    print para
    p, p1, p2, a, a1, a2, b, b1, b2 = para
   # print p, a, b
    y = p * (a / b) * x_fit ** (a - 1) * np.exp(-((x_fit / b) ** a))
    y1 = p1 * (a1 / b1) * x_fit ** (a1 - 1) * np.exp(-((x_fit / b1) ** a1))
    y2= p2 * (a2 / b2) * x_fit ** (a2 - 1) * np.exp(-((x_fit / b2) ** a2))
    return y + y1 + y2  #   #

def residuals(para, x_fit, y_interp):
    return y_interp - func(x_fit, para)

#
#myfunc and myresiduals are used for lmfit with parameter aranges
def myfunc(x_fit, params):
    #p, p1, p2, a, a1, a2, b, b1, b2 = para\
    p = params['p'].value
    p1= params['p1'].value
    p2= params['p2'].value
    a= params['a'].value
    a1= params['a1'].value
    a2= params['a2'].value
    b= params['b'].value
    b1= params['b1'].value
    b2= params['b2'].value
    y = p * (a / b) * x_fit ** (a - 1) * np.exp(-((x_fit / b) ** a))
    y1 = p1 * (a1 / b1) * x_fit ** (a1 - 1) * np.exp(-((x_fit / b1) ** a1))
    y2 = p2 * (a2 / b2) * x_fit ** (a2 - 1) * np.exp(-((x_fit / b2) ** a2))
    return y + y1 + y2

def myresiduals(params, x_fit, y_interp):
    return y_interp - myfunc(x_fit, params)

#
#single is for single endmember result
def single(x_fit, para):
    p, a, b = para
    return p * (a / b) * x_fit ** (a - 1) * np.exp(-((x_fit / b) ** a))


#set x value and y value, using line space rather than log space
x_fit = np.linspace(0.2, x.max(), 1000)
y_t = interpolate.splrep(x, y)
y_interp = interpolate.splev(x_fit, y_t)

#set initial value for least square caculating
para = [1., 1, 1, 1., 1, 1, 7., 7, 7]
plsqr = leastsq(residuals, para, args=(x_fit, y_interp), maxfev=10000)
plsq = plsqr[0]   #this is the result of the first value of initial value from scipy leastsq
'''
#plsq = ([5.65411684e-08,  1.01406847e-07,   7.23604702e-09,
#        2.86515301e+00,   3.16429461e+00,   2.61233488e+00,
#       7.03543809e-02,   4.35863370e-02,   1.20080759e-01])
para1 = [plsq[0], plsq[3], plsq[6]]
para2 = [plsq[1], plsq[4], plsq[7]]
para3 = [plsq[2], plsq[5], plsq[8]]
print para
'''
#
#give the value from scipy leastsq to second leastsq(lmfit) and set the arrange
params = Parameters()
params.add('p', value=abs(plsq[0]), min=10**-10)
params.add('p1', value=abs(plsq[1]), min=10**-10)
params.add('p2', value=abs(plsq[2]), min=10**-10)
params.add('a', value=abs(plsq[3]), min=10**-1)
params.add('a1', value=abs(plsq[4]), min=10**-1)
params.add('a2', value=abs(plsq[5]), min=10**-1)
params.add('b', value=abs(plsq[6]), min=10**-10)
params.add('b1', value=abs(plsq[7]), min=10**-10)
params.add('b2', value=abs(plsq[8]), min=10**-10)
#
#using lmfit to get the final result without negtive values
result = minimize(myresiduals, params, args=(x_fit, y_interp))
final = y_interp +result.residual
report_fit(result.params)
#
#get the parameters for each endmembers
para1 = [result.params['p'].value, result.params['a'].value, result.params['b'].value]
para2 = [result.params['p1'].value, result.params['a1'].value, result.params['b1'].value]
para3 = [result.params['p2'].value, result.params['a2'].value, result.params['b2'].value]
#
#start to draw the figs
fig = plt.figure(figsize=(20, 10), dpi=50, facecolor='white')
ax = fig.add_subplot(121)
ax.plot(x, y)
ax.plot(x, y_df)
ax.plot(x, y_df2)
ax.set_xscale('log')
ax.set_xlim(0.1, 1000)
ax1 = fig.add_subplot(122)
ax1.scatter(x, y, c='red')
ax1.plot(x_fit, y_interp)
ax1.plot(x_fit, myfunc(x_fit, result.params))
ax1.set_xscale('log')
ax1.set_xlim(0.1, 1000)
ax1.set_ylim(0, y.max()*1.2)
ax1.plot(x_fit,single(x_fit, para1))
ax1.plot(x_fit,single(x_fit, para2))
ax1.plot(x_fit,single(x_fit, para3))

plt.show()