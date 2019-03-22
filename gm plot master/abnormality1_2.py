import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import pymysql.cursors
import statistics
import csv
import math
from gmplot import gmplot
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from dbscanfa import MyDBSCAN
from numpy import array
from sklearn.cluster import KMeans
datast = []
datamov = []
datamovlatactual = []
datamovlat = []

datamovspd = []


with open('exactEarth_historical_data.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    i=0
    
    for row in readCSV:
        if(i==0 or row[26]==''):
            i=1
        else:
            data = float(row[26])
            
            if(data > 0.5):
                datamov.append([row[0],row[3],float(row[28]),float(row[29]),float(row[26]),float(row[30])])
            else:
                datast.append([row[0],row[3],row[28],row[29],row[30],row[26]])
                
            
            
    for r in datamov:
        datamovlatactual.append([r[2],r[3]])
        datamovspd.append([r[4],r[5]])
        
    datamovlat= StandardScaler().fit_transform(datamovlatactual)
        
print ("Running my implementation...")

#print(datamovlat)

list_labels = MyDBSCAN(datamovlat,datamovspd, eps=0.3, MinPts=5)
db = array( list_labels )

#core_samples_mask = np.zeros_like(list_labels, dtype=bool)
#core_samples_mask[db.core_sample_indices_] = True

n_clusters_ = len(set(list_labels)) - (1 if -1 in list_labels else 0)
#print(type(db))

unique_labels = set(list_labels)

x = datamovlat[:, 0]
y = datamovlat[:, 1]

#for j in (range(len(unique_labels))):
   # print(j)


colors = [plt.cm.Spectral(each)

          for each in np.linspace(0, 1, len(unique_labels))]

        
for k, col in zip(unique_labels, colors):

    if k == -1:

        # Black used for noise.

        col = [0, 0, 0, 1]

    #plt.plot(datamovlat[:, 0], datamovlat[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)


#plt.title('Estimated number of clusters: %d' % n_clusters_)

#plt.show()
color_codes = [
   'darkmagenta'
   , 'yellow'
   ,'darkgreen'
   ,'black'
   ,'darkorange'
   ,'purple'
   ,'cornflowerblue'
   , 'orchid'
   ,'darkgray'
   ,'gold'
   ,'pink'
   ,'brown'
   ,'crimson'
   ,'coral'
   , 'navy'
   
   
]

gmap = gmplot.GoogleMapPlotter(-68.779056, 33.529694,3 )
clustermat=[]
for i in range(1,max(list_labels)+1):
    clustermat.insert(i,[i])
for i in range(0,len(list_labels)):
    
    clustermat[list_labels[i]-1].append([datamovlatactual[i][0],datamovlatactual[i][1],datamovspd[i][0],datamovspd[i][1]])

for i in range(len(list_labels)):
    lats, lons = zip(datamovlatactual[i])
    
    gmap.scatter(lats, lons, color_codes[list_labels[i]], size=15600, marker=False)
gmap.draw("hack_dbscan_plot.html")  
gv=[]
for i in range(max(list_labels)):
    clustermat[i].pop(0)
gmapcl = gmplot.GoogleMapPlotter(-23.3011833333, 38.1240483333,8 ) 
   
cogw=[]
g=[]
for i in range(0,len(clustermat)):
    g.insert(i,[0])
for clustval in range(len(clustermat)):
    p=[]
    p=clustermat[clustval]
    pts=[]
    
    for i in p:
        pts.append((i[0],i[1]))
                   
        #gmapcl.scatter(lats, lons,'black', size=60, marker=False)
    distance = math.sqrt( ((pts[0][0]-pts[len(pts)-1][0])**2)+((pts[0][1]-pts[len(pts)-1][1])**2) )
    kpt=int(distance/2)
    kpt+=1
    
    kmeans = KMeans(n_clusters=kpt).fit(pts)
    clustar=kmeans.labels_
    clustercenter=kmeans.cluster_centers_
    sumcog=0.0
    sumsog=0.0
    for i in range(len(clustercenter)):
        mediancl=[]
        for j in range(len(p)):
            if clustar[j]==i:
                sumcog+=p[j][3]
                sumsog+=p[j][2]
                mediancl.append( math.sqrt( ((p[j][0]-clustercenter[i][0])**2)+((p[j][1]-clustercenter[i][1])**2) ))
    
        cnt=list(clustar).count(i)
        sumcog/=cnt
        sumsog/=cnt
        medianval=statistics.median(mediancl)
        if medianval==0:
            medianval=0.0000001
        g[clustval].append((clustercenter[i][0],clustercenter[i][1],sumsog,sumcog,medianval))
        
    lats, lons = zip(*clustercenter)
    
    gmapcl.scatter(lats, lons,color_codes[clustval], size=3500, marker=False)
for i in range(0,len(clustermat)):
    g[i].pop(0)
gmapcl.draw("hack_dbscan_plot_cluster.html")                  

#Anomaly Detection
def RDD(gv,dm):
    rdddist = math.sqrt(((gv[0]-dm[0])**2)+((gv[1]-dm[1])**2))/gv[4]
    return rdddist
def CDD(gv,dm):
    alpha=gv[3]-dm[3]
    cdddist= (min(gv[2],dm[2])/max(gv[2],dm[2]))*math.cos(alpha)
    return cdddist
def ABNormality(gv,datam):    
    m_label=[]
    for i in datam:
        m_label.append(0)
    rdd_thres=4.5
    cdd_thres=0.5
    mm=0
    for m in datam:
        rdd_m=100000000
        for i in gv:
            for j in i:
                #print(RDD(j,m))
                if rdd_m> RDD(j,m):
                    rdd_m=RDD(j,m)
        print(rdd_m)
        if rdd_m>rdd_thres:
            m_label[mm]= -1
            print("rdd")
        else:
            
            cdd_m=0
            for i in gv:
                for j in i:
                    if cdd_m < CDD(j,m):
                        cdd_m=CDD(j,m)
            #print("cdd_m")
            #print(cdd_m)            
            if cdd_m<cdd_thres:
                m_label[mm]= -1
                print("cdd")
        mm+=1
    count_ab=m_label.count(-1)
    #print(count_ab)
    #print(len(m_label))
    abnormality=count_ab/len(m_label)
    return abnormality

with open('cm2.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    datavals=[]
    for row in readCSV:
        datavals.append([float(row[0]),float(row[1]),float(row[2]),float(row[3])])

abr=ABNormality(g,datavals)
print(abr)  
""" 
if abr>0.4 and abr<=0.7:
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='shore',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO notification ( user_id, heading, message, status, abnormality_level) VALUES (1,'WARNING','The ship is moving into an abnormal position',0,1);"
            cursor.execute(sql)
    
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    finally:
        connection.close()
elif abr>0.7 and abr<=1:
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='shore',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO notification ( user_id, heading, message, status, abnormality_level) VALUES (1,'DANGER','High Abnormality Detected',0,2);"
            cursor.execute(sql)
    
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    finally:
        connection.close()
        
        """
    
    
#abr=ABNormality(g,clustermat[13])
#print(abr)

plt.plot([item[0] for item in datavals], [item[1] for item in datavals], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)
plt.plot([item[0] for item in clustermat[2]], [item[1] for item in clustermat[2]], 'o', markerfacecolor='blue',         markeredgecolor='k', markersize=14)
plt.title('Estimated number of clusters: %d') 



