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
plt.rcParams["font.size"] = 20 


# In[2]:


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

wind_thresh = 6
wave_thresh = 2.8

bdf_env["condition"] = ["Windy Highwave" if x>wind_thresh and y>wave_thresh else 
                        "Calm Highwave" if x<wind_thresh and y>wave_thresh else 
                        "Windy Lowwave" if x>wind_thresh and y<wave_thresh else 
                        "Calm Lowwave" for x,y in zip(bdf_env["wind_spd_list"],bdf_env["sgh_list"])]


# In[5]:


WH = bdf_env[bdf_env['condition'] == "Windy Highwave"]
CH = bdf_env[bdf_env['condition'] == "Calm Highwave"]
WL = bdf_env[bdf_env['condition'] == "Windy Lowwave"]
CL = bdf_env[bdf_env['condition'] == "Calm Lowwave"]


# In[6]:


WH_running_time_list = WH["running_time_list"].values.tolist()
CH_running_time_list = CH["running_time_list"].values.tolist()
WL_running_time_list = WL["running_time_list"].values.tolist()
CL_running_time_list = CL["running_time_list"].values.tolist()


# In[7]:


WH_flap_num10_list = WH["flap_num2_list"].values.tolist()
CH_flap_num10_list = CH["flap_num2_list"].values.tolist()
WL_flap_num10_list = WL["flap_num2_list"].values.tolist()
CL_flap_num10_list = CL["flap_num2_list"].values.tolist()


# In[8]:


WH_DPspd_delta_list = WH["DPspd_delta_list"].values.tolist()
CH_DPspd_delta_list = CH["DPspd_delta_list"].values.tolist()
WL_DPspd_delta_list = WL["DPspd_delta_list"].values.tolist()
CL_DPspd_delta_list = CL["DPspd_delta_list"].values.tolist()
WH_DPspd_list = WH["DPspd_list"].values.tolist()
CH_DPspd_list = CH["DPspd_list"].values.tolist()
WL_DPspd_list = WL["DPspd_list"].values.tolist()
CL_DPspd_list = CL["DPspd_list"].values.tolist()


# In[9]:


# bdf = bdf[bdf['flap_freq_list5'] > 1.8]
WH_flap_freq_list = np.array([x  for x in WH["flap_freq_list5"] if x > 1.8])
CH_flap_freq_list = np.array([x  for x in CH["flap_freq_list5"] if x > 1.8])
WL_flap_freq_list = np.array([x  for x in WL["flap_freq_list5"] if x > 1.8])
CL_flap_freq_list = np.array([x  for x in CL["flap_freq_list5"] if x > 1.8])


# In[11]:


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


# In[12]:


plt.rcParams["font.size"] = 20
fig = plt.figure(figsize = (6,6))

gp = 0.80

ax_main = fig.add_axes([0, 0, gp, gp])
ax_main.scatter(WH["wind_spd_list"],WH["sgh_list"],s = 100 ,label = "風速大 波高大", marker = "o", c = "gray", edgecolor='k')
ax_main.scatter(CH["wind_spd_list"],CH["sgh_list"],s = 81 ,label = "風速小 波高大", marker = "s", c = "gray", edgecolor='k')
ax_main.scatter(WL["wind_spd_list"],WL["sgh_list"],s = 100 ,label = "風速大 波高小", marker = "o", c = "w", edgecolor='k')
ax_main.scatter(CL["wind_spd_list"],CL["sgh_list"],s = 81 ,label = "風速小 波高小", marker = "s", c = "w", edgecolor='k')

ax_main.set_xlim(-0.5,16.5)
ax_main.set_ylim(1.2,5.8)
ax_main.set_xticks([0,4,8,12,16])
ax_main.set_yticks([2,3,4,5])

ax_main.set_xlabel("Wind speed (m/s)")
ax_main.set_ylabel("Wave height (m)")

ax_main.hlines(y=2.79, xmin=-3, xmax=20,linestyles='--', color = "gray", linewidths = 1)
ax_main.vlines(x=6, ymin=-3, ymax=20,linestyles='--', color = "gray", linewidths = 1)

ax_wave = fig.add_axes([gp+0.02, 0, 0.98-gp, gp],sharey = ax_main)
ax_wind = fig.add_axes([0, gp+0.02, gp, 0.98-gp],sharex = ax_main)

ax_wind.set_xlim(-0.5,16.5)
ax_wave.set_ylim(1.2,5.8)
# ax_wind.set_xticks([0,4,8,12,16])
# ax_wave.set_yticks([2,3,4,5])

# ax_wind.tick_params(labelbottom=False,labelleft=False,left=False)
ax_wind.tick_params(labelbottom=False, labelsize = 13)
# ax_wave.tick_params(labelbottom=False,labelleft=False,bottom=False)
ax_wave.tick_params(labelleft=False, labelsize = 13)
ax_wave.set_xticklabels(["　0.0", "0.5"])

ax_wind.hist(bdf_wind["wind_spd_list"], bins=8, range=(0,16),alpha = 0.7, density=True,color="gray", edgecolor='w')
ax_wind.plot(wind_fit_x, wind_fit_curve, c = "k")

ax_wave.hist(bdf_wave["sgh_list"], bins=10, range=(1,6),alpha = 0.7, density=True,color="gray", edgecolor='w',orientation="horizontal")
ax_wave.plot(wave_fit_curve,wave_fit_x ,c = "k")

plt.show

save_dir = "C:\\Users\\butte\\Desktop\\Take-off of wandering albatrosses in relation to wave and wind condition measured by animal-born recorders\\fig&tables\\工場\\"
# plt.savefig(save_dir + "4area_grid.png", dpi=500, bbox_inches='tight')


# In[26]:


plt.rcParams["font.size"] = 16 
fig = plt.figure(figsize = (7,6))
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

ax1.boxplot((CL_running_time_list, CH_running_time_list, WL_running_time_list, WH_running_time_list),
            whis=1, patch_artist=True, medianprops=dict(color="k", linewidth=1),
            boxprops=dict(facecolor="w",color="k", linewidth=1),
            showmeans=True,
            meanprops={"marker":"x","markerfacecolor":"white", "markeredgecolor":"k", "markersize":"7"})
ax1.set_xticklabels(["WL","WH","SL","SH"])
ax1.grid(axis="y",linestyle = ":")
# ax1.set_title("Running duration (s)", fontsize = 16)
ax1.set_ylabel("Running duration (s)", fontsize = 16)
ax1.set_ylim(-0.5,11)
ax1.set_yticks([0, 4, 8])
# ax1.set_yticklabels(["0", "5", "10(s)"])


ax2.boxplot((CL_DPspd_list, CH_DPspd_list, WL_DPspd_list, WH_DPspd_list),
            whis=1, patch_artist=True, medianprops=dict(color="k", linewidth=1),
            boxprops=dict(facecolor="w",color="k", linewidth=1),
            showmeans=True,
            meanprops={"marker":"x","markerfacecolor":"white", "markeredgecolor":"k", "markersize":"7"})
ax2.set_xticklabels(["WL","WH","SL","SH"])
ax2.grid(axis="y",linestyle = ":")
# ax2.set_title("Running speed (m/s)", fontsize = 16)
ax2.set_ylabel("Running speed (m/s)", fontsize = 16)
ax2.set_ylim(-0.5,13)
ax2.set_yticks([0, 4, 8, 12])


ax3.boxplot((CL_flap_num10_list, CH_flap_num10_list, WL_flap_num10_list, WH_flap_num10_list),
            whis=1, patch_artist=True, medianprops=dict(color="k", linewidth=1),
            boxprops=dict(facecolor='w',color="k", linewidth=1),
            showmeans=True,
            meanprops={"marker":"x","markerfacecolor":"white", "markeredgecolor":"k", "markersize":"7"})
ax3.set_xticklabels(["WL","WH","SL","SH"])
ax3.grid(axis="y",linestyle = ":")
# ax3.set_title("Flapping number", fontsize = 16)
ax3.set_ylabel("Flapping number", fontsize = 16)
ax3.set_ylim(-0.5,42)
ax3.set_yticks([0, 10, 20, 30, 40])


ax4.boxplot((CL_flap_freq_list, CH_flap_freq_list, WL_flap_freq_list, WH_flap_freq_list),
            whis=1, patch_artist=True, medianprops=dict(color="k", linewidth=1),
            boxprops=dict(facecolor='w',color="k", linewidth=1),
            showmeans=True,
            meanprops={"marker":"x","markerfacecolor":"white", "markeredgecolor":"k", "markersize":"7"})
ax4.set_xticklabels(["WL","WH","SL","SH"])
ax4.grid(axis="y",linestyle = ":")
# ax4.set_title("Flapping frequency (Hz)", fontsize = 16)
ax4.set_ylabel("Flapping frequency (Hz)", fontsize = 16)
ax4.set_yticks([2, 2.5, 3, 3.5])

plt.tight_layout()

save_dir = "C:\\Users\\butte\\Desktop\\Wandering albatross exert high take-off effort in weak wind with low wave conditions\\fig&tables\\工場\\"
plt.savefig(save_dir + "4boxplots_paperrevise.png", dpi=500, bbox_inches='tight')
plt.show


# In[ ]:




