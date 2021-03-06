#!/usr/bin/python

import numpy as np
from scipy import optimize
from sympy import *
import matplotlib.pyplot as plt
import pdb

def evalResidual(point,S,Sp,CFL):
    Res=0.
    if S.shape[0]==1:
        S1=[S[0,0]]
        S2=[S[0,1]]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=1
    else:
        S1=np.asarray(S[0,:])[0]
        S2=np.asarray(S[1,:])[0]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=len(S1) 
    if Sp.shape[0]==1:
        Sp1=[Sp[0,0]]
        Sp2=[Sp[0,0]]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=1
    else:
        Sp1=np.asarray(Sp[0,:])[0]
        Sp2=np.asarray(Sp[1,:])[0]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=len(Sp1) 
    # Sum over material points in curent cell
    for p in range(Nmp):
        ## First order contributions
        D_mu = S1[point]*S1[p]/Sum1 + S2[point]*S2[p]/Sum2 + CFL*( S2[point]/Sum2 - S1[point]/Sum1 -Nmp*S2[point]*S2[p]/(Sum2**2) )
        Res = Res +np.abs(D_mu)
    # Sum over material points in previous cell
    for p in range(Nmpp):
        ## First order contributions
        D_mu = CFL*Nmp*Sp2[p]*S1[point]/(Sum1*Sump2)
        ## Second order contributions
        Res=Res + np.abs(D_mu)  
    return Res-1.

def symbolResidual(point,S,Sp):
    CFL = symbols('CFL')
    Res=0.
    if S.shape[0]==1:
        S1=[S[0,0]]
        S2=[S[0,1]]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=1
    else:
        S1=np.asarray(S[0,:])[0]
        S2=np.asarray(S[1,:])[0]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=len(S1) 
    if Sp.shape[0]==1:
        Sp1=[Sp[0,0]]
        Sp2=[Sp[0,0]]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=1
    else:
        Sp1=np.asarray(Sp[0,:])[0]
        Sp2=np.asarray(Sp[1,:])[0]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=len(Sp1) 
    # Sum over material points in curent cell
    #pdb.set_trace()
    for p in range(Nmp):
        ## First order contributions
        D_mu = S1[p]*S1[point]/Sum1 + S2[p]*S2[point]/Sum2 + CFL*( S2[point]/Sum2 - S1[point]/Sum1 -Nmp*S2[p]*S2[point]/(Sum2**2) )
        ## Second order contributions
        #D_mu += 0.5*Nmp*(CFL**2)*((S2[p]/Sum2)*(S1[point]/Sum1-S2[point]/Sum2) + (S2[point]/Sum2)*(Nmp*S2[p]/Sum2-1.)/Sum2)
        Res = Res +np.abs(D_mu)
    # Sum over material points in previous cell
    #pdb.set_trace()
    for p in range(Nmpp):
        ## First order contributions
        D_mu = CFL*Nmp*Sp2[p]*S1[point]/(Sum1*Sump2)
        ## Second order contributions
        #D_mu +=0.5*Nmp*(CFL**2)*( S1[point]/(Sum1*Sump2)*(1.-Nmpp*Sp2[p]/Sump2) -(Sp2[p]/Sump2)*(S1[point]/Sum1-S2[point]/Sum2) )
        Res=Res + np.abs(D_mu)    
    Residual = lambdify((CFL),Res-1.)
    #Residual = lambdify((CFL),np.abs(Res)-1.)
    return Residual

def computeResidual(CFL,point,S,Sp):
    Res=0.
    #pdb.set_trace()
    if S.shape[0]==1:
        S1=[S[0,0]]
        S2=[S[0,1]]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=1
    else:
        S1=np.asarray(S[0,:])[0]
        S2=np.asarray(S[1,:])[0]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=len(S1) 
    if Sp.shape[0]==1:
        Sp1=[Sp[0,0]]
        Sp2=[Sp[0,0]]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=1
    else:
        Sp1=np.asarray(Sp[0,:])[0]
        Sp2=np.asarray(Sp[1,:])[0]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=len(Sp1)
    # Sum over material points in curent cell
    for p in range(Nmp):
        ## First order contributions
        D_mu = S1[point]*S1[p]/Sum1 + S2[point]*S2[p]/Sum2 + CFL*( S2[point]/Sum2 - S1[point]/Sum1 -Nmp*S2[point]*S2[p]/(Sum2**2) )
        ## Second order contributions
        #D_mu += 0.5*Nmp*(CFL**2)*((S2[p]/Sum2)*(S1[point]/Sum1-S2[point]/Sum2) + (S2[point]/(Sum2**2))*(Nmp*S2[p]/Sum2-1.) )
        Res = Res +np.abs(D_mu)
    # Sum over material points in previous cell
    #pdb.set_trace()
    for p in range(Nmpp):
        ## First order contributions
        D_mu = CFL*Nmp*Sp2[p]*S1[point]/(Sum1*Sump2)
        ## Second order contributions
        #D_mu +=0.5*Nmp*(CFL**2)*( S1[point]/(Sum1*Sump2)*(1.-Nmpp*Sp2[p]/Sump2) -(Sp2[p]/Sump2)*(S1[point]/Sum1-S2[point]/Sum2) )
        Res=Res + np.abs(D_mu)  
    return Res

def accuracyResidual(CFL,point,order,S,Sp):
    Res=0.
    #pdb.set_trace()
    if S.shape[0]==1:
        S1=[S[0,0]]
        S2=[S[0,1]]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=1
    else:
        S1=np.asarray(S[0,:])[0]
        S2=np.asarray(S[1,:])[0]
        Sum1=np.sum(S1) ; Sum2=np.sum(S2)
        Nmp=len(S1) 
    if Sp.shape[0]==1:
        Sp1=[Sp[0,0]]
        Sp2=[Sp[0,0]]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=1
    else:
        Sp1=np.asarray(Sp[0,:])[0]
        Sp2=np.asarray(Sp[1,:])[0]
        Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
        Nmpp=len(Sp1)
    # Sum over material points in curent cell
    for p in range(Nmp):
        ## First order contributions
        D_mu = S1[point]*S1[p]/Sum1 + S2[point]*S2[p]/Sum2 + CFL*( S2[point]/Sum2 - S1[point]/Sum1 -Nmp*S2[point]*S2[p]/(Sum2**2) )
        Res += D_mu*(p-point)**order
    # Sum over material points in previous cell
    #pdb.set_trace()
    for p in range(Nmpp):
        ## First order contributions
        D_mu = CFL*Nmp*Sp2[p]*S1[point]/(Sum1*Sump2)
        Res+=D_mu*(point-(Nmpp-p))**order
    return Res-(-CFL)**order

# Symbolic function to evaluate shape functions
shape_functions=lambda x: np.matrix([(1-x)/DX,x/DX])

xn = np.array([0.,1.])
DX = 1.


CFL=np.linspace(0.,1.,100.)

############### 1PPC
print "**************************************************************"
print "******************  1PPC discretization **********************"
print "**************************************************************"
solution=optimize.root(symbolResidual(0,shape_functions(0.5),shape_functions(0.5)),1.,method='hybr',options={'xtol':1.e-4}).x[0]
print "Solution is: ",solution
order0=accuracyResidual(solution,0,0,shape_functions(0.5),shape_functions(0.5))
order1=accuracyResidual(solution,0,1,shape_functions(0.5),shape_functions(0.5))
order2=accuracyResidual(solution,0,2,shape_functions(0.5),shape_functions(0.5))
order3=accuracyResidual(solution,0,3,shape_functions(0.5),shape_functions(0.5))
order4=accuracyResidual(solution,0,4,shape_functions(0.5),shape_functions(0.5))
print "accuracy orders (0-1-2-3-4)",order1,order2,order2,order3,order4

############### 2PPC
print "**************************************************************"
print "******************  2PPC discretization **********************"
print "**************************************************************"
solution=optimize.root(symbolResidual(0,shape_functions(0.5*np.array([1.-1./np.sqrt(3.),1.+1./np.sqrt(3.)])),shape_functions(np.array([0.25,0.75]))),1.,method='hybr',options={'xtol':1.e-4}).x[0]
print "Solution is: ",solution
order0=accuracyResidual(solution,0,0,shape_functions(0.5*np.array([0.25,0.75])),shape_functions(np.array([0.25,0.75])))
order1=accuracyResidual(solution,0,1,shape_functions(0.5*np.array([0.25,0.75])),shape_functions(np.array([0.25,0.75])))
order2=accuracyResidual(solution,0,2,shape_functions(0.5*np.array([0.25,0.75])),shape_functions(np.array([0.25,0.75])))
print "accuracy orders (0-1-2-3-4)",order1,order2,order2
pdb.set_trace()
############### 3PPC
print "**************************************************************"
print "******************  3PPC discretization **********************"
print "**************************************************************"
solution=optimize.root(symbolResidual(0,shape_functions(np.array([0.25,0.5,0.75])),shape_functions(np.array([0.25,0.5,0.75]))),1.,method='hybr',options={'xtol':1.e-4}).x
print "Solution is: ",solution
############### 4PPC
print "**************************************************************"
print "******************  4PPC discretization **********************"
print "**************************************************************"
solution=optimize.root(symbolResidual(0,shape_functions(np.array([0.2,0.4,0.6,0.8])),shape_functions(np.array([0.2,0.4,0.6,0.8]))),1.,method='hybr',options={'xtol':1.e-4}).x
print "Solution is: ",solution

