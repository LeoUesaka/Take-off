#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy import optimize
import japanize_matplotlib
plt.rcParams["font.size"] = 18 


# In[ ]:


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

# bdf = bdf.drop(columns='TO_dir_list')
bdf = bdf.drop(columns='before_top_speed_list')
bdf = bdf.drop(columns='before_top_speed_time_list')
bdf["flap_freq_list5"] =  1/bdf["flap_freq_list5"]
# bdf = bdf[bdf['flap_freq_list5'] > 1.8]

bdf_wind = bdf.dropna(subset=['wind_spd_list'])
bdf_wind = bdf_wind.dropna(subset=['TO_dir_list2'])
bdf_wind = bdf_wind[bdf_wind['AIC_list'] == 1]

bdf_wave = bdf.dropna(subset=['sgh_list'])

bdf_env = bdf_wind.dropna(subset=['sgh_list'])

bdf = bdf.reset_index()
bdf_wind = bdf_wind.reset_index()
bdf_wave = bdf_wave.reset_index()
bdf_env = bdf_env.reset_index()

# wind_thresh = 6
# wave_thresh = 2.8

# bdf_env["condition"] = ["Windy Highwave" if x>wind_thresh and y>wave_thresh else 
#                         "Calm Highwave" if x<wind_thresh and y>wave_thresh else 
#                         "Windy Lowwave" if x>wind_thresh and y<wave_thresh else 
#                         "Calm Lowwave" for x,y in zip(bdf_env["wind_spd_list"],bdf_env["sgh_list"])]
bdf_env = bdf_env.iloc[::-1]


# In[4]:


def lognormfunc(params,x,y):
    residual = y - stats.lognorm.pdf(x, s = params[0], loc=0, scale=np.exp(params[1]))
    return residual

def weibullfunc(params,x,y):
    residual = y - stats.weibull_min.pdf(x/params[1], c = params[2])/params[0]
    return residual

wind_hist = np.histogram(bdf_wind["wind_spd_list"], bins = 8,range = (0,16), density=True)[0]
wind_hist_x = np.arange(1, 16, 2)

params = [7,7,3]
result = optimize.leastsq(weibullfunc,params, args = (wind_hist_x, wind_hist))[0]
wind_fit_x = np.arange(0.05,16,0.05)
wind_fit_curve = stats.weibull_min.pdf(wind_fit_x/params[1], c = params[2])/params[0]

wave_hist = np.histogram(bdf_wave["sgh_list"], bins = 10,range = (1,6), density=True)[0]
wave_hist_x = np.arange(1.25, 6, 0.5)

param1 = [0.3,1]
result = optimize.leastsq(lognormfunc,param1, args = (wave_hist_x, wave_hist))[0]

wave_fit_x = np.arange(0.05,6,0.05)
wave_fit_curve = stats.lognorm.pdf(wave_fit_x, s = result[0], loc=0, scale=np.exp(result[1]))


# In[142]:


plt.rcParams["font.size"] = 16 
fig = plt.figure(figsize = (8,6))
# fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2,figsize = (7,6), sharex="col", sharey="row")

# Duration
ax1 = fig.add_subplot(221)
sc1 = ax1.scatter(bdf_env["wind_spd_list"],bdf_env["sgh_list"],s = 40, c = bdf_env["running_time_list"],
                 cmap = "gray_r", edgecolor='k',vmin=3.8, vmax=8.2)
cbar = fig.colorbar(sc1,ticks=[4,6,8], extend = "both")
cbar.ax.set_yticklabels(["4","6","8 (s)"])
ax1.set_xlim(-0.5,16.5)
ax1.set_ylim(1.2,5.8)
ax1.set_xticks([0,4,8,12,16])
ax1.set_yticks([2,3,4,5])
ax1.axes.xaxis.set_ticklabels([])
# ax1.set_title("Running duration (s)",fontsize = 16)
ax1.text(0.98, 0.02,"Running\nduration", ha = "right", va = "bottom",size = 14, transform=ax1.transAxes)
ax1.set_ylabel("Wave height (m)")

# Speed
ax2 = fig.add_subplot(222)
sc2 = ax2.scatter(bdf_env["wind_spd_list"],bdf_env["sgh_list"],s = 40 , c = bdf_env["DPspd_list"],
                 cmap = "gray_r", edgecolor='k',vmin=3.8, vmax=9.2)
cbar = fig.colorbar(sc2,ticks=[4,6.5,9], extend = "both")
cbar.ax.set_yticklabels(["4","6.5","9 (m/s)"])
ax2.set_xlim(-0.5,16.5)
ax2.set_ylim(1.2,5.8)
ax2.set_xticks([0,4,8,12,16])
ax2.set_yticks([2,3,4,5])
ax2.axes.xaxis.set_ticklabels([])
ax2.axes.yaxis.set_ticklabels([])
ax2.text(0.98, 0.02,"Running\nspeed", ha = "right", va = "bottom",size = 14, transform=ax2.transAxes)
# ax2.set_title("Running speed (m/s)",fontsize = 16)

# number
ax3 = fig.add_subplot(223,)
sc3 = ax3.scatter(bdf_env["wind_spd_list"],bdf_env["sgh_list"],s = 40 , c = bdf_env["flap_num2_list"],
                 cmap = "gray_r", edgecolor='k',vmin=0, vmax=12.2)
cbar = fig.colorbar(sc3,ticks=[0,6,12], extend = "both")
cbar.ax.set_yticklabels(["0","6","12"])
ax3.set_xlim(-0.5,16.5)
ax3.set_ylim(1.2,5.8)
ax3.set_xticks([0,4,8,12,16])
ax3.set_yticks([2,3,4,5])
ax3.text(0.98, 0.02,"Flapping\nnumber", ha = "right", va = "bottom",size = 14, transform=ax3.transAxes)
# ax3.set_title("Flapping number (times)",fontsize = 16)

ax3.set_xlabel("Wind speed (m/s)")
ax3.set_ylabel("Wave height (m)")

# frequency
ax4 = fig.add_subplot(224)
sc4 = ax4.scatter(freq_bdf_env["wind_spd_list"],freq_bdf_env["sgh_list"],s = 40 , c = freq_bdf_env["flap_freq_list5"],
                 cmap = "gray_r", edgecolor='k',vmin=1.95, vmax=3.05)
cbar = fig.colorbar(sc4,ticks=[2.0,2.5,3.0], extend = "both")
cbar.ax.set_yticklabels(["2","2.5","3 (Hz)"])
ax4.set_xlim(-0.5,16.5)
ax4.set_ylim(1.2,5.8)
ax4.set_xticks([0,4,8,12,16])
ax4.set_yticks([2,3,4,5])
ax4.axes.yaxis.set_ticklabels([])
ax4.text(0.98, 0.02,"Flapping\nfrequency", ha = "right", va = "bottom",size = 14, transform=ax4.transAxes)
# ax4.set_title("Flapping frequency (Hz)",fontsize = 16)

ax4.set_xlabel("Wind speed (m/s)")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
plt.savefig(save_dir + "4colorplots.png", dpi=500, bbox_inches='tight')


# In[ ]:




