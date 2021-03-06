#!/usr/bin/python

import numpy as np
from scipy import optimize
from sympy import *
import matplotlib.pyplot as plt
import pdb

# def evalResidual(point,S,Sp,CFL):
#     Res=0.
#     if S.shape[0]==1:
#         S1=[S[0,0]]
#         S2=[S[0,1]]
#         Sum1=np.sum(S1) ; Sum2=np.sum(S2)
#         Nmp=1
#     else:
#         S1=np.asarray(S[0,:])[0]
#         S2=np.asarray(S[1,:])[0]
#         Sum1=np.sum(S1) ; Sum2=np.sum(S2)
#         Nmp=len(S1) 
#     if Sp.shape[0]==1:
#         Sp1=[Sp[0,0]]
#         Sp2=[Sp[0,0]]
#         Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
#         Nmpp=1
#     else:
#         Sp1=np.asarray(Sp[0,:])[0]
#         Sp2=np.asarray(Sp[1,:])[0]
#         Sump1=np.sum(Sp1) ; Sump2=np.sum(Sp2)
#         Nmpp=len(Sp1) 
#     # Sum over material points in curent cell
#     for p in range(Nmp):
#         ## First order contributions
#         D_mu = S1[point]*S1[p]/Sum1 + S2[point]*S2[p]/Sum2 + CFL*( S2[point]/Sum2 - S1[point]/Sum1 -Nmp*S2[point]*S2[p]/(Sum2**2) )
#         ## Second order contributions
#         D_mu += 0.5*Nmp*(CFL**2)*((S2[p]/Sum2)*(S1[point]/Sum1-S2[point]/Sum2) + (S2[point]/(Sum2**2))*(Nmp*S2[p]/Sum2-1.) )
#         Res = Res +np.abs(D_mu)
#     # Sum over material points in previous cell
#     for p in range(Nmpp):
#         ## First order contributions
#         D_mu = CFL*Nmp*Sp2[p]*S1[point]/(Sum1*Sump2)
#         ## Second order contributions
#         D_mu +=0.5*Nmp*(CFL**2)*( S1[point]/(Sum1*Sump2)*(1.-Nmpp*Sp2[p]/Sump2) -(Sp2[p]/Sump2)*(S1[point]/Sum1-S2[point]/Sum2) )
#         Res=Res + np.abs(D_mu)  
#     return Res-1.

# Symbolic function to evaluate shape functions
shape_functions=lambda x,y: np.array([(1.-x)*(1.-y)/4.,(1.+x)*(1.-y)/4.,(1.+x)*(1.+y)/4.,(1.-x)*(1.+y)/4.])
grad_xi=lambda y:np.array([-(1.-y)/4.,(1.-y)/4.,(1.+y)/4.,-(1.+y)/4.])
grad_eta=lambda x:np.array([-(1.-x)/4.,-(1.+x)/4.,(1.+x)/4.,(1.-x)/4.])

# shapes=| N1(Xp1) N1(Xp2) ... N1(XNp) |
#        | N2(Xp1) N2(Xp2) ... N2(XNp) |
#        | N3(Xp1) N3(Xp2) ... N3(XNp) |
#        | N4(Xp1) N4(Xp2) ... N4(XNp) |

# grad_z=| N1_z(Xp1) N1_z(Xp2) ... N1_z(XNp) |
#        | N2_z(Xp1) N2_z(Xp2) ... N2_z(XNp) |
#        | N3_z(Xp1) N3_z(Xp2) ... N3_z(XNp) |
#        | N4_z(Xp1) N4_z(Xp2) ... N4_z(XNp) |

# where Ni(Xj) is the shape function of node i evaluated at the jth particles position


def symbolResidual(point,cx,cy,XC,XB,XL,XBL=0):
    transverse=True
    if XBL==0: transverse=False
    shapesC=shape_functions(XC[0],XC[1])
    dSxi_C=grad_xi(XC[1])
    dSeta_C=grad_eta(XC[0])
    shapesB=shape_functions(XB[0],XB[1])
    dSxi_B=grad_xi(XB[1])
    dSeta_B=grad_eta(XB[0])
    shapesL=shape_functions(XL[0],XL[1])
    dSxi_L=grad_xi(XL[1])
    dSeta_L=grad_eta(XL[0])
    ## Number of material points in cells
    NmpC=len(XC[0])
    NmpL=len(XL[0])
    NmpB=len(XB[0])
    if XBL!=0:
        shapesBL=shape_functions(XL[0],XL[1])
        dSxi_BL=grad_xi(XBL[1])
        dSeta_BL=grad_eta(XBL[0])
        NmpBL=len(XBL[0])
    else:
        NmpBL=0

    dt = symbols('dt')
    ## sum_i^K = np.sum(shapesK[i,:]) with cell K and node i
    ## shape functions evaluated at edges centers to weight fluxes contributions
    ## o -- 3 -- o
    ## |         |
    ## 4         2
    ## |         |
    ## o -- 1 -- o
    shapeOnEdge=shape_functions(np.array([0.,1.,0.,-1.]),np.array([-1.,0.,1.,0.]))
    ## Define the normal to edges
    Nx=np.array([0.,1.,0.,-1.])
    Ny=np.array([-1.,0.,1.,0.])
    Nnodes=4
    Nedges=4
    Res=0.
    for P in range(NmpC):
        ## Contributions of material points sharing the same cell
        D_PI=0.
        for i in range(Nnodes):
            # 0th-order contributions
            wheightings=shapesC[i,point]/np.sum(shapesC[i,:])
            D_PI+=wheightings*shapesC[i,P]
            # 1st-order contributions
            for j in range(Nnodes):
                D_PI+=dt*wheightings*(shapesC[j,P]/np.sum(shapesC[j,:]))*(cx*np.dot(dSxi_C[i,:],shapesC[j,:]) + cy*np.dot(dSeta_C[i,:],shapesC[j,:]))
            # Contributions of edges 2 and 3
            D_PI-=0.25*dt*wheightings*shapeOnEdge[i,1]*NmpC*cx*(shapesC[1,P]/np.sum(shapesC[1,:])+shapesC[2,P]/np.sum(shapesC[2,:]))
            D_PI-=0.25*dt*wheightings*shapeOnEdge[i,2]*NmpC*cx*(shapesC[2,P]/np.sum(shapesC[2,:])+shapesC[3,P]/np.sum(shapesC[3,:]))
            # Transverse contributions
            if transverse:
                D_PI+= (0.25*dt)**2*wheightings*shapeOnEdge[i,1]*NmpC*cx*cy*(shapesC[0,P]/np.sum(shapesC[0,:])+shapesC[1,P]/np.sum(shapesC[1,:]))
                D_PI+= (0.25*dt)**2*wheightings*shapeOnEdge[i,2]*NmpC*cx*cy*(shapesC[0,P]/np.sum(shapesC[0,:])+shapesC[3,P]/np.sum(shapesC[3,:]))
        Res+=np.abs(D_PI)
    ## Contributions of material points of left cell
    for P in range(NmpL):
        D_PI=0.
        for i in range(Nnodes):
            wheightings=shapesC[i,point]/np.sum(shapesC[i,:])
            ## edge 4 contribution
            D_PI+= 0.25*dt*wheightings*shapeOnEdge[i,3]*NmpC*cx*(shapesL[2,P]/np.sum(shapesL[2,:])+shapesL[3,P]/np.sum(shapesL[3,:]))
            if transverse:
                D_PI-=(0.25*dt)**2*wheightings*shapeOnEdge[i,3]*NmpC*cx*cy*(shapesL[0,P]/np.sum(shapesL[0,:])+shapesL[1,P]/np.sum(shapesL[1,:]))
                ## edge 3 contribution
                D_PI-=(0.25*dt)**2*wheightings*shapeOnEdge[i,2]*NmpC*cy*cx*(shapesL[1,P]/np.sum(shapesL[1,:])+shapesL[2,P]/np.sum(shapesL[2,:]))
        Res+=np.abs(D_PI)
    ## Contributions of material points of bottom cell            
    for P in range(NmpB):
        D_PI=0.
        for i in range(Nnodes):
            wheightings=shapesC[i,point]/np.sum(shapesC[i,:])
            ## edge 1 contribution
            D_PI+= 0.25*dt*wheightings*shapeOnEdge[i,0]*NmpC*cy*(shapesB[2,P]/np.sum(shapesB[2,:])+shapesB[3,P]/np.sum(shapesB[3,:]))
            if transverse:
                D_PI-=(0.25*dt)**2*wheightings*shapeOnEdge[i,0]*NmpC*cy*cx*(shapesB[0,P]/np.sum(shapesB[0,:])+shapesB[3,P]/np.sum(shapesB[3,:]))
                ## edge 2 contribution
                D_PI-=(0.25*dt)**2*wheightings*shapeOnEdge[i,1]*NmpC*cx*cy*(shapesB[2,P]/np.sum(shapesB[2,:])+shapesB[3,P]/np.sum(shapesB[3,:]))
        Res+=np.abs(D_PI)
    ## Contributions of material points of bottom-left cell
    for P in range(NmpBL):
        D_PI=0.
        for i in range(Nnodes):
            wheightings=shapesC[i,point]/np.sum(shapesC[i,:])
            ## edge 1 contribution
            D_PI+=(0.25*dt)**2*wheightings*shapeOnEdge[i,0]*NmpC*cy*cx*(shapesBL[1,P]/np.sum(shapesBL[1,:])+shapesBL[2,P]/np.sum(shapesBL[2,:]))
            ## edge 4 contribution
            D_PI+=(0.25*dt)**2*wheightings*shapeOnEdge[i,3]*NmpC*cx*cy*(shapesBL[2,P]/np.sum(shapesBL[2,:])+shapesBL[3,P]/np.sum(shapesBL[3,:]))
        Res+=np.abs(D_PI)
    Residual = lambdify((dt),Res-1.)
    return Residual


def rootFinder(function,tol=1.e-12):
    NiterMax=1000
    # Find the bigest root of the residual by dichotomy algorithm
    a0=function(0.)
    a1=function(1.)
    it=0
    #pdb.set_trace()
    if a0*a1>tol:
        print "No solution can be found within the [0,1]"
    while (a1-a0)>tol:
        it+=1
        a2=0.5*(a0+a1)
        if function(a2)<1.e-7:
            a0=a2
        else:
            a1=a2
        if (a1-a0)<tol:
            return a0
        if it == NiterMax :
            print "Solution not converged yet"
            return a0

def gridSearch(function,tol=1.e-7):
    samples=500000
    # Find the bigest root of the residual by grid search algorithm
    CFL=np.linspace(0.,1.,samples)
    for i in CFL:
        if i==samples-1:return i
        a0=function(i)
        if a0<tol:
            continue
        else:
           return i

cx=20.;cy=20.
print "Speeds: cx/cy=",cx/cy
############### 1PPC
print "**************************************************************"
print "******************  1PPC discretization **********************"
print "**************************************************************"
# Local coordinates of material points in current element
Xp=np.array([0.])
Yp=np.array([0.])

solution=optimize.fsolve(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution DCU is: ",CFL,cx*solution/2. + cy*solution/2.

Residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp))
CFL=np.linspace(0.,1.,100.)
res=np.zeros(len(CFL))
for i in range(len(CFL)):
    res[i]=Residual(2.*CFL[i]/max(cx,cy))
plt.plot(CFL,res)
plt.grid()
plt.show()



Residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solution=optimize.root(Residual,1.,method='hybr',options={'xtol':1.e-12}).x
# print solution
solution=optimize.fsolve(Residual,1.)
CFL=max(cx,cy)*solution/2.

print "Solution CTU is: ",CFL
CFL=np.linspace(0.,1.,100.)
res=np.zeros(len(CFL))
for i in range(len(CFL)):
    res[i]=Residual(2.*CFL[i]/max(cx,cy))
plt.plot(CFL,res)
plt.grid()
plt.show()

pdb.set_trace()
cx=20.;cy=20.
print "Speeds: cx/cy=",cx/cy

# ############### 2PPC
# print "**************************************************************"
# print "******************  2PPC discretization **********************"
# print "**************************************************************"
# print "=== Symmetric horizontal ==="
# Xp=np.array([-0.5,0.5])
# Yp=np.array([0.,0.])

# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL, " (Newton ", 0.5*max(cx,cy)*solutionN,")"


# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solution=gridSearch(residual)
# solutionN=optimize.newton(residual,1.)
# CFL=(max(cx,cy)*solution/2.)
# print "Solution CTU is: ",CFL, " (Newton ",0.5*max(cx,cy)*solutionN,")"

# print "   "
# print "=== Symmetric vertical ==="
# Yp=np.array([-0.5,0.5])
# Xp=np.array([0.,0.])

# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL, " (Newton ", 0.5*max(cx,cy)*solutionN,")"


# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(residual,1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution CTU is: ",CFL, " (Newton ",0.5*max(cx,cy)*solutionN,")"

# print "   "
# print "=== Shifted ==="
# print "=== Symmetric horizontal ==="
# Xp=np.array([-0.25,0.25])
# Yp=np.array([0.,0.])

# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(residual,1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL, " (Newton ", 0.5*max(cx,cy)*solutionN,")"

# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(residual,1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution CTU is: ",CFL, " (Newton ",0.5*max(cx,cy)*solutionN,")"


# print "   "
# print "=== Symmetric vertical ==="
# Yp=np.array([-0.25,0.25])
# Xp=np.array([0.,0.])

# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(residual,1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL, " (Newton ", 0.5*max(cx,cy)*solutionN,")"


# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solutionN=optimize.newton(residual,1.)
# solution=gridSearch(residual)
# CFL=max(cx,cy)*solution/2.
# print "Solution CTU is: ",CFL, " (Newton ",0.5*max(cx,cy)*solutionN,")"

# CFL=np.linspace(0.,1.,10000)
# res=np.zeros(len(CFL))
# for i in range(len(CFL)):
#     res[i]=residual(2.*CFL[i]/max(cx,cy))
# plt.plot(CFL,res,label='residual')
# plt.plot([0.5*max(cx,cy)*solution,0.5*max(cx,cy)*solution],[0,max(res)],'g',label='grid search')
# plt.plot([0.5*max(cx,cy)*solutionN,0.5*max(cx,cy)*solutionN],[0,max(res)],'r',label='Newton')
# plt.legend()
# plt.grid()
# plt.show()

############### 4PPC
print "**************************************************************"
print "******************  4PPC discretization **********************"
print "**************************************************************"
print "=== Symmetric ==="
# Xp=np.array([-0.25,0.25,0.25,-0.25])
# Yp=np.array([-0.25,-0.25,0.25,0.25])

# solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL


# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# CFL=max(cx,cy)*solution/2.
# print "Solution CTU is: ",CFL


# print "=== Shiffted symmetrically ==="
# Xp=np.array([-0.5,0.5,0.5,-0.5])
# Yp=np.array([-0.5,-0.5,0.5,0.5])

# solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# CFL=max(cx,cy)*solution/2.
# print "Solution DCU is: ",CFL


# residual=symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp))
# solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
# CFL=max(cx,cy)*solution/2.
# print "Solution CTU is: ",CFL
cx=20.;cy=2.
print "Speeds: cx/cy=",cx/cy


print "    "
print "=== Shiffted right ==="
shift=+0.25
Xp=np.array([-0.25,0.25,0.25,-0.25])+shift
Yp=np.array([-0.25,-0.25,0.25,0.25])

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution DCU is: ",CFL


solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution CTU is: ",CFL

print "    "
print "=== Shiffted above ==="
Xp=np.array([-0.25,0.25,0.25,-0.25])
Yp=np.array([-0.25,-0.25,0.25,0.25])+shift

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution DCU is: ",CFL


solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution CTU is: ",CFL

print "    "
print "=== Shiffted left ==="
shift=-0.25
Xp=np.array([-0.25,0.25,0.25,-0.25])+shift
Yp=np.array([-0.25,-0.25,0.25,0.25])

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution DCU is: ",CFL

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution CTU is: ",CFL

print "    "
print "=== Shiffted below ==="
Xp=np.array([-0.25,0.25,0.25,-0.25])
Yp=np.array([-0.25,-0.25,0.25,0.25])+shift

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution DCU is: ",CFL

solution=optimize.newton(symbolResidual(0,cx,cy,(Xp,Yp),(Xp,Yp),(Xp,Yp),(Xp,Yp)),1.)
CFL=max(cx,cy)*solution/2.
print "Solution CTU is: ",CFL

