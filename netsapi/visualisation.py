import sys, os
import numpy as np
# import tensorflow as tf
# import gpflow
import numpy.ma as ma

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def ResponseSurface(rewards):
    Q = rewards
    XYg = Q[:,(0,1)]
    # print 'XYg=',XYg
    Z = Q[:,2]
    Z = Z.reshape(-1,1)

    #Normalise
    Z = Z - np.amin(Z) + 0.01 #set max at zero

#     Z = np.log(Z)



    ##Plotting data
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #plt.hold(True)
    ax.scatter(XYg[:,0], XYg[:,1], Z, c = 'r', marker = 'x')

    ax.set_xlabel('ITN_coverage')
    ax.set_ylabel('IRS_coverage')
    ax.set_zlabel('Normalised Reward')
    #
    #Fitting GP
    # k = gpflow.kernels.Matern52(2, lengthscales=0.2)
    # m = gpflow.models.GPR(XYg, Z, kern=k)
    # m.likelihood.variance = 0.1
    # # m.likelihood.variance.trainable = False
    # # m.read_trainables()
    # # print(m)
    # # gpflow.train.ScipyOptimizer().minimize(m)
    # # # m.optimize()
    # # print(m)

    # # m.clear()
    # # m.kern.lengthscales.prior = gpflow.priors.Gamma(1., 1.)
    # # m.kern.variance.prior = gpflow.priors.Gamma(1., 1.)
    # # m.likelihood.variance.prior = gpflow.priors.Gamma(1., 1.)
    # # m.compile()
    # # print(m)

    # # sampler = gpflow.train.HMC()
    # # samples = sampler.sample(m, num_samples=500, epsilon=0.05, lmin=10, lmax=20, logprobs=False)


    # # sampler = gpflow.train.HMC()
    # # samples = sampler.sample(m, num_samples=500, epsilon=0.05, lmin=10, lmax=20, logprobs=False)

    # n=100

    # xitn = np.linspace(0,1,n)#take from Action and time space
    # xirs = np.linspace(0,1,n)
    # x, y = np.meshgrid(xitn, xirs)

    # xg = x.reshape(-1,1)
    # yg = y.reshape(-1,1)
    # #
    # xyg = np.concatenate((xg, yg), axis=1)

    # mean, var = m.predict_y(xyg)

    # z = mean.reshape((n,n))
    # v_up = mean[:,0] + 2*np.sqrt(var[:,0])
    # v_down = mean[:,0] - 2*np.sqrt(var[:,0])
    # #print 'v_up=',v_up
    # v_up_plot = v_up.reshape((n,n))
    # v_down_plot = v_down.reshape((n,n))
    # #
    # fig, ax = plt.subplots(nrows=1, ncols=1)

    # im = ax.pcolor(x, y, z,cmap=cm.Reds, vmin=np.amin(z), vmax=np.amax(z), alpha = 1)
    # ax.contour(x, y, z, 4, colors='k')
    # # ax.set_title('GPR')
    # ax.set_xlabel('ITN Coverage')
    # ax.set_ylabel('IRS Coverage')
    # ax.set_xlim(0.55,1)
    # ax.set_ylim(0,1)

    # fig.colorbar(im, label = '-log Normalised Reward')
    # plt.subplots_adjust(wspace=2, hspace=1)


    # ax.scatter(presults[:-2,0], presults[:-2,1], c = 'k', marker = 'o', s = 35)
    # ax.text(presults[0,0], presults[0,1] + 0.02, '1: {%.2f, %.2f}' % (presults[0,0], presults[0,1]), color = 'k', fontsize=10, horizontalalignment='center', weight = 'bold')
    # ax.text(presults[1,0], presults[1,1] + 0.02, '2: {%.2f, %.2f}' % (presults[1,0], presults[1,1]), color = 'k', fontsize=10, horizontalalignment='center')
    # ax.text(presults[2,0], presults[2,1] + 0.02, '3: {%.2f, %.2f}' % (presults[2,0], presults[2,1]), color = 'k', fontsize=10, horizontalalignment='center')
    # ax.scatter(presults[3,0], presults[3,1], c = 'k', marker = 'o', s = 50)
    # ax.text(presults[3,0] - 0.05, presults[3,1] + 0.02, 'Current: {%.2f, %.2f}' % (presults[3,0], presults[3,1]), fontsize=11,)

    # ax.scatter(presults[4,0], presults[4,1], c = 'k', marker = 'o', s = 50)
    # ax.text(presults[4,0], presults[4,1] + 0.02, 'Expert Human: {%.2f, %.2f}' % (presults[4,0], presults[4,1]), fontsize=11, horizontalalignment='center')

    #
    plt.show()
