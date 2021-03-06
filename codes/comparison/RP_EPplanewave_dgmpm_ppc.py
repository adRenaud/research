#!/usr/bin/pyton

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import pdb
import os
from ExactplaneWaveKin import *

directory=os.path.basename(__file__)[:-3]

if not os.path.exists('texFiles/'+str(directory)):
    os.system('mkdir texFiles/'+str(directory))
path='texFiles/'+str(directory)
"""
Comparison of DGMPM implementations of the 1D elastic-plastic set of equations
in dynamics for linear kinematic hardening materials
"""
def export2DTeXFile(fileName,xFields,xlabel,ylabel,subtitle,yfields,*kwargs):
    TeXFile=open(fileName,"w")
    n_fields = np.shape(yfields)[0]
    n_labels = np.shape(kwargs)[0]
    # Define Paul Tol's colors (purple to red)
    ## 5 fields
    marker=['none','none','none','|','x','none','pentagone*','none','triangle*']
    style=['dashed','dotted','solid','solid','only marks','solid','solid','solid']
    thickness=['very thick','very thick','very thick','thick','thick','thin','very thick','thin','thick']
    couleur=['Red','Orange','Blue','Purple','Green','black','Yellow','black','Green']
    TeXFile.write(r'\begin{tikzpicture}[scale=0.8]');TeXFile.write('\n')
    TeXFile.write(r'\begin{axis}[xlabel='+str(xlabel)+',ylabel='+str(ylabel)+',ymajorgrids=true,xmajorgrids=true,legend pos=outer north east,title={'+subtitle+'},xmin=0.,xmax=6.]');TeXFile.write('\n')
    legend=''
    for i in range(n_fields):
        if i==0:
            legend=legend+kwargs[0][i]
        else:
            legend=legend+','+kwargs[0][i]
        TeXFile.write(r'\addplot['+str(couleur[i])+','+str(thickness[i])+',mark='+str(marker[i])+','+str(style[i])+'] coordinates {')
        for j in range(np.shape(yfields[i])[0]):
            TeXFile.write('('+str(xFields[i][j])+','+str(yfields[i][j])+') ')
        TeXFile.write('};\n')
    if subtitle[:3]=='(c)':
        TeXFile.write(r'\legend{'+str(legend)+'}')
    else:
        TeXFile.write(r'%\legend{'+str(legend)+'}')
    TeXFile.write('\n')    
    TeXFile.write(r'\end{axis}')
    TeXFile.write('\n')
    TeXFile.write('\end{tikzpicture}')
    TeXFile.write('\n')
    TeXFile.write('%%% Local Variables:')
    TeXFile.write('\n')
    TeXFile.write('%%% mode: latex')
    TeXFile.write('\n')
    TeXFile.write('%%% TeX-master: "../../mainManuscript"')
    TeXFile.write('\n')
    TeXFile.write('%%% End:')
    TeXFile.write('\n')
    TeXFile.close()

def export2DGroupplot(fileName,containers,rowFields,colFields,titles,Ylabels,legend,*kwargs):
    row=len(rowFields)
    col=len(colFields)
    fields_in_plots=len(containers)
    marker=['none','+','x','none','triangle*','none']
    style=['solid','only marks','only marks','solid','dotted']
    thickness=['very thick','thin','thick','thin','very thick','thin','thick','very thick']
    couleur=['Blue','Purple','Duck','black','Yellow','black','Green','Orange']

    TeXFile=open(fileName,"w")
    # Define Paul Tol's colors (purple to red)
    TeXFile.write(r'\begin{tikzpicture}[scale=.9]');TeXFile.write('\n')
    TeXFile.write(r'\begin{groupplot}[group style={group size='+str(col)+' by '+str(row)+',');TeXFile.write('\n')
    TeXFile.write('ylabels at=edge left, yticklabels at=edge left,horizontal sep=2.ex,');TeXFile.write('\n')
    TeXFile.write('vertical sep=4ex,xticklabels at=edge bottom,xlabels at=edge bottom},');TeXFile.write('\n')
    if row==1:
        TeXFile.write(r'ymajorgrids=true,xmajorgrids=true,enlargelimits=0,xmin=0.,xmax=6.,'+str(Ylabels)+',xlabel=x (m),');TeXFile.write('\n')
    else:
        TeXFile.write(r'ymajorgrids=true,xmajorgrids=true,enlargelimits=0,xmin=0.,xmax=6.,xlabel=$x (m)$,');TeXFile.write('\n')
    TeXFile.write('axis on top,scale only axis,width=0.32\linewidth');TeXFile.write('\n')
    TeXFile.write(']');TeXFile.write('\n')
    for i,field in enumerate(rowFields): ## sum over rows
        for j in range(col):
            TeXFile.write(r'\nextgroupplot[')
            if i==0: TeXFile.write(r'title={'+str(titles[j])+'},')
            if j==0: TeXFile.write(r'ylabel='+str(Ylabels[i])+',')
            if j==col-1 and i==row-1: TeXFile.write(r'legend style={at={($(0.3,-0.45)+(0.cm,1cm)$)},legend columns=2}')
            TeXFile.write(']');TeXFile.write('\n')
            for k in range(fields_in_plots):
                TeXFile.write(r'\addplot['+str(couleur[k])+','+str(style[k])+',mark='+str(marker[k])+','+thickness[k]+',mark size=2pt] coordinates{')
                #pdb.set_trace()
                #print field
                FIELD=containers[k][field][:,colFields[j][k]]
                xFields=containers[k]["pos"][:,colFields[j][k]]
                for l in range(len(FIELD)):
                    TeXFile.write('('+str(xFields[l])+','+str(FIELD[l])+') ')
                TeXFile.write('};\n')
    for lab in legend:
        TeXFile.write(r'\addlegendentry{'+str(lab)+'}');TeXFile.write('\n')
    TeXFile.write('\n')    
    TeXFile.write(r'\end{groupplot}')
    TeXFile.write('\n')
    TeXFile.write('\end{tikzpicture}')
    TeXFile.write('\n')
    TeXFile.write('%%% Local Variables:')
    TeXFile.write('\n')
    TeXFile.write('%%% mode: latex')
    TeXFile.write('\n')
    TeXFile.write('%%% TeX-master: "../../mainManuscript"')
    TeXFile.write('\n')
    TeXFile.write('%%% End:')
    TeXFile.write('\n')
    TeXFile.close()
    
def export2pgfPlot(fileName,xfield,yfield,xlabel,ylabel):
    #pdb.set_trace()
    dataFile=open(fileName,"w")
    dataFile.write('# Curve ('+str(xlabel)+';'+str(ylabel)+') '+str(len(xfield))+' points.\n')
    for i,x in enumerate(xfield):
        dataFile.write(str(x)+' '+str(yfield[i])+' i\n')
    dataFile.close()

###Opening the files and computation of the solution by each method
###Parameters####
CFL=0.5
NTmaxi = 300
length = 6.0
ppc=1
Nelem = 50
E = 2.0e11
nu=0.3
lamb=E*nu/((1.+nu)*(1.-2.*nu))
mu=0.5*E/(1.+nu)
Sigy = 400.0e6
H = 10e9
rho = 7800.0
HEL = ((lamb+2.0*mu)/(2.0*mu))*Sigy
c=np.sqrt((lamb+2.*mu)/rho)
sigd =0.
v0=2.*HEL/(rho*c)
factor=1.
timeOut = 1.*length/c
t_order=1
timeUnload = 2*timeOut
algo = 'USL'
update_position=False
mpm_mapping=True
limit=-1
hardening='kinematic'
fvmlimiter=-1

parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":t_order,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}
#################

##MPM: Material Point Method
USL = dict(parameters)
print 'Computing  USF'
#execfile('mpm/planeWave.py', USL)

parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":'USF',"t_order":t_order,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}
#################

##MPM: Material Point Method
USF = dict(parameters)
print 'Computing  USF'
#execfile('mpm/planeWave.py', USF)
ppc=2
#Nelem = 50/ppc
parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":t_order,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}

print "=============== 2PPC COMPUTATIONS ===================="

##DGMPM: Discontinuous Galerkin Material Point Method
DGMPM2 = dict(parameters)
print 'Computing  DGMPM (ep solver)'
execfile('dgmpm/planeWaveEP_EPsolver.py', DGMPM2)




parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":2,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}

print "=============== 2PPC COMPUTATIONS ===================="

##DGMPM: Discontinuous Galerkin Material Point Method
DGMPM3 = dict(parameters)
print 'Computing  DGMPM (ep solver)'
execfile('dgmpm/planeWaveEP_EPsolver.py', DGMPM3)

# frames=[]
# frmpm=[]
# for i in DGMPM2["time"]:
#     for j in DGMPM["time"]:
#         if abs(i-j)<5.e-7:
#             ndg = np.where(DGMPM["time"]==j)[0][0]
#             nmpm = np.where(DGMPM2["time"]==i)[0][0]
#             print nmpm
#             tdg = '%.2e' % j ; tmpm = '%.2e' % i
#             print "dgmpm increment ",ndg, " ; time difference: ",'%.2e' %abs(j-i)
#             print "mpm time: ",tmpm," ; dgmpm time:",tdg
#             frames.append(ndg)
#             frmpm.append(nmpm)
# print frames
# start=3
=======

ppc=2
parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":t_order,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}
#################

##MPM: Material Point Method
USL2 = dict(parameters)
print 'Computing  USL (2ppc)'
execfile('mpm/planeWave.py', USL2)


##DGMPM: Discontinuous Galerkin Material Point Method
DGMPM2 = dict(parameters)
print 'Computing  DGMPM (ep solver 2ppc)'
execfile('dgmpm/planeWaveEP_EPsolver.py', DGMPM2)


parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":2,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}

##DGMPM: Discontinuous Galerkin Material Point Method
DGMPM3 = dict(parameters)
print 'Computing  DGMPM (ep solver 2ppc + RK2)'
execfile('dgmpm/planeWaveEP_EPsolver.py', DGMPM3)


ppc=8
parameters = {"CFL":CFL,"Nelem":Nelem,"NTmaxi":NTmaxi,"ppc":ppc,"length":length,"Young":E,"nu":nu,"Sigy":Sigy, "H":H,"rho":rho,"sigd":sigd,"timeOut":timeOut,"timeUnload":timeUnload,"update_position":update_position,"v0":v0,"factor":factor,"algo":algo,"t_order":t_order,"limit":limit,"mpm_mapping":mpm_mapping,"compute_CFL":False,"hardening":hardening,"fvmlimiter":fvmlimiter}
#################

##MPM: Material Point Method
USL3 = dict(parameters)
print 'Computing  USL (8ppc)'
execfile('mpm/planeWave.py', USL3)

>>>>>>> a8f9c4507db8470149558797c903f9e42890b458
#############################################################################
#########################  Comparison  ######################################
#############################################################################

####Animated plot ###########################################################
from matplotlib import rcParams
rcParams['axes.labelsize'] = 16
rcParams['xtick.labelsize'] = 16
rcParams['ytick.labelsize'] = 16
rcParams['legend.fontsize'] = 16


subtitles=['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)']
frames=[45,65,95]
frames=[20,30,45]
titles=[]
sig_th=np.zeros((len(DGMPM["pos"][:,0]),len(frames)))
epsp_th=np.zeros((len(DGMPM["pos"][:,0]),len(frames)))

for i,n1 in enumerate(frames):
    mpm=2*n1-1#frmpm[start+i]
    print n1,mpm,mpm/2+1
    time = '%.2e' % DGMPM["time"][n1]
    fig, (ax1, ax2) = plt.subplots(2,1)
    if DGMPM["time"][n1]<=0.5*length/c :
        temps=DGMPM["time"][n1]
    else:
        temps=DGMPM["time"][n1-1]
    
    if hardening=='isotropic':
        Sexact,Epexact,Vexact = computeAnalyticalSolutionISO(DGMPM["pos"][:,n1],length,c,temps,abs(v0),HEL,lamb,mu,H,rho)
    elif hardening=='kinematic':
        Sexact,Epexact,Vexact = computeAnalyticalSolutionKIN(DGMPM["pos"][:,n1],length,c,temps,abs(v0),HEL,lamb,mu,H,rho)
    sig_th[:,i]=-np.sign(v0)*Sexact
    epsp_th[:,i]=-np.sign(v0)*Epexact
    ax1.plot(DGMPM["pos"][:,n1],DGMPM["sig"][:,n1],'b',lw=2.,ms=4.,label='DGMPM 1ppc')
    ax1.plot(DGMPM2["pos"][:,mpm],DGMPM2["sig"][:,mpm],'r--',lw=2.,ms=4.,label='DGMPM 2ppc')
    ax1.plot(DGMPM3["pos"][:,mpm/2+1],DGMPM3["sig"][:,mpm/2+1],'g-',lw=2.,ms=4.,label='DGMPM RK2')
    ax1.plot(DGMPM["pos"][:,n1],-np.sign(v0)*Sexact,'k',lw=2.,ms=4.,label='exact')
    ax1.set_title('Stress at time t='+str(time)+' s.',size=24.)
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel(r'$\sigma (Pa)$')

    ax2.plot(DGMPM["pos"][:,n1],DGMPM["epsp"][:,n1],'b',lw=2.,ms=4.,label='DGMPM 1ppc')
    ax2.plot(DGMPM2["pos"][:,mpm],DGMPM2["epsp"][:,mpm],'r--',lw=2.,ms=4.,label='DGMPM 2ppc')
    ax2.plot(DGMPM3["pos"][:,mpm/2+1],DGMPM3["epsp"][:,mpm/2+1],'r--',lw=2.,ms=4.,label='DGMPM RK2')
    ax2.plot(DGMPM["pos"][:,n1],-np.sign(v0)*Epexact,'k',lw=2.,ms=4.,label='exact')
    ax2.set_title('Plastic strain at time t='+str(time)+' s.')
    ax2.set_xlabel('x (m)')
    ax2.set_ylabel(r'$\varepsilon^p (Pa)$')
    ax1.legend(numpoints=1)
    ax1.grid();ax2.grid()
    plt.show()
    legend=['usl 1ppc','dgmpm 1ppc (ep solver)','dgmpm 1ppc (ac solver)','exact']
    temps=time[:-4]
    subtitle=subtitles[i]+r' $t = '+str(temps)+r'\times 10^{-'+str(time[-1])+'} $ s.'
    titles.append(subtitle)
    #export2DTeXFile(str(path)+'/EP_dgmpm_mpm_stress'+str(n1)+'.tex',np.array([USL["pos"][:,2*n1],DGMPM["pos"][:,n1],DGMPM2["pos"][:,n1],DGMPM["pos"][:,n1]]),'$x (m)$',r'$\sigma (Pa)$',str(subtitle),np.array([USL["sig"][:,2*n1],DGMPM["sig"][:,n1],DGMPM2["sig"][:,n1],-np.sign(v0)*Sexact]),legend)
    #export2DTeXFile(str(path)+'/EP_dgmpm_mpm_epsp'+str(n1)+'.tex',np.array([USL["pos"][:,2*n1],DGMPM["pos"][:,n1],DGMPM2["pos"][:,n1],DGMPM["pos"][:,n1]]),'$x (m)$',r'$\eps^p$',str(subtitle),np.array([USL["epsp"][:,2*n1],DGMPM["epsp"][:,n1],DGMPM2["epsp"][:,n1],-np.sign(v0)*Epexact]),legend)
    #export2DTeXFile(str(path)+'/EP_dgmpm_mpm_velo'+str(n1)+'.tex',np.array([USL["pos"][:,2*n1],DGMPM["pos"][:,n1],DGMPM2["pos"][:,n1],DGMPM["pos"][:,n1]]),'$x (m)$',r'$\eps^p$',str(subtitle),np.array([USL["velo"][:,2*n1],DGMPM["Velocity"][:,n1],DGMPM2["Velocity"][:,n1],-np.sign(v0)*Vexact]),legend)

fileName=str(path)+'/ep_dgmpm_ppc.tex'
Exact=dict();Exact["pos"]=DGMPM["pos"];Exact["sig"]=sig_th;Exact["epsp"]=epsp_th
# USL["pos"][:,2*n1],DGMPM["pos"][:,n1],DGMPM2["pos"][:,n1],DGMPM["pos"][:,n1]
containers=np.array([DGMPM,DGMPM2,DGMPM3,Exact])
rowFields=['sig','epsp']
colFields=np.array([[20,39,20,0],[30,59,30,1],[45,89,45,2]])
legend=['dgmpm 1ppc','dgmpm 2ppc','dgmpm 2ppc (RK2)','exact']
Ylabels=[r'$\sigma (Pa)$',r'$\eps^p $']

export2DGroupplot(fileName,containers,rowFields,colFields,titles,Ylabels,legend)

