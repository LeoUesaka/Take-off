#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import japanize_matplotlib
from astropy.stats import vtest
from astropy.stats import rayleightest
from astropy import units as u

plt.rcParams["font.size"] = 18 


# In[5]:


# ここからワタリ
birdID_list = ([
                "F0957","F19181","F9899","F23559","F25202","F28308","M9065","M19469","M23642","M25593","M25800","M27528","M28596",
                "F28704","F34122","M8829","M11675","M12505","M25153","M27931",
                "F19818", "F20435", "F22526", "F22950","F28266", "F28388", "F28633", "M20216","M20479","M21219",
                "F9184", "F21278","F22527", "F22675", "F28262", "F28715", "M19162", "M20227", "M25207", "M28191", "M29963", "M30439"
                ])

bdf = pd.DataFrame()
for birdID in birdID_list:
    csv_path1 = fr"C:\\Users\\butte\\Desktop\\datas\\2019_wanderingalbatross\\Ninja\\" + birdID + "\\" + birdID + "takeoff_new.csv"
    csv_path2 = fr"C:\\Users\\butte\\Desktop\\datas\\2019_wanderingalbatross\\Ninja_watari\\" + birdID + "\\" + birdID + "takeoff_new.csv"
    csv_path3 = fr"C:\\Users\\butte\\Desktop\\datas\\2020_wanderingalbatross\\Ninja\\" + birdID + "\\" + birdID + "takeoff_new.csv"
    csv_path4 = fr"C:\\Users\\butte\\Desktop\\datas\\2020_wanderingalbatross\\Ninja_watari\\" + birdID + "\\" + birdID + "takeoff_new.csv"

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
#     df = df[df['flap_freq_list5'] < 0.5]
    
#     df = df[df['DPspd_delta_list'] <= 15]
    bdf = pd.concat([bdf,df])
    


# bdf = bdf.drop(columns='TO_dir_list')
bdf = bdf.drop(columns='before_top_speed_list')
bdf = bdf.drop(columns='before_top_speed_time_list')
bdf["flap_freq_list5"] =  1/bdf["flap_freq_list5"]

bdf_wind = bdf.dropna(subset=['wind_spd_list'])
bdf_wind = bdf_wind.dropna(subset=['TO_dir_list2'])
bdf_wind = bdf_wind[bdf_wind['AIC_list'] == 1]
dir_diff_wind = bdf_wind["TO_dir_list2"] - bdf_wind["wind_dir_list"]
dir_diff_wind = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_wind])
bdf_wind["net_wind"] = np.cos(np.deg2rad(dir_diff_wind))*bdf_wind['wind_spd_list']

bdf_wave = bdf.dropna(subset=['sgh_list'])

bdf_env = bdf_wind.dropna(subset=['sgh_list'])

bdf = bdf.reset_index()
bdf_wind = bdf_wind.reset_index()
bdf_wave = bdf_wave.reset_index()
bdf_env = bdf_env.reset_index()

bdf_env["condition"] = ["Windy Highwave" if x>6 and y>3else 
                        "Calm Highwave" if x<6 and y>3 else 
                        "Windy Lowwave" if x>6 and y<3 else 
                        "Calm Lowwave" for x,y in zip(bdf_env["wind_spd_list"],bdf_env["sgh_list"])]


# In[7]:


dir_diff_wind = bdf_wind["TO_dir_list2"] - bdf_wind["wind_dir_list"]
dir_diff_wind = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_wind])

dir_diff_wave = bdf_wave["TO_dir_list2"] - bdf_wave["sgd_list"]
dir_diff_wave = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_wave])

dir_diff_wind_env = bdf_env["TO_dir_list2"] - bdf_env["wind_dir_list"]
dir_diff_wind_env = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_wind_env])

dir_diff_ww = bdf_env["wind_dir_list"] - bdf_env["sgd_list"]
dir_diff_ww = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_ww])

dir_diff_cruis_wind = bdf_wind["cruis_dir_list"] - bdf_wind["wind_dir_list"]
dir_diff_cruis_wind = np.array([x+360 if x<-180 else x-360 if x>180 else x for x in dir_diff_cruis_wind])


# In[9]:


# 論文用の図
fig = plt.figure(figsize = (12,12))
plt.rcParams["font.size"] = 17

ax1 = fig.add_subplot(211, projection="polar")

ax1.scatter(dir_diff_cruis_wind*np.pi/180, bdf_wind["wind_spd_list"], facecolor = "gray", edgecolor = "gray", marker = "x", s = 25, alpha = 0.5)
ax1.scatter(dir_diff_wind*np.pi/180, bdf_wind["wind_spd_list"], facecolor = "None", edgecolor = "k", s = 25)

ax1.set_xlim([-np.pi, np.pi])
ax1.set_xticks(np.arange(-np.pi,np.pi,np.pi/4))

ax1.set_rlim(0, 16)
ax1.set_rgrids(np.arange(4, 16, 4),angle=180)

ax1.set_theta_zero_location("N")

ax1.text(0.5, 0.03,"wind speed\n(m/s)", transform=ax1.transAxes, fontsize = 14)

save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "relative_TO_duration.png", dpi=500, bbox_inches='tight')

