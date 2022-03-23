# computer module: list file data, plot data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import Series
import scipy.stats as ss
import os
import itertools  #marker, color 
from flask import json
from io import BytesIO
    
#gloal variables 
pmode = 'simple'   #true weibull algorithm is disabled.

#transfrom data for linear regression in log-log curve
def fdataX(x,pmode):
    x = x[x>0]
    x = x.dropna()
    if pmode=='simple':
    	return Series(x.values*0.001, index=x.index)
    else:
    	return Series(-np.log(1-x.values*0.001), index=x.index )

# linear regression based on log-log 
def fitcdf(x,sa,sb):
    d=[i for i in x.index if i>=sa and i<=sb]
    x2=x[d].dropna()
    logx=np.log(x2.index)
    logy=np.log(x2.values)
    z = np.polyfit(logx,logy,1)
    return z

#calculate CDF
def calcdf(x,pginfo,pmis,pmode):
    pn=x.name
    z=fitcdf(x,pginfo[pn]['minX'],pginfo[pn]['maxX'])
    k=np.arange(1,pmis+5)
    if pmode=='simple':
        pbeta=z[0]
        plambda=np.exp(z[1])
        v=plambda*np.power(k,pbeta)*1000.0
    elif pmode=='weibull':
        v=ss.exponweib.cdf(k,1.0,z[0],0,np.exp(-z[1]/z[0]))*1000
    return Series(v,index=k) 

#calculate C1000 at estimated X
def predict(x,pginfo,pmis,pmode):
     #calculate CDF
    pn=x.name
    z=fitcdf(x,pginfo[pn]['minX'],pginfo[pn]['maxX'])
    pid=pginfo[pn]['pid']
    if pmode=='simple':
        plambda=np.exp(z[1])
        pbeta=z[0]
        v=plambda*np.power(pmis,z[0])*1000
    elif pmode=='weibull':
        plambda=np.exp(-z[1]/z[0])
        pbeta=z[0]
        v=ss.exponweib.cdf(pmis,1.0,z[0],0,plambda)*1000
    return (pid,pmis,round(v,4),round(plambda,4),round(pbeta,4))


#find min and max values of dataframe 
def findMinMaxC1000(x):
    return np.array([x.min().min(),x.max().max()])
 

#read input file content (format:xlsx,csv,or txt)    
def listdata(filename=None):
    filetype = filename.rsplit('.', 1)[1]

    # find data x-y type
    if filetype == 'xlsx':
    	df_xyname = pd.read_excel(filename,header=None,index_col=None,nrows=1)
    elif filetype == 'txt':
        df_xyname = pd.read_csv(filename,header=None,index_col=None,nrows=1,sep='\t')
    elif filetype == 'csv':
        df_xyname = pd.read_csv(filename,header=None,index_col=None,nrows=1,sep='\,')
    df_xyname = df_xyname.values[0]

    # read data content	
    if filetype == 'xlsx':
        df = pd.read_excel(filename,header=0,index_col=0,skiprows=[0])
    elif filetype == 'txt':
        df = pd.read_csv(filename,header=0,index_col=0,skiprows=[0],sep='\t')
    elif filetype == 'csv':
        df = pd.read_csv(filename,header=0,index_col=0,skiprows=[0],sep=',')    

    df = df.apply(pd.to_numeric, errors='coerce')
    # for each type of data file to read datainto df
    #convert this pandas dataframe into a html table, only round(1) is displayed.
    datatable=df.round(2).to_html(na_rep='*',classes=['table  table-striped'])
    # read min,max info of each program
    program=[]
    data_min_X=10000000
    data_max_X=0
    inputEstX =0
    for k in df:
        p=df[k]
        p=p.dropna()
        p=p[p>0]
        ainx=p.index.values
        ainx=ainx[ainx>0]
        p=p[ainx]
        minX=int(p.index.min())
        maxX=int(p.index.max())
        if minX < data_min_X:
            data_min_X=minX
        if maxX > data_max_X:
            data_max_X=maxX
        pinfor={'name':p.name,'minX':minX,'maxX':maxX}
        program.append(pinfor)
    inputEstX = int(data_max_X * 1.5)
    data_name_x = df_xyname[0] # mile, mileage, year, years, month,
    xtick_max = int(data_max_X*2.0)
    if ('mis' in data_name_x.lower())| ('mop' in  data_name_x.lower() ) | ('month' in  data_name_x.lower() ):
        xtick_list = [1,2,5,10,20,36,50,100,180]
    elif 'year' in data_name_x.lower():
        xtick_list = [1,2,3,4,5,6,7,8,9,10,11,12]
    elif 'mile' in data_name_x.lower():
        xtick_list = [1000,2000,5000,10000,20000,50000,100000,150000]
        #xtick_list = [1,2,5,10,20,50,80,100,150]
    elif 'km' in data_name_x.lower():
        xtick_list = [1000,2000,5000,8000,10000,20000,50000,100000]
    xtick_arr = np.array(xtick_list)
    
    if np.amax(xtick_arr)>xtick_max:
        xtick_opt = xtick_arr[xtick_arr<=xtick_max]
    else:
        xtick_opt = np.append(xtick_arr,xtick_max)
    xtick = ','.join(str(e) for e in xtick_opt)
    
#   send back data to controler.py
    rdata={'filename':os.path.basename(filename)
    	,'filetype':filetype
    	,'datatype': df.index.name
    	,'data_x_name': df_xyname[0]
    	,'data_y_name': df_xyname[1]
    	,'datatable':datatable
    	,'programlist':list(df)
    	,'program': program
    	,'inputEstX':inputEstX
    	,'xtick':xtick

    }
    return json.dumps(rdata)

 
# (predict)+plot 
def plotdata(filename=None,param=None):
    #    	var plotfunctionparameters = {
    #		"task": task
    #		,"estX": estX
    #		,"plot": plotinfor
    #		,"program": programinfor
    #	};

    global pmode
#    plot options
    pplot = param['plot']
    title = pplot['title']
    xlabel = pplot['xlabel']
    ylabel = pplot['ylabel']
    xtick = np.array([float(x) for x in pplot['xtick'].split(',')])
    ytick = np.array([float(x) for x in pplot['ytick'].split(',')])
    titlesize = float(pplot['titlesize'])
    labelsize = float(pplot['labelsize'])
    legendposition=pplot['legendposition']
    legendsize = float(pplot['legendsize'])
    linewidth = float(pplot['linewidth'])
    markdersize = float(pplot['markdersize'])
    xtickrotation = float(pplot['xtickrotation'])

    ptask = param['task']# 0 plot fitting, 1 plot fitting
    pmis=param['estX']
    pmis=float(pmis)
    ppgm=param['program']  

    filetype = filename.rsplit('.', 1)[1]
 
    if filetype == 'xlsx':
        data = pd.read_excel(filename,header=0,index_col=0,skiprows=[0])
    elif filetype == 'txt':
        data = pd.read_csv(filename,header=0,index_col=0,skiprows=[0],sep='\t')
    elif filetype == 'csv':
        data = pd.read_csv(filename,header=0,index_col=0,skiprows=[0],sep=',')
    data = data.apply(pd.to_numeric, errors='coerce')
    
    data.columns = [str(i) for i in data.columns]
    if ptask=='plot':
        data=data[ppgm]
    else:
        for p in data.columns:
            if(ppgm[p]['selected']==0):
                data.drop(p, axis=1, inplace=True)
    data_X = data.apply(fdataX,args=(pmode,))
    calvalue={}
    if ptask=='predict': 
        data_fit = data_X.apply(calcdf,args=(ppgm,pmis,pmode,))
        data_fit_X=data_fit.apply(fdataX,args=(pmode,))
        data_predict=data_X.apply(predict,args=(ppgm,pmis,pmode,))
        for a,b in data_predict.iteritems():
            calvalue[b[0]]={'estY':b[2],'lambda':b[3],'beta':b[4]}

#    plot
    plt.clf() # clean up first
    plt.title(title, fontsize=titlesize)
    plt.tight_layout(pad=4, w_pad=4, h_pad=3)
    plt.xlabel(xlabel, fontsize=labelsize)
    plt.ylabel(ylabel, fontsize=labelsize)
    plt.xscale('log',basex=np.e)
    plt.yscale('log',basey=np.e)
    plt.grid(True)

    if ('mile' in xlabel.lower())| ('km' in  xlabel.lower() ) :
        plt.xticks(xtick, [int(i/1000) for i in xtick],rotation=xtickrotation)
        plt.xlabel(xlabel+' (x 1000)', fontsize=labelsize)
    else:
        plt.xticks(xtick, [int(i) for i in xtick],rotation=xtickrotation)    
    plt.xlim([xtick[0],xtick[-1]])


    # cal c1000 y range
    ytickV=[]
    if pmode == 'simple':
        ytickV=ytick*0.001
    elif pmode =='weibull':
        ytickV=-np.log(1.0-ytick*0.001)
    plt.yticks(ytickV,ytick)
    plt.ylim([ytickV.min(),ytickV.max()]) 
    
    if ptask == 'predict':
        if pmode == 'simple':
            ylimv=findMinMaxC1000(data)
        elif pmode =='weibull':
            ylimv=findMinMaxC1000(data_fit)
        
        if ylimv.min()<=ytickV.min():  
            ylimvmin=ylimv.min()             
        else:
            ylimvmin=ytickV.min()
        plt.plot([pmis,pmis],[ytickV[0],ytickV[-1]],ls='-',lw=1,color='red')
#    
 
    markers = itertools.cycle((',', '+', '.', 'o', '*','D','s', '^', 'h', '*', 'o', '1', 'p', 'H', 'v', '8', '>')) 
    colors = itertools.cycle(('#e41a1c','#377eb8', '#4daf4a', '#984ea3', '#ff7f00','#ffff33','#a65628','#f781bf','#999999'))

    for c in data:
        datax=data_X[c].dropna()      
        ainx=datax.index.values
        idatax=datax.loc[ainx>0]
        idatax=idatax[idatax>0]
        newcolor = next(colors)
        newmarker = next(markers)
        plt.scatter(idatax.index,idatax,marker=newmarker,s=2**markdersize,color=newcolor,label=c)
        if ptask=='predict':
            datax=data_fit_X[c].dropna()      
            ainx=datax.index.values
            idatax=datax.loc[ainx>0]
            idatax=idatax[idatax>0]
            plt.plot(idatax.index,idatax,color=newcolor,linestyle='--',linewidth=linewidth,label='_nolegend_') 

    plt.legend(loc=legendposition,prop={'size': legendsize})
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    import base64
    figdata_png = base64.b64encode(figfile.getvalue())

    rdata={'plotimg':figdata_png.decode('ascii')
    	,'calvalue':calvalue}
    return json.dumps(rdata)
#    return figdata_png.decode('ascii')
   

if __name__ == "__main__":
    filename='uploads/Delmar_new.csv'
    param={'title': 'titlename',
           'datatype': 'C1000 vs MOP/MIS',
           'model': 'weibull',
           'task': 'predict',
           'estX': 36,
           'plot': {'xtick': '1,2,5,10,15,20,25,30,35,40', 'ytick': '0.1,0.2,0.5,1,2,5,10,20,50,70,100,200,500,999'},
           'program': {'BU 2015 Totals': {'pid': 0, 'selected': 1, 'minX': 1, 'maxX': 26},
                       'BU 2016 Totals': {'pid': 1, 'selected': 0, 'minX': 2, 'maxX': 16},
                       'BU 2017 Totals': {'pid': 2, 'selected': 0, 'minX': 3, 'maxX': 5},
                       'VM 2015 Totals': {'pid': 3, 'selected': 0, 'minX': 4, 'maxX': 25},
                       'VM 2016 Totals': {'pid': 4, 'selected': 1, 'minX': 5, 'maxX': 15},
                       'VM 2017 Totals': {'pid': 5, 'selected': 0, 'minX': 1, 'maxX': 7},
                       'FB 2016 Totals': {'pid': 6, 'selected': 1, 'minX': 2, 'maxX': 23}}
           }
    plotdata(filename, param)
