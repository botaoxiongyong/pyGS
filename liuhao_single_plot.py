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
path = '/home/jiabo/google_drive/硕士资料/兰大/'  #文件路径
sample = 'liuhao_grainsize.dat'         #文件名

l = []
with open(path + sample) as dat:
    data = dat.readlines()
    for lines in data:
        var = lines.split()
        l.append(var)

i = 500
smaplenum = str(l[i][0])                    #样品号
print  smaplenum
x = np.array(l[0], dtype=np.float64)        #粒级
y = np.array(l[i][1:101], dtype=np.float64) #含量
y_df = np.gradient(y)
y_df2 = np.gradient(y_df)

x_ = np.logspace(np.log10(0.2), np.log10(x.max()), 1000)
y_t = interpolate.splrep(x, y)
y_ = interpolate.splev(x_, y_t)
'''
x_over_1 = []
y_over_1 = []
x_blow_1 = []
y_blow_1 = []
for i in np.arange(len(x_)):
    if x_[i] >= 1.01:
        x_over_1.append(x_[i])
        y_over_1.append(y_[i])
    elif x_[i] < 1.01:
        x_blow_1.append(x_[i])
        y_blow_1.append(y_[i])
'''


x_fit=[]
for i in x_:
    x_fit.append(np.log10(i)+1)

y_interp = y_


#func and residuals is used for scipy leatsq results

#
#myfunc and myresiduals are used for lmfit with parameter aranges
def func(x_fit, params):
    #p, p1, p2, a, a1, a2, b, b1, b2 = para\
    y_component=[]
    for i in np.arange(len(params)/3):
        p = 'p'+str(i)
        a = 'a'+str(i)
        b = 'b'+str(i)
        p = params[p].value
        a= params[a].value
        b= params[b].value
        y = p * (a / b) * x_fit ** (a - 1) * np.exp(-((x_fit / b) ** a))
        y_component.append(y)

    return sum(y_component)

def residuals(params, x_fit, y_interp):
    return y_interp - func(x_fit, params)

#
#single is for single endmember result
def single(x_fit, para):
    p, a, b = para
    return p * (a / b) * x_fit ** (a - 1) * np.exp(-((x_fit / b) ** a))



group=3

para = [1]*group
para.extend([1]*group)
para.extend([3]*group)

plsq = para

################
params = Parameters()
for i in np.arange(len(plsq)/3):
    p = 'p'+str(i)
    a = 'a'+str(i)
    b = 'b'+str(i)
    if i == 0:
        params.add(p, value=abs(plsq[i]), min=10**-1)
        params.add(a, value=abs(plsq[i+len(plsq)/3]), min=0.5)
        params.add(b, value=0.5, min=0.1, max=1.1)
    else:
        params.add(p, value=abs(plsq[i]), min=10**-10)
        params.add(a, value=abs(plsq[i+len(plsq)/3]), min=10**-5)
        params.add(b, value=abs(plsq[i + 2*len(plsq)/3]), min=0.5, max=5)


#
#using lmfit to get the final result without negtive values
result = minimize(residuals, params, args=(x_fit, y_interp), method='leastsq')
final = y_interp +result.residual
report_fit(result.params)
print result.aic


#
#start to draw the figs
fig = plt.figure(figsize=(20, 10), dpi=50, facecolor='white')
fig.suptitle(smaplenum)
ax = fig.add_subplot(121)
ax.plot(np.log10(x), y)
ax.plot(np.log10(x), y_df)
ax.plot(np.log10(x), y_df2)
#ax.set_xscale('log')
#ax.set_xlim(0.1, 1000)
ax1 = fig.add_subplot(122)
ax1.scatter(x, y, c='red')
#ax1.plot(10**x_fit, y_interp)
ax1.plot(x_, func(x_fit, result.params))
ax1.set_xscale('log')
ax1.set_xlim(0.1, 10**3)
ax1.set_ylim(0, y.max()*1.2)

y_test = []
for i in np.arange(group):
    p = 'p'+str(i)
    a = 'a'+str(i)
    b = 'b'+str(i)
    para = [result.params[p].value, result.params[a].value, result.params[b].value]
    ax1.plot(x_,single(x_fit, para))
    if i == 0:
        y_test.append(single(x_fit, para))

#ax1.plot(10**x_fit, y_-sum(y_test))
fig.savefig('/home/jiabo/google_drive/硕士资料/兰大/' +smaplenum+'_liuhao.png')
plt.show()