#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from scipy import optimize
from scipy import stats
import japanize_matplotlib

plt.rcParams["font.size"] = 18 


# In[2]:


# ここからワタリ
birdID_list = ([
                "F0957","F19181","F9899","F23559","F25202","F28308","M9065","M19469","M23642","M25593","M25800","M27528","M28596",
                "F28704","F34122","M8829","M11675","M12505","M25153","M27931",
                "F19818", "F20435", "F22526", "F22950","F28266", "F28388", "F28633", "M20216","M20479","M21219",
                "F9184", "F21278","F22527", "F22675", "F28262", "F28715", "M19162", "M20227", "M25207", "M28191", "M29963", "M30439"
                ])

BM_list = ([
        7.2, 8.8, 9.1, 7.5, 8.0, 7.0, 11.2, 8.6, 9.1, 10.8, 10.2, 10.4, 9.6,
        9.4, 7.4, 11.0, 10.2, 11.0, 11.0, 11.2,
        8.0, 8.5, 8.2, 7.4, 8.3, 7.1, 7.1, 10.9, 9.0, 8.2,
        9.0, 8.3, 8.0, 8.2, 8.1, 8.1, 9.3, 9.2, 9.5, 8.4, 9.2, 9.2
        ])

bdf = pd.DataFrame()
for birdID, mass in zip(birdID_list,BM_list):
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
    df['mass'] = mass
    df = df.dropna(subset=['running_time_list'])
    bdf = pd.concat([bdf,df])
    


# bdf = bdf.drop(columns='TO_dir_list')
bdf = bdf.drop(columns='before_top_speed_list')
bdf = bdf.drop(columns='before_top_speed_time_list')
bdf["flap_freq_list5"] =  1/bdf["flap_freq_list5"]

bdf_wind = bdf.dropna(subset=['wind_spd_list'])
bdf_wind = bdf_wind.dropna(subset=['TO_dir_list2'])
bdf_wind = bdf_wind[bdf_wind['AIC_list'] == 1]

bdf_wave = bdf.dropna(subset=['sgh_list'])

bdf_env = bdf_wind.dropna(subset=['sgh_list'])

bdf = bdf.reset_index()
bdf_wind = bdf_wind.reset_index()
bdf_wave = bdf_wave.reset_index()
bdf_env = bdf_env.reset_index()

bdf_env["condition"] = ["Windy Highwave" if x>6 and y>2.8 else 
                        "Calm Highwave" if x<6 and y>2.8 else 
                        "Windy Lowwave" if x>6 and y<2.8 else 
                        "Calm Lowwave" for x,y in zip(bdf_env["wind_spd_list"],bdf_env["sgh_list"])]


# In[3]:


longflap = bdf_env[bdf_env['flap_num2_list'] > 20]


# In[5]:


M = bdf[bdf['ID'].str[:1] == "M"]
F = bdf[bdf['ID'].str[:1] == "F"]


# In[9]:


plt.hist(M["running_time_list"], bins = 15,range = (0,15),color="navy", edgecolor='w',alpha = 0.5)
plt.hist(F["running_time_list"], bins = 15,range = (0,15),color="firebrick", edgecolor='w',alpha = 0.5)
plt.xlabel("Running duration (s)")
plt.ylabel("Count (times)")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "running_duration_MF.png", dpi=300, bbox_inches='tight')

print("M : " + str(np.mean(M["running_time_list"])) + "±" + str(np.std(M["running_time_list"])))
print("F : " + str(np.mean(F["running_time_list"])) + "±" + str(np.std(F["running_time_list"])))

print(stats.mannwhitneyu(M["running_time_list"],F["running_time_list"]))
# print(stats.ttest_ind(M["running_time_list"],F["running_time_list"]))


# In[11]:


# plt.hist(M["DPspd_delta_list"], bins = 15,range = (0,15),color="navy", edgecolor='w',alpha = 0.5)
# plt.hist(F["DPspd_delta_list"], bins = 15,range = (0,15),color="firebrick", edgecolor='w',alpha = 0.5)
plt.hist(M["DPspd_list"], bins = 15,range = (0,15),color="navy", edgecolor='w',alpha = 0.5)
plt.hist(F["DPspd_list"], bins = 15,range = (0,15),color="firebrick", edgecolor='w',alpha = 0.5)

plt.xlabel("Running speed (m/s)")
plt.ylabel("Count (times)")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "running_speed_MF.png", dpi=300, bbox_inches='tight')

print("M : " + str(np.mean(M["DPspd_list"])) + "±" + str(np.std(M["DPspd_list"])))
print("F : " + str(np.mean(F["DPspd_list"])) + "±" + str(np.std(F["DPspd_list"])))

print(stats.mannwhitneyu(M["DPspd_list"],F["DPspd_list"]))
# print(stats.ttest_ind(M["DPspd_delta_list"],F["DPspd_delta_list"]))


# In[13]:


plt.hist(M["flap_num2_list"], bins = 15,range = (0,30),color="navy", edgecolor='w',alpha = 0.5)
plt.hist(F["flap_num2_list"], bins = 15,range = (0,30),color="firebrick", edgecolor='w',alpha = 0.5)

plt.xlabel("Flapping number (times)")
plt.ylabel("Count (times)")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Flapping_number_MF.png", dpi=300, bbox_inches='tight')

print("M : " + str(np.mean(M["flap_num2_list"])) + "±" + str(np.std(M["flap_num2_list"])))
print("F : " + str(np.mean(F["flap_num2_list"])) + "±" + str(np.std(F["flap_num2_list"])))

print(stats.mannwhitneyu(M["flap_num2_list"],F["flap_num2_list"]))
# print(stats.ttest_ind(M["flap_num10_list"],F["flap_num10_list"]))


# In[16]:


M = M[M['flap_freq_list5'] > 1.8]
F = F[F['flap_freq_list5'] > 1.8]

plt.hist(M["flap_freq_list5"], bins = 10,range = (1.4,3.4),color="navy", edgecolor='w',alpha = 0.5)
plt.hist(F["flap_freq_list5"], bins = 10,range = (1.4,3.4),color="firebrick", edgecolor='w',alpha = 0.5)

plt.xlabel("Flapping frequency (Hz)")
plt.ylabel("Count (times)")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Flapping_frequency_MF.png", dpi=300, bbox_inches='tight')
plt.show

print(stats.mannwhitneyu(M["flap_freq_list5"],F["flap_freq_list5"]))
print("M : " + str(len(M)))
print("F : " + str(len(F)))

# print(stats.ttest_ind(M["flap_freq_list5"],F["flap_freq_list5"]))


# In[17]:


plt.rcParams["font.size"] = 16 
fig = plt.figure(figsize = (7,6))
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

ax1.hist(bdf["running_time_list"], bins = 13,range = (0,13),color="gray", edgecolor='w')
ax1.set_xlabel("Running duration (s)")
ax1.set_ylabel("Count")

ax2.hist(bdf["DPspd_list"], bins = 13,range = (0,13),color="gray", edgecolor='w')
ax2.set_xlabel("Running speed (m/s)")

ax3.hist(bdf["flap_num2_list"], bins = 13,range = (0,26),color="gray", edgecolor='w')
ax3.set_xlabel("Flapping number")
ax3.set_ylabel("Count")

ax4.hist(freq_bdf["flap_freq_list5"], bins = 9,range = (1.6,3.4),color="gray", edgecolor='w')
ax4.set_xlabel("Flapping frequency (Hz)")

plt.tight_layout()

save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "4Hist.png", dpi=500, bbox_inches='tight')


# In[19]:


def lognormfunc(params,x,y):
    residual = y - stats.lognorm.pdf(x, s = params[0], loc=0, scale=np.exp(params[1]))
    return residual

def weibullfunc(params,x,y):
    residual = y - stats.weibull_min.pdf(x/params[1], c = params[2])/params[0]
    return residual

wind_hist = np.histogram(bdf_wind["wind_spd_list"], bins = 8,range = (0,16), density=True)[0]
wind_hist_x = np.arange(1, 16, 2)

params = [7,7,3]
# params = [7,3]
result = optimize.leastsq(weibullfunc,params, args = (wind_hist_x, wind_hist))[0]
# result = optimize.leastsq(lognormfunc,params, args = (wind_hist_x, wind_hist))[0]

fit_x = np.arange(0.05,16,0.05)
fit_curve = stats.weibull_min.pdf(fit_x/params[1], c = params[2])/params[0]
# fit_curve = stats.lognorm.pdf(fit_x, s = result[0], loc=0, scale=np.exp(result[1]))


# In[20]:


plt.figure(figsize = (5,3))
plt.hist(bdf_wind["wind_spd_list"], bins=8, range=(0,16),alpha = 1, color="gray", edgecolor='w')
# plt.xlim(0.1,16)
# plt.ylim(0,0.18)
# plt.yticks(np.arange(0,0.16,0.05))

plt.xlabel("Wind speed (m/s)")
plt.ylabel("Count (times)")
plt.xticks([4,8,12])

# plt.plot(fit_x, fit_curve, c = "k")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Wind_spd.png", dpi=500, bbox_inches='tight')

plt.show

print(str(np.mean(bdf_wind["wind_spd_list"])) + "±" + str(np.std(bdf_wind["wind_spd_list"])))
print(min(bdf_wind["wind_spd_list"]))
print(max(bdf_wind["wind_spd_list"]))


# In[22]:


sgd_list_hist = np.histogram(bdf_wind["wind_dir_list"], bins = 18,range = (0,360))
plt.figure(figsize = (3,3))
plt.rcParams["font.size"] = 10 
theta = np.arange(0.0, 2 * np.pi,2 * np.pi/18)
radii = sgd_list_hist[0]
width = 2 * np.pi/18
bottom = 0

ax = plt.subplot(111, polar=True)
bars = ax.bar(theta, radii, width=width, bottom=0, align = 'edge',alpha = 1, color="lightgray", edgecolor='k')
ax.set_yticks([20,40,60])
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_thetagrids(np.rad2deg(np.linspace(0, 2*np.pi, 9)[1:]), 
                      labels=["NE", "E","SE" , "S", "SW", "W","NW", "N"],
                      fontsize=20)
ax.set_axisbelow(True)

plt.ylim(-40,80)

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Wind_direction.png", dpi=500, bbox_inches='tight')
plt.show()


# In[23]:


wave_hist = np.histogram(bdf_wave["sgh_list"], bins = 10,range = (1,6), density=True)[0]
wave_hist_x = np.arange(1.25, 6, 0.5)

param1 = [0.3,1]
result = optimize.leastsq(lognormfunc,param1, args = (wave_hist_x, wave_hist))[0]

fit_x = np.arange(0.05,6.5,0.05)
fit_curve = stats.lognorm.pdf(fit_x, s = result[0], loc=0, scale=np.exp(result[1]))

# print("mu = ", result[1])
# print("sigma = ", result[0])

plt.rcParams["font.size"] = 18 
plt.figure(figsize = (5,3))
plt.hist(bdf_wave["sgh_list"], bins=10, range=(1,6),alpha = 1, color="gray", edgecolor='w')


plt.xlabel("Wave height (m)")
plt.ylabel("Count (times)")
plt.xlim(0.5,6.5)

# plt.plot(fit_x, fit_curve, c = "k")

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Wave_height.png", dpi=500, bbox_inches='tight')

plt.show

print(str(np.mean(bdf_wind["sgh_list"])) + "±" + str(np.std(bdf_wind["sgh_list"])))
print(min(bdf_wind["sgh_list"]))
print(max(bdf_wind["sgh_list"]))


# In[25]:


sgd_list_hist = np.histogram(bdf_wave["sgd_list"], bins = 18,range = (0,360))
plt.figure(figsize = (3,3))
plt.rcParams["font.size"] = 10 
theta = np.arange(0.0, 2 * np.pi,2 * np.pi/18)
radii = sgd_list_hist[0]
width = 2 * np.pi/18
bottom = 0

ax = plt.subplot(111, polar=True)
bars = ax.bar(theta, radii, width=width, bottom=0, align = 'edge',alpha = 1, color="lightgray", edgecolor='k')
ax.set_yticks([20,40,60])
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_thetagrids(np.rad2deg(np.linspace(0, 2*np.pi, 9)[1:]), 
                      labels=["NE", "E","SE" , "S", "SW", "W","NW", "N"],
                      fontsize=20)
ax.set_axisbelow(True)
plt.ylim(-40,80)

save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "Wave_direction.png", dpi=500, bbox_inches='tight')
plt.show()


# In[26]:


# 多重共線性の確認
from statsmodels.stats.outliers_influence import variance_inflation_factor as VIF

bdf_vif = np.array([bdf_env["wind_spd_list"], bdf_env["sgh_list"]]).T
VIF(bdf_vif,0)

