# !\usr\bin\python
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import scipy.optimize
from matplotlib import animation
from scipy.integrate import ode
import pdb
from buildTeXFiles import *
import os
import sys

directory=os.path.basename(__file__)[:20]
if not os.path.exists('pgf_'+str(directory)+'/'):
    os.system('mkdir pgf_'+str(directory)+'/')
path='pgf_'+str(directory)+'/'


# Material parameters
rho = 7800.
E = 2.e11
nu = 0.3
mu = 0.5*E/(1.+nu)
kappa = E/(3.*(1.-2.*nu))
lamb = kappa-2.*mu/3.
sigy = 100.0e6        
H = 100.0e6
#H = 100.0e8
beta=(6.*mu**2)/(3.*mu+H)

        
def export2pgfPlot2D(fileName,field1,field2,dico={"xlabel":'x',"ylabel":'y'}):
    #pdb.set_trace()
    dataFile=open(fileName,"w")
    xlabel=dico["xlabel"]
    ylabel=dico["ylabel"]
    dataFile.write('# Curve ('+str(xlabel)+';'+str(ylabel)+') '+str(len(field1))+' points.\n')
    for i,x in enumerate(field1):
        dataFile.write(str(x)+' '+str(field2[i])+' \n')
    dataFile.close()

def export2pgfPlot3D(fileName,field1,field2,field3,dico={"xlabel":'x',"ylabel":'y',"zlabel":'z'}):
    #pdb.set_trace()
    dataFile=open(fileName,"w")
    # 2D export
    xlabel=dico["xlabel"]
    ylabel=dico["ylabel"]
    zlabel=dico["zlabel"]
    dataFile.write('# Curve ('+str(xlabel)+';'+str(ylabel)+';'+str(zlabel)+') '+str(field1.shape[0])+' points.\n')
    for i,x in enumerate(field1):
        dataFile.write(str(x)+' '+str(field2[i])+' '+str(field3[i])+' \n')
    dataFile.close()

def export2pgfPlotFile(fileName,fields,*kwargs):
    #pdb.set_trace()
    dataFile=open(fileName,"w")
    # 2D export
    n_fields = np.shape(fields)[0]
    n_labels = np.shape(kwargs)[0]
    if n_fields != n_labels : print n_fields-n_labels," missing in export to pgf File !"
    labels=[]
    line1 = ' # Curve ('
    line2 = ''
    for i in range(n_labels):
        labels.append(str(kwargs[i]))
        line1+=str(kwargs[i])+' ; '
        line2+=str(kwargs[i])+' '
        if i==n_labels-1 :
            line1+=str(np.shape(fields)[1])+' points.)\n'
            line2+=' \n'
        
    dataFile.write(line1)
    dataFile.write(line2)
    for i,x in enumerate(fields[0,:]):
        dataFile.write(str(x))
        for j in range(n_fields-1):
            dataFile.write(' '+str(fields[j+1,i]))
        dataFile.write(' \n')
    dataFile.close()
    
def tangentModulus(sigma,lamb,mu,beta,tangent):
    H=np.zeros((3,3))
    #    |H1111 H1112 H1122|
    # H =|H1211 H1212 H1222|
    #    |H2211 H2212 H2222|
    # sigma = [sig11 , sig12 , sig22 , sig33 ]
    sigDev = computeDeviatoricPart(sigma)
    sigdnorm2=np.dot(sigDev.T,sigDev)
    BETA=beta/sigdnorm2
    s11=sigDev[0];s12=sigDev[1]/np.sqrt(2.);s22=sigDev[2];s33=sigDev[3]
    
    ## Plane stress tangent modulus Hijkl = Hijkl - Hij33*H33kl/H3333
    H1133=(lamb -BETA*s11*s33)
    H1233=(-BETA*s12*s33)
    H1122=(lamb -BETA*s11*s22)
    H2222=(lamb+2.*mu -BETA*s22**2)
    H1222=(-BETA*s12*s22)
    H2233=(lamb-BETA*s22*s33)
    H3333=(lamb+2.*mu-BETA*s33*s33)
    if tangent=='planeStress':
        H[0,0]=lamb+2.*mu - BETA*s11**2 -H1133*H1133/H3333
        H[0,1]=-BETA*s11*s12 -H1133*H1233/H3333
        H[0,2]=lamb-BETA*s11*s22 -H1133*H2233/H3333
        H[1,0]=-BETA*s12*s11-H1233*H1133/H3333
        H[1,1]=mu-BETA*s12**2 -H1233*H1233/H3333
        H[1,2]=-BETA*s12*s22-H1233*H2233/H3333
        H[2,0]=lamb - BETA*s11*s22 -H2233*H1133/H3333
        H[2,1]=-BETA*s22*s12 -H2233*H1233/H3333
        H[2,2]=lamb+2.*mu-BETA*s22**2 -H2233*H2233/H3333
    elif tangent=='thinWalled':
        H[0,0]=lamb+2.*mu - BETA*s11**2 -H1122*(H1122+H1133)/(H2233+H2222)
        H[0,1]=-BETA*s11*s12  -H1222*(H1122+H1133)/(H2233+H2222)
        H[0,2]=lamb-BETA*s11*s22 
        H[1,0]=-BETA*s12*s11-H1122*(H1222+H1233)/(H2233+H2222)
        H[1,1]=mu-BETA*s12**2-H1222*(H1222+H1233)/(H2233+H2222)
        H[1,2]=-BETA*s12*s22
        H[2,0]=lamb - BETA*s11*s22 
        H[2,1]=-BETA*s22*s12
        H[2,2]=lamb+2.*mu-BETA*s22**2
    else :
        H[0,0]=lamb+2.*mu - BETA*s11**2 
        H[0,1]=-BETA*s11*s12
        H[0,2]=lamb-BETA*s11*s12
        H[1,0]=-BETA*s12*s11
        H[1,1]=mu-BETA*s12**2
        H[1,2]=-BETA*s12*s22
        H[2,0]=lamb-BETA*s11*s22
        H[2,1]=-BETA*s12*s22
        H[2,2]=lamb+2.*mu-BETA*s22**2
        
    return H

def acousticTensor(H,n):
    n1=n[0] ; n2=n[1]
    C11 = H[0,0]*n1**2 + H[1,1]*n2**2 + 2.*H[0,1]*n1*n2
    C12 = H[0,1]*n1**2 + H[1,2]*n2**2 + (H[0,2]+H[1,1])*n1*n2
    C22 = H[1,1]*n1**2 + H[2,2]*n2**2 + 2.*H[2,1]*n1*n2
    return np.array([C11,C12,C22])


def acousticEigenStructure(C):
    C11=C[0];C12=C[1];C22=C[2]
    ## omega1,w1 associated to cf
    ## omega2,w2 associated to cs
    omega1=0.5*(C11+C22 + np.sqrt((C11-C22)**2+4.*C12**2))
    omega2=0.5*(C11+C22 - np.sqrt((C11-C22)**2+4.*C12**2))
    w1=np.array([-C12,C11-omega1])
    w2=np.array([-C12,C11-omega2])
    return [omega1,w1],[omega2,w2]

def vonMisesYieldSurface(sigy):
    radius=np.sqrt((2./3.)*sigy**2)
    theta=np.linspace(0,2*np.pi,50)
    s2 = radius*np.cos(theta)
    s3 = radius*np.sin(theta)
    s1=0.
    c=np.sqrt(2.)/2.;
    s=np.sqrt(2.)/2.;
    P2=np.array([[c,-c,0.],[c,c,0.],[0.,0.,1.]])
    P1=np.array([[c,0.,-c],[0.,1.,0.],[c,0.,c]])
    c=np.cos(np.arctan(1./np.sqrt(2.0)))
    s=np.sin(np.arctan(1./np.sqrt(2.0)))
    P1=np.array([[c,0.,-s],[0.,1.,0.],[s,0.,c]])
    cylindre=np.zeros((3,len(s2)))

    for i in range(len(s2)):
        cylindre[:,i] = np.dot(P2,np.dot(P1,np.array([s1,s2[i],s3[i]])))
    return cylindre

def computeDeviatoricPart(T):
    # T = [T11 T21 T22 T33]
    Pdev=np.array([[1.-1/3.,0.,-1./3.,-1./3.],[0.,1.,0.,0.],[-1./3.,0.,1.-1./3.,-1./3.],[-1./3.,0.,-1./3.,1.-1./3.]])
    Tdev=np.dot(Pdev,T)
    return np.array([Tdev[0],np.sqrt(2.)*Tdev[1],Tdev[2],Tdev[3]])

def computeCriterion(sig11,sig22,sig12,sig33,sigy):
    # deviatoric stress
    sDev=computeDeviatoricPart(np.array([sig11,sig12,sig22,sig33]))
    normSDev=np.sqrt(np.dot(sDev,sDev))
    f=np.sqrt(3./2.)*normSDev - sigy
    return f

def computePsiFast(sig12,sigma,sig33,lamb,mu,beta,tangent):
    # sig12 driven
    n1=1.;n2=0.
    sig11=sigma[0];sig22=sigma[1]
    H=tangentModulus(np.array([sig11,sig12,sig22,sig33]),lamb,mu,beta,tangent)
    C=acousticTensor(H,np.array([n1,n2]))
    eigenf,eigens=acousticEigenStructure(C)
    alpha11= (H[0,1]*n1+H[1,1]*n2)*(H[1,2]*n1+H[2,2]*n2) - (H[0,2]*n1+H[1,2]*n2)*(H[1,1]*n1+H[1,2]*n2)
    alpha12=((H[0,1]*n1+H[0,2]*n2)*(H[0,2]*n1+H[1,2]*n2) - (H[0,0]*n1+H[0,1]*n2)*(H[1,2]*n1+H[2,2]*n2))/2.
    alpha22= (H[0,0]*n1+H[0,1]*n2)*(H[1,1]*n1+H[1,2]*n2) - (H[0,1]*n1+H[0,2]*n2)*(H[0,1]*n1+H[1,1]*n2)
    w1=eigens[1][0];w2=eigens[1][1]
    psi11=-w2/(1.*w1)
    psi22=(w2*alpha11/(1.*w1)-alpha12)/alpha22
    return np.array([psi11,psi22])

def computeSpeed(sigma,lamb,mu,beta,tangent):
    # sig12 driven
    n1=1.;n2=0.
    sig11=sigma[0,0];sig22=sigma[1,1];sig12=sigma[0,1];sig33=sigma[2,2]
    H=tangentModulus(np.array([sig11,sig12,sig22,sig33]),lamb,mu,beta,tangent)
    C=acousticTensor(H,np.array([n1,n2]))
    eigenf,eigens=acousticEigenStructure(C)
    return eigenf[0]

## Modify it by integrating for sig11 sig22 p and the yield surface
def integrateODE(dtau,sig0,tau0,sig22_0,sig33,lamb,mu,beta,tangent):
    sigma=np.array([sig0,sig22_0])
    # computePsiSlow(sig12,sigma,sig33,lamb,mu,beta,tangent)
    # subdivision of time step
    sub_steps = 1
    dTAU = dtau/sub_steps
    theta = 1.0
    for i in range(sub_steps):
        ## Nonlinear solution procedure
        ## R = s^{n+1} - s^{n} - RHS
        R=lambda x: x - sigma - dTAU*(theta*computePsiFast(tau0+dTAU,x,sig33,lamb,mu,beta,tangent)+(1.0-theta)*computePsiFast(tau0,sigma,sig33,lamb,mu,beta,tangent))
        #pdb.set_trace()
        solution = scipy.optimize.root(R,sigma).x
        sigma = solution
    return solution

######################## Full integration
def loadingPath(tau0,dTau,sigma0,sig33,plast,lamb,mu,beta,tangent,H,sigy):
    dsigma = computePsiFast(tau0,sigma0,sig33,lamb,mu,beta,tangent)
    sigma = np.array([sigma0[0],np.sqrt(2.)*tau0,sigma0[1],0.])
    sigman = np.array([sigma0[0]+dsigma[0],np.sqrt(2.)*(tau0+dTau),sigma0[1]+dsigma[1],0.])

    dp = updateEquivalentPlasticStrain(sigma,sigman,H)
    ## plastic residual
    sigDev=computeDeviatoricPart(np.array([sigma[0],sigma[1]/np.sqrt(2.),sigma[2],sigma[3]]))
    sigDevn=computeDeviatoricPart(np.array([sigman[0],sigman[1]/np.sqrt(2.),sigman[2],sigman[3]]))
    norm=np.sqrt(np.dot(sigDevn,sigDevn))
    flow=sigDevn/norm
    #dSig=sign-sig
    dSig=sigDevn-sigDev
    df = np.dot(flow,dSig) + H*dp
    return np.array([dsigma[0],dsigma[1],df])

def integrateFullODE(iteration,dtau,sig0,tau0,sig22_0,sig33,plast,lamb,mu,beta,tangent,H,sigy):
    crit = computeCriterion(sig0,sig22_0,tau0,sig33,sigy) - H*plast
    sigma=np.array([sig0,sig22_0,crit])
    # computePsiSlow(sig12,sigma,sig33,lamb,mu,beta,tangent)
    # subdivision of time step
    if iteration<2:
        sub_steps = 10
    else:
        sub_steps =1
    dTAU = dtau/sub_steps
    theta = 1.
    for i in range(sub_steps):
        ## Nonlinear solution procedure
        ## R = s^{n+1} - s^{n} - RHS
        # updateEquivalentPlasticStrain(sigma,sigman,H)
        R=lambda x: x - sigma - dTAU*(theta*loadingPath(tau0+dTAU,dTAU,x,sig33,plast,lamb,mu,beta,tangent,H,sigy)+(1.0-theta)*loadingPath(tau0,dTAU,sigma,sig33,plast,lamb,mu,beta,tangent,H,sigy))
        #pdb.set_trace()
        solution = scipy.optimize.root(R,sigma).x
        sigma = solution
    #print solution[2]
    return solution[0:2]

def computePsiFastSig(sig11,sigma,sig33,lamb,mu,beta,tangent):
    # sig12 driven
    n1=1.;n2=0.
    sig12=sigma[0];sig22=sigma[1]
    H=tangentModulus(np.array([sig11,sig12,sig22,sig33]),lamb,mu,beta,tangent)
    C=acousticTensor(H,np.array([n1,n2]))
    eigenf,eigens=acousticEigenStructure(C)
    alpha11= (H[0,1]*n1+H[1,1]*n2)*(H[1,2]*n1+H[2,2]*n2) - (H[0,2]*n1+H[1,2]*n2)*(H[1,1]*n1+H[1,2]*n2)
    alpha12=((H[0,1]*n1+H[0,2]*n2)*(H[0,2]*n1+H[1,2]*n2) - (H[0,0]*n1+H[0,1]*n2)*(H[1,2]*n1+H[2,2]*n2))/2.
    alpha22= (H[0,0]*n1+H[0,1]*n2)*(H[1,1]*n1+H[1,2]*n2) - (H[0,1]*n1+H[0,2]*n2)*(H[0,1]*n1+H[1,1]*n2)
    w1=eigens[1][0];w2=eigens[1][1]
    sDev=computeDeviatoricPart(np.array([sig11,sig12,sig22,sig33]))
    if w1==0. and w2==0.:
        pdb.set_trace()
    psi12=-w1/w2
    psi22=(w1*alpha12/w2-alpha11)/alpha22
    #pdb.set_trace()
    return np.array([psi12,psi22])

def integrateODE_sigdriven(dsig,sig0,tau0,sig22_0,sig33,lamb,mu,beta,tangent):
    sigma=np.array([tau0,sig22_0])
    # computePsiSlow(sig12,sigma,sig33,lamb,mu,beta,tangent)
    # subdivision of time step
    sub_steps = 1
    dSIG = dsig/sub_steps
    theta = 0.5
    for i in range(sub_steps):
        ## Nonlinear solution procedure
        ## R = s^{n+1} - s^{n} - RHS
        R=lambda x: x - sigma - dSIG*(theta*computePsiFastSig(sig0+dSIG,x,sig33,lamb,mu,beta,tangent)+(1.0-theta)*computePsiFastSig(sig0,sigma,sig33,lamb,mu,beta,tangent))
        #pdb.set_trace()
        solution = scipy.optimize.fsolve(R,sigma)
        sigma = solution
    return solution


def computeLodeAngle(sig11,sig22,sig12,sig33):
    # deviatoric stress
    sDev=computeDeviatoricPart(np.array([sig11,sig12,sig22,sig33]))
    s11=sDev[0];s12=sDev[1]/np.sqrt(2.);s22=sDev[2];s33=sDev[3]
    sig=computeEigenStresses(np.matrix([[s11,s12,0.],[s12,s22,0.],[0.,0.,s33]]))
    # deviator 2nd and 3rd invariants
    J3=s33*(s11*s22-s12**2) ; sqrtJ2=np.sqrt(0.5*np.dot(sDev,sDev))
    sqrtJ2=np.sqrt(np.dot(sDev,sDev))
    #tan=(1./np.sqrt(3.))*(2.*(sig[1]-sig[2])/(sig[0]-sig[2])-1.)
    #theta=-np.sign(tan)*np.arccos((3./2.)*np.sqrt(3.)*J3/(sqrtJ2**3))/3.
    #theta=theta*360./(2.*np.pi)
    theta=9.*np.sqrt(2./3.)*J3/(sqrtJ2**3)
    return theta

def updateEquivalentPlasticStrain(sig,sign,H):
    # sig=[sig11^n , sqrt(2)*sig12^n , sig22 , sig33^n]
    # sign=[sig11^n+1 , sqrt(2)*sig12^n+1 , sig22 , sig33^n+1]
    sigDev=computeDeviatoricPart(np.array([sig[0],sig[1]/np.sqrt(2.),sig[2],sig[3]]))
    sigDevn=computeDeviatoricPart(np.array([sign[0],sign[1]/np.sqrt(2.),sign[2],sign[3]]))
    norm=np.sqrt(np.dot(sigDevn,sigDevn))
    flow=sigDevn/norm
    #dSig=sign-sig
    dSig=sigDevn-sigDev
    dp=(1./H)*np.sqrt(3./2.)*np.dot(flow,dSig)
    return dp

def computeEigenStresses(sig):
    #    | sig11 sig12   0   |
    #sig=| sig12 sig22   0   |
    #    |   0     0   sig33 |
    s3=sig[2,2]
    delta=(sig[0,0]-sig[1,1])**2+4.*sig[0,1]**2
    s1=0.5*(sig[0,0]+sig[1,1]-np.sqrt(delta))
    s2=0.5*(sig[0,0]+sig[1,1]+np.sqrt(delta))
    return np.array([s1,s2,s3])

from mpl_toolkits.mplot3d import proj3d
def orthogonal_proj(zfront, zback):
    a = (zfront+zback)/(zfront-zback)
    b = -2*(zfront*zback)/(zfront-zback)
    return np.array([[1,0,0,0],
                        [0,1,0,0],
                        [0,0,a,b],
                        [0,0,0,zback]])
proj3d.persp_transformation = orthogonal_proj

Samples=6

## Setting initial values
# admissible range for sigma11
sig=np.linspace(-np.sqrt(4./3.)*sigy,np.sqrt(4./3.)*sigy,Samples)
# corresponding values of sig22 through elastic characteristics
sig22=sig*mu/(2.*(mu+lamb))
# associated value of sigma12
delta=(sig*sig22 -sig**2-sig22**2 + sigy**2)/3.
tau=np.sqrt(delta)

#col=["r","g","b","y","c","m","k","p"]
tauM=1.5*sigy/np.sqrt(3.)
sigM=1.5*sigy/np.sqrt(1-nu+nu**2)
tauM=0.*sigy#sigM
Niter=150
TAU=np.zeros((Niter,Samples))
SIG11=np.zeros((Niter,Samples))
SIG22=np.zeros((Niter,Samples))
eigsigS=np.zeros((Niter,Samples,3))
criterionF=np.zeros((Niter,Samples))
PsiS=np.zeros((Samples))

plast_F=np.zeros((Niter,Samples))
LodeAngle_F=np.zeros((Niter,Samples))
rcf2=np.zeros((Niter,Samples))
# Boolean to plot the upadted yield surface
updated_criterion=False
## LOADING PATHS PLOTS
pgfFilesList=[]
yields11_s12=[]
yields22_s12=[]
deviatorPlots=[]

fig = plt.figure()
ax3=plt.subplot2grid((1,1),(0,0),projection='3d')

cylindre=vonMisesYieldSurface(sigy)
ax3.plot(cylindre[0,:],cylindre[1,:],cylindre[2,:], color="k")
elevation_Angle_radian=np.arctan(1./np.sqrt(2.0))
angle_degree= 180.*elevation_Angle_radian/np.pi
radius=1.*np.sqrt((2./3.)*sigy**2)
ax3.set_xlim(-1.*radius,1.*radius)
ax3.set_ylim(-1.*radius,1.*radius)
ax3.set_zlim(-1.*radius,1.*radius)
ax3.view_init(angle_degree,45.)
ax3.plot([0.,sigy],[0.,sigy],[0.,sigy],color="k")
ax3.set_xlabel(r'$\sigma_1$',size=24.)
ax3.set_ylabel(r'$\sigma_2$',size=24.)
ax3.set_zlabel(r'$\sigma_3$',size=24.)
    
fig = plt.figure()
ax1=plt.subplot2grid((1,2),(0,0))
ax2=plt.subplot2grid((1,2),(0,1))
ax1.set_xlabel(r'$\sigma_{11}$',size=28.)
#ax1.set_ylabel(r'$\sigma_{12}$',size=28.)
ax2.set_xlabel(r'$\sigma_{22}$',size=28.)
#ax2.set_ylabel(r'$\sigma_{12}$',size=28.)
ax1.grid()
ax2.grid()

tangent='planeStress'
## LOADING PATHS PLOTS
for k in range(len(sig22))[1:-1]:
    
    s22=sig22[k]
    tauM=0.
    
    sig0=sig[k]
    tau0=tau[k]

    tauM = 0.
    dtau=(tauM-tau0)/Niter
    print "sig22=",s22,", sig11=",sig0,", tau=",tau0
    print "initial yield function ", computeCriterion(sig0,s22,tau0,0.,sigy)
    
    TAU[:,k]=np.linspace(tau0,tauM,Niter)
    
    SIG11[0,k]=sig0
    SIG22[0,k]=s22
    
    
    sigma = np.matrix([[SIG11[0,k],TAU[0,k],0.],[TAU[0,k],SIG22[0,k],0.],[0.,0.,0.]])
    rcf2[0,k] = np.sqrt(computeSpeed(sigma,lamb,mu,beta,tangent)/rho)
    eigsigS[0,k,:]=computeEigenStresses(sigma)
    LodeAngle_F[0,k]=computeLodeAngle(sigma[0,0],SIG22[0,k],sigma[0,1],0.)
    
    plast=0.
    epsp33=0.
    for j in range(Niter-1):
        #SIG11[j+1,k],SIG22[j+1,k]=integrateODE(dtau,SIG11[j,k],TAU[j,k],SIG22[j,k],0.,lamb,mu,beta,tangent)
        
        SIG11[j+1,k],SIG22[j+1,k]=integrateFullODE(j,dtau,SIG11[j,k],TAU[j,k],SIG22[j,k],0.,plast,lamb,mu,beta,tangent,H,sigy)
        
        sigma = np.array([SIG11[j,k],np.sqrt(2.)*TAU[j,k],SIG22[j,k],0.])
        sigman = np.array([SIG11[j+1,k],np.sqrt(2.)*TAU[j+1,k],SIG22[j+1,k],0.])
        
        dp=updateEquivalentPlasticStrain(sigma,sigman,H)
        plast+=dp
        
        criterionF[j+1,k]=computeCriterion(SIG11[j+1,k],SIG22[j+1,k],TAU[j+1,k],0.,sigy+H*plast)
        plast_F[j+1,k]=plast
        
        LodeAngle_F[j+1,k]=computeLodeAngle(sigman[0],sigman[2],sigman[1]/np.sqrt(2.),0.)
        
        # Eigenvalues of sigma (for deviatoric plane plots)
        sigma = np.matrix([[SIG11[j+1,k],TAU[j+1,k],0.],[TAU[j+1,k],SIG22[j+1,k],0.],[0.,0.,0.]])
        rcf2[j+1,k] = np.sqrt(computeSpeed(sigma,lamb,mu,beta,tangent)/rho)
        if rcf2[j+1,k]>rcf2[j,k]:
            print "Simple wave condition violated"
        
        eigsigS[j+1,k,:]=computeEigenStresses(sigma)
        
        Nfinal=Niter
        if rcf2[j+1,k]>rcf2[j,k]:
            print "Simple wave condition violated"
            Nfinal=j
            break
    
    print "Final equivalent plastic strain after fast wave: ",plast
    print "Final value of the shear stress: ",TAU[j+1,k]
    fileName=path+'CPfastStressPlane_Stress'+str(k)+'.pgf'
    # if Nfinal/100>5:
    #     pas=Nfinal/100
    # else:
    #     pas=2
    if Nfinal/100>1:
        pas=Nfinal/100
        ranging=np.linspace(0,Nfinal-1,Nfinal/100,True,False,np.int)
    else:
        pas=1
        ranging=np.linspace(0,Nfinal-1,Nfinal,True,False,np.int)
    ## color bar of rcf2
    export2pgfPlotFile(fileName,np.array([TAU[ranging,k],SIG11[ranging,k],SIG22[ranging,k],rcf2[ranging,k],LodeAngle_F[ranging,k]]),'sigma_12','sigma_11','sigma_22','p','Theta')
    pgfFilesList.append(fileName)
    fileName=path+'CPfastDevPlane_Stress'+str(k)+'.pgf'
    dico={"xlabel":r'$s_1$',"ylabel":r'$s_2$',"zlabel":r'$s_3$'}
    export2pgfPlot3D(fileName,eigsigS[ranging,k,0],eigsigS[ranging,k,1],eigsigS[ranging,k,2],dico)
    deviatorPlots.append(fileName)
    
    
    #### PLOTTING THE RESULTS
    cylindre=vonMisesYieldSurface(sigy)
    fileName=path+'CPCylindreDevPlane.pgf'
    export2pgfPlot3D(str(fileName),cylindre[0,:],cylindre[1,:],cylindre[2,:])
    deviatorPlots.append(fileName)
    
    ### SUBPLOTS SETTINGS
    ax3.plot(eigsigS[:,k,0],eigsigS[:,k,1],eigsigS[:,k,2],lw=1.5)
    ax3.plot([-sigy,sigy],[0.,0.],[0.,0.],color="k",linestyle="--",lw=1.)
    ax3.plot([0.,0.],[-sigy,sigy],[0.,0.],color="k",linestyle="--",lw=1.)
    ax3.plot([-radius,radius],[radius,-radius],[0.,0.],color="k",linestyle="--",lw=1.)
    plt.tight_layout()
    #plt.show()

    
    # ax1.plot(SIG11[:,k],TAU[:,k])
    # ax2.plot(SIG22[:,k],TAU[:,k])
    ax1.set_xlabel(r'$p$',size=28.)
    ax2.set_xlabel(r'$cos(3\Theta)$',size=28.)
    norm_vm = criterionF[:,k]+sigy+H*plast_F[:,k]
    press = (1./3.)*(eigsigS[:,k,0]+eigsigS[:,k,1]+eigsigS[:,k,2])
    triax = np.sqrt(1/3.)*press/norm_vm
    det = (eigsigS[:,k,0]*eigsigS[:,k,1]*eigsigS[:,k,2])
    ax1.plot(np.arange(0,len(press),1),det)
    ax2.plot(LodeAngle_F[:,k],2.*SIG22[:,k]/SIG11[:,k],linestyle='-.')
    #ax2.plot(np.arange(0,len(triax),1),triax,linestyle='-.')
    #ax4.plot(SIG22[:,k],LodeAngle_F[:,k],linestyle='--')

    ## sig22 value will change here
    xlabels=['$\sigma_{11} $','$\sigma_{22} $','$s_1 $'] #size=number of .tex files
    ylabels=['$\sigma_{12} $','$\sigma_{12} $','$s_2 $'] #size=number of .tex files
    zlabels=['','','$s_3$'] #size=number of .tex files


    subtitle=[r'(a) ($\sigma_{11},\sigma_{12}$) plane',r'(b) ($\sigma_{22},\sigma_{12}$) plane',r'(c) Deviatoric plane']

    srcX=['sigma_11','sigma_22']
    srcY=['sigma_12','sigma_12']

    name1='CPfastWaves_sig11_tau'+str(k)+'.tex'
    name2='CPfastWaves_sig22_tau'+str(k)+'.tex'
    name3='CPfastWaves_deviator'+str(k)+'.tex'
    names=[name1,name2,name3]
    
    files1=np.concatenate([pgfFilesList,yields11_s12])
    #files2=np.concatenate([pgfFilesList,yields22_s12])
    files2=pgfFilesList
    pgfFiles=[files1,files2,deviatorPlots]
    #buildTeXFiles(names,pgfFiles,xlabels,ylabels,zlabels,subtitle,srcX,srcY)
    names=[[name1,name2],name3]
    pgfFiles=[[files1,files2],deviatorPlots]
    xlabels=[['$\sigma_{11} (Pa)$','$\sigma_{22}  (Pa)$'],'$s_1 $'] #size=number of .tex files
    ylabels=[['$\sigma_{12}  (Pa)$','$\sigma_{12}  (Pa)$'],'$s_2 $'] #size=number of .tex files
    zlabels=[['',''],'$s_3$'] #size=number of .tex files

    TauMax=1.1*np.max(TAU[ranging,k])
    buildTeXFiles2(names,pgfFiles,xlabels,ylabels,zlabels,srcX,srcY,TauMax)
    
    pgfFilesList=[];yields11_s12=[];
plt.show()
    
