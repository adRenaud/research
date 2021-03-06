import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import pdb
from scipy.integrate import ode
from scipy.optimize import fsolve

"""
Implementation of high order shock capturing methods to solve the 1D elastoviscoplastic set of equations with the model of Sokolowski-Malvern.
The viscoplasticity is treated through the addition of a right hand side containing the viscoplastic flow rule. The right hand side is treated by a second order splitting approach: the total solution is advanced of 2*dt at each time step.
Plane Wave 1D strain case.
"""

E_A=Young
nu_A=nu
rho_A=rho
Sigy_A=Sigy
H_A=H
eta_A=eta
n_A=n
sigd=0.

#Define 1D mesh
#Intercells points
DX=length/Nelem

x = np.linspace(0.,length,Nelem+1)
x = np.linspace(-DX/2.,length+DX/2.,Nelem+1)
dx = x[1]-x[0]
y=x+(dx/2.0)
#Centres of cells
y=y[:(len(y)-1)]
centroids=y

#Define parameters
t = np.zeros(NTmaxi)
#Define material parameters
lam_A = (E_A*nu_A)/((1.0+nu_A)*(1.0-2.0*nu_A)) 
mu_A = E_A/(2.0*(1.0+nu_A))
c_A = np.sqrt((lam_A+2.0*mu_A)/rho_A)

"""Limiters of waves:
mthlim(i)<0: no limiter
         =0: minmod limiter
         =1: superbee limiter
         =2: van Leer limiter
         =3: Monotonized centered
         =4: Beam-Warming
         =5: Lax-Wendroff
"""
limit = True
mthlim = np.zeros(2,dtype=int)
for idx,i in enumerate(mthlim):
    mthlim[idx] = -1   #Choose of the Superbee limiter

#Definition of arrays
#Ghost cells at both ends of the bar are used to prescribe boundary conditions
v = np.zeros((len(y)+4,NTmaxi))
disp = np.zeros((len(y)+4,NTmaxi))
sig = np.zeros((len(y)+4,NTmaxi))
eps = np.zeros((len(y)+4,NTmaxi))
U = np.zeros((len(y)+4,2))
matC = np.zeros(len(y)+4)
rho = np.zeros(len(y)+4)
Sigy = np.zeros(len(y)+4)
H = np.zeros(len(y)+4)
lam = np.zeros(len(y)+4)
mu = np.zeros(len(y)+4)
eta = np.zeros(len(y)+4)
n = np.zeros(len(y)+4)
EP = np.zeros((len(y)+4,NTmaxi))
dEP = np.zeros((len(y)+4,NTmaxi))


#Initial conditions et definition properties
matC[:] = c_A 
rho[:] = rho_A
Sigy[:] = Sigy_A
H_A*=3.0/2.0
H[:] = H_A
eta[:] = eta_A
n[:] = n_A
lam[:] = lam_A
mu[:] = mu_A

for i in range(len(y)+4):
    if (i<len(range(len(y)+4))/2):
        v[i,0] = v0
        matC[i] = c_A 
        rho[i] = rho_A
        Sigy[i] = Sigy_A
        H[i] = H_A
        eta[i] = eta_A
        n[i] = n_A
    else:
        v[i,0] = -v0
        matC[i] = c_A 
        rho[i] = rho_A
        Sigy[i] = Sigy_A
        H[i] = H_A
        eta[i] = eta_A
        n[i] = n_A

U[:,0] = sig[:,0]
U[:,1] = v[:,0]



#Definition of functions
def computeAlpha(dU,rho1,rho2,c1,c2):
    alpha1 = (dU[0]+rho2*c2*dU[1])/(rho1*c1+rho2*c2)
    alpha2 = -(dU[0]-rho1*c1*dU[1])/(rho1*c1+rho2*c2)
    return [alpha1,alpha2]

def computeElasticWaves(alpha,rho1,rho2,c1,c2):
    w = np.zeros((2,2))
    w[:,0] = alpha[0]*np.array([rho1*c1,1])
    w[:,1] = alpha[1]*np.array([-rho2*c2,1])
    return w

def computeFlux(U,rho,matC):
    amdq = np.zeros((Nelem+3,U.shape[1]))
    apdq = np.zeros((Nelem+3,U.shape[1]))
    waves = np.zeros((Nelem+3,U.shape[1],U.shape[1]))
    s = np.zeros((Nelem+3,U.shape[1]))
    #Loop on interfaces
    for i in range(Nelem+3):
        UL = U[i,:]
        UR = U[i+1,:]
        dU = UR-UL
        #Resolution du probleme de Riemann
        alpha = computeAlpha(dU,rho[i],rho[i+1],matC[i],matC[i+1])
        waves[i,:,:] = computeElasticWaves(alpha,rho[i],rho[i+1],matC[i],matC[i+1])
        amdq[i,:] = -matC[i]*waves[i,:,0]
        apdq[i,:] = matC[i+1]*waves[i,:,1]
        s[i,0] = -matC[i] ; s[i,1] = matC[i+1]
    return amdq,apdq,waves,s

def computeLimitedWaves(waves,s,mthlim,dtdx):
    cqxx = np.zeros((Nelem+3,U.shape[1]))
    #Loop on interfaces
    for i in range(Nelem+2)[1:]:
        #Apply limiter to waves 
        modWaves = limiter(s[i,:],waves[i,:,:],waves[i-1,:,:],waves[i+1,:,:],mthlim,i)
        #Second order corrections of normal fluxes
        for j in range(len(s[i,:])):
            cqxx[i,:] += np.abs(s[i,j])*(1.0-(dtdx)*np.abs(s[i,j]))*modWaves[:,j]
    return cqxx

def limiter(s,wave,wave_L,wave_R,mthlim,j):
    modWaves = np.zeros((2,2))
    for i in range(len(s)):
        if (mthlim[i]>=0) and (not (wave[:,i]==np.zeros(2)).all()):
            #Compute the L2-norm of wave and projections
            wnorm2 = np.dot(wave[:,i],wave[:,i])
            if (wnorm2 == 0.0):
                print 'wnorm2 = 0 pour l onde',i,'de l edge',j
                print 'wave[:,:,',j,'] = ',wave
                break
            wwR = np.dot(wave[:,i],wave_R[:,i])
            wwL = np.dot(wave[:,i],wave_L[:,i])
            #Upwind and compute wave strength
            if (s[i]>0.0):
                wlimiter = philim(wnorm2,wwL,mthlim[i])
            else:
                wlimiter = philim(wnorm2,wwR,mthlim[i])
        else:
            wlimiter =0.0
        #Apply the limiter
        modWaves[:,i] = wlimiter*wave[:,i]
    return modWaves

def philim(a,b,meth):
    theta = b/a
    if (meth==0):
        philim = np.max([0.0,np.min([1.0,theta])])  #minmod
    elif (meth==1):
        philim = np.max([0.0,np.min([1.0,2.0*theta]),np.min([2.0,theta])])  #superbee
    elif (meth==2):
        philim = (theta+np.abs(theta))/(1.0+np.abs(theta))   #van Leer
    elif (meth==3):
        c=(1.0+theta)/2.0
        philim = np.max([0.0,np.min([c,2.0,2.0*theta])])   #Monotonized Centered
    elif (meth==4): 
        philim = theta                                   #Beam-Warming
    elif (meth==5):       
        philim = 1.0                                   #Lax-Wendroff
    return philim


def conservativeUpdate(U,dt0dx,amdq,apdq,cqxx,limit):
    for i in range(Nelem+2)[2:]:
        U[i,:] -= dt0dx*(apdq[i-1,:]+amdq[i,:])
        if (limit):
            U[i,:] -= (dt0dx/2.0)*(cqxx[i,:]-cqxx[i-1,:])


def positive_part(x):
    return 0.5*(x+np.abs(x))

def creep_law(f,Seq,eta,n):
    return ((positive_part(f)/eta)**n)*np.sign(Seq)

def criterion(Seq,Sigy):
    return (np.abs(Seq)-Sigy)

def computeSeq(S,EP,lam,mu,H):
    KK = 3.0*(H/2.0) +(mu*(3.0*lam+2.0*mu))/(lam+2.0*mu)
    #KK = H +0.5*(4.*mu*(lam+mu)-lam**2)/(lam+2.0*mu)
    return (((2.0*mu)/(lam+2.0*mu))*S-KK*EP)


def computeS(t,U,EP,lam,mu,H,Sigy,eta,n):
    S = np.zeros(len(U))
    Seq = computeSeq(U[0],EP,lam,mu,H)
    f = criterion(Seq,Sigy)
    S[0] = -(2.0*mu)*creep_law(f,Seq,eta,n)
    S[1] = 0
    return S


#pdb.set_trace()

for i in range(NTmaxi)[1:]:
    #Apply Courant condition
    dt = dx/np.max(c_A)
    if ((t[i-1]+dt)>timeOut):
        dt = timeOut - t[i-1]
    t[i]=t[i-1]+dt
    #Apply boundary conditions: prescribed stress on the left
    U[0,0] = 2.0*sigd-U[3,0] ; U[0,1] = U[3,1]
    U[1,0] = 2.0*sigd-U[2,0] ; U[1,1] = U[2,1]
    #reflective boundary on the right
    U[Nelem+1+1,0] = -U[Nelem+1,0] ; U[Nelem+1+1,1] = U[Nelem+1,1]
    U[Nelem+2+1,0] = -U[Nelem-1+1,0] ; U[Nelem+2+1,1] = U[Nelem-1+1,1]
    #Compute flux first order
    amdq,apdq,waves,s = computeFlux(U,rho,matC)
    #Compute second order fluxes
    cqxx = computeLimitedWaves(waves,s,mthlim,dt/dx)
    #Conservative update
    conservativeUpdate(U,dt/dx,amdq,apdq,cqxx,limit)
    #RHS (2)
    for j in range(Nelem+4):
        r = ode(computeS).set_integrator('vode', method='bdf')
        r.set_initial_value(U[j,:],t[i]).set_f_params(EP[j,i-1],lam[j],mu[j],H[j],Sigy[j],eta[j],n[j])
        r.integrate(r.t+(dt))
        if r.successful():
            U[j,:] = r.y
    #Update of fields and Store results
    sig[:,i] = U[:,0]
    v[:,i] = U[:,1]
    Seq = computeSeq(sig[:,i],EP[:,i-1],lam,mu,H)
    f = criterion(Seq,Sigy)
    #Explicit update of the viscoplastic strain
    EP[:,i] = EP[:,i-1] + creep_law(f,Seq,eta,n)*dt
    dEP[:,i] = (EP[:,i] - EP[:,i-1])/dt
    #Update of the displacement field
    disp[:,i] = disp[:,i-1] + v[:,i]*dt
    eps[:,i] = (sig[:,i]+2*mu_A*EP[:,i])/(lam_A+2.0*mu_A)
    if (t[i]==timeOut):
        increments=i
        break
sig=sig[2:-2,:increments]
EP=EP[2:-2,:increments]
