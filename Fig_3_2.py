#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pyper
import japanize_matplotlib
from scipy import optimize
from scipy import stats
plt.rcParams["font.size"] = 18 
pd.set_option('display.max_columns', 100)


# In[2]:


r = pyper.R(use_pandas=True)
r("library(MASS)")
r("library(lme4)")
r("library(lmerTest)")


# In[3]:


# ここからワタリ
birdID_list = ([
                "F0957","F19181","F9899","F23559","F25202","F28308","M9065","M19469","M23642","M25593","M25800","M27528","M28596",
                "F28704","F34122","M8829","M11675","M12505","M25153","M27931",
                "F19818", "F20435", "F22526", "F22950","F28266", "F28388", "F28633", "M20216","M20479","M21219",
                "F9184", "F21278","F22527", "F22675", "F28262", "F28715", "M19162", "M20227", "M25207", "M28191", "M29963", "M30439"
                ])

bdf = pd.DataFrame()

for birdID in birdID_list:
    csv_path1 = fr"C:\\Users\\butte\\Desktop\\datas\\2019_wanderingalbatross\\Ninja\\" + birdID + "\\" + birdID + "takeoff_new_15mw.csv"
    csv_path2 = fr"C:\\Users\\butte\\Desktop\\datas\\2019_wanderingalbatross\\Ninja_watari\\" + birdID + "\\" + birdID + "takeoff_new_15mw.csv"
    csv_path3 = fr"C:\\Users\\butte\\Desktop\\datas\\2020_wanderingalbatross\\Ninja\\" + birdID + "\\" + birdID + "takeoff_new_15mw.csv"
    csv_path4 = fr"C:\\Users\\butte\\Desktop\\datas\\2020_wanderingalbatross\\Ninja_watari\\" + birdID + "\\" + birdID + "takeoff_new_15mw.csv"

    if os.path.exists(csv_path1):
        df = pd.read_csv(csv_path1, sep=',', header = 0)
        
    elif os.path.exists(csv_path2):
        df = pd.read_csv(csv_path2, sep=',', header = 0)
    
    elif os.path.exists(csv_path3):
        df = pd.read_csv(csv_path3, sep=',', header = 0)
        
    elif os.path.exists(csv_path4):
        df = pd.read_csv(csv_path4, sep=',', header = 0)

    else:
        print(birdID + "nodata found") 
    
    df['ID'] = birdID
    
    df = df.dropna(subset=['running_time_list'])
    
#     df = df[df['DPspd_delta_list'] <= 15]
    
    bdf = pd.concat([bdf,df])

bdf = bdf.reset_index()


# In[4]:


print(bdf.columns)


# In[6]:


r.assign("bdf", bdf)


# In[7]:


print(r("result1 <- lmer(DPspd_list ~ running_time_list + (1|ID), data = bdf)"))
# print(r("result1 <- lmer(DPspd_delta_list ~ running_time_list + (1|ID), data = bdf)"))
print(r("summary(result1)"))


# In[8]:


print(r("result2 <- lmer(DPspd_list ~ 1 + (1|ID), data = bdf)"))
# print(r("result2 <- lmer(DPspd_delta_list ~ 1 + (1|ID), data = bdf)"))
print(r("summary(result2)"))


# In[9]:


print(r("anova(result1,result2)"))


# In[10]:


# coefs = r.get("coef(summary(result1))")
# intercept = coefs[0][0]
# coef1 = coefs[1][0]


# In[11]:


# x = np.arange(1,13,1)
# y = intercept + coef1*x

# plt.scatter(bdf["running_time_list"],bdf["DPspd_list"], c = "firebrick")
# # plt.scatter(bdf["running_time_list"],bdf["DPspd_delta_list"], c = "firebrick")
# plt.plot(x,y, color = "k")
# plt.xlabel("助走時間 (s)")
# plt.ylabel("助走速度 (m/s)")

# plt.tight_layout()
# # plt.savefig('running_time_spd.png', dpi=300)

# print(np.corrcoef(bdf["running_time_list"],bdf["DPspd_list"])[0][1])
# # print(np.corrcoef(bdf["running_time_list"],bdf["DPspd_delta_list"])[0][1])
# print("slope " + str(coef1) + " intercept " + str(intercept))


# In[12]:


running_distance = bdf["running_time_list"]*bdf["DPspd_list"]/2
# running_distance = bdf["running_time_list"]*bdf["DPspd_delta_list"]/2
plt.plot(running_distance)
print(str(np.mean(running_distance)) + "±" + str(np.std(running_distance)))


# In[13]:


def linfunc(param,x,y):
    residual = y - (param * x)
#     residual = y - (param[0] * x + param[1])
    return residual
param = 1
result = optimize.leastsq(linfunc,param, args = (bdf["running_time_list"], bdf["DPspd_list"]))[0]
# result = optimize.leastsq(linfunc,param, args = (bdf["running_time_list"], bdf["DPspd_delta_list"]))[0]


# In[14]:


result


# In[34]:


x = np.arange(1,10,1)
y = result*x

plt.figure(figsize = (5,3))
plt.scatter(bdf["running_time_list"],bdf["DPspd_list"],alpha = 0.2, c = "k")
# plt.scatter(bdf["running_time_list"],bdf["DPspd_delta_list"], c = "firebrick")
plt.plot(x,y, color = "k")
# plt.grid()
plt.xlabel("Running duration (s)", fontsize=18)
plt.ylabel("Running\nspeed (m/s)", fontsize=18)
plt.xlim(-0.5,13)
plt.ylim(-0.5,13)

# plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
plt.savefig(save_dir + "duration_speed.png", dpi=500, bbox_inches='tight')
print(result)
print(stats.pearsonr(bdf["running_time_list"],bdf["DPspd_list"]))

