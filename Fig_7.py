#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import japanize_matplotlib
from scipy import stats
plt.rcParams["font.size"] = 18 
pd.set_option('display.max_columns', 100)


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


bdf_wind = bdf.dropna(subset=['wind_spd_list'])
bdf_wind = bdf_wind.dropna(subset=['TO_dir_list2'])
bdf_wind = bdf_wind[bdf_wind['AIC_list'] == 1]

bdf_wave = bdf.dropna(subset=['sgh_list'])

bdf_env = bdf_wind.dropna(subset=['sgh_list'])

bdf = bdf.reset_index()
bdf_wind = bdf_wind.reset_index()
bdf_wave = bdf_wave.reset_index()
bdf_env = bdf_env.reset_index()

bdf_env["condition"] = ["Windy Highwave" if x>6 and y>2.5 else 
                        "Calm Highwave" if x<6 and y>2.5 else 
                        "Windy Lowwave" if x>6 and y<2.5 else 
                        "Calm Lowwave" for x,y in zip(bdf_env["wind_spd_list"],bdf_env["sgh_list"])]


# In[3]:


wind = bdf_env["wind_spd_list"]
wave = bdf_env["sgh_list"]
wave_x = np.arange(0.9,5.2,0.1)
alpha = 0.01
wind1 = 2
wind2 = 8


# In[4]:


# duration
n_data = len(bdf_env["running_time_list"])
df = n_data-2
mean_x = np.mean(bdf_env["sgh_list"])
coef1 = 10.17941
coef2 = -0.65248
coef3 = -1.29141
coef4 = 0.15805

model = coef1 + coef2*wind + coef3*wave  + coef4*wind*wave
y_err = model - bdf_env["running_time_list"]
t = stats.t.ppf(1-alpha, df=df) 
s_err = np.sum(y_err**2)
std_err = np.sqrt(s_err/(n_data-2))
std_x = np.std(bdf_env["sgh_list"])
conf = t*std_err/np.sqrt(n_data)*np.sqrt(1+((wave_x-mean_x)/std_x)**2)

g1_duration = coef1  + coef2*wind1 + coef3*wave_x  + coef4*wind1*wave_x
upper1_duration = g1_duration + abs(conf)
lower1_duration = g1_duration - abs(conf)

g2_duration = coef1  + coef2*wind2 + coef3*wave_x  + coef4*wind2*wave_x
upper2_duration = g2_duration + abs(conf)
lower2_duration = g2_duration - abs(conf)


# In[5]:


# speed
n_data = len(bdf_env["DPspd_list"])
df = n_data-2
mean_x = np.mean(bdf_env["sgh_list"])
coef1 = 10.94537 
coef2 = -0.53452
coef3 = -0.82545
coef4 = 0.08426

model = coef1 + coef2*wind + coef3*wave  + coef4*wind*wave
y_err = model - bdf_env["DPspd_list"]
t = stats.t.ppf(1-alpha, df=df) 
s_err = np.sum(y_err**2)
std_err = np.sqrt(s_err/(n_data-2))
std_x = np.std(bdf_env["sgh_list"])
conf = t*std_err/np.sqrt(n_data)*np.sqrt(1+((wave_x-mean_x)/std_x)**2)

g1_speed = coef1  + coef2*wind1 + coef3*wave_x  + coef4*wind1*wave_x
upper1_speed = g1_speed + abs(conf)
lower1_speed = g1_speed - abs(conf)

g2_speed = coef1  + coef2*wind2 + coef3*wave_x  + coef4*wind2*wave_x
upper2_speed = g2_speed + abs(conf)
lower2_speed = g2_speed - abs(conf)


# In[6]:


# number
n_data = len(bdf_env["flap_num2_list"])
df = n_data-2
mean_x = np.mean(bdf_env["sgh_list"])
coef1 = 19.0491 
coef2 = -1.5781 
coef3 = -3.4127 
coef4 = 0.3031 

model = coef1 + coef2*wind + coef3*wave  + coef4*wind*wave
y_err = model - bdf_env["flap_num2_list"]
t = stats.t.ppf(1-alpha, df=df) 
s_err = np.sum(y_err**2)
std_err = np.sqrt(s_err/(n_data-2))
std_x = np.std(bdf_env["sgh_list"])
conf = t*std_err/np.sqrt(n_data)*np.sqrt(1+((wave_x-mean_x)/std_x)**2)

g1_number = coef1  + coef2*wind1 + coef3*wave_x  + coef4*wind1*wave_x
upper1_number = g1_number + abs(conf)
lower1_number = g1_number - abs(conf)

g2_number = coef1  + coef2*wind2 + coef3*wave_x  + coef4*wind2*wave_x
upper2_number = g2_number + abs(conf)
lower2_number = g2_number - abs(conf)


# In[7]:


bdf_env_freq = bdf_env[bdf_env['flap_freq_list5'] < 0.555]
bdf_env_freq['flap_freq_list5'] = 1/bdf_env_freq['flap_freq_list5']


# In[8]:


# frequency

wind = bdf_env_freq["wind_spd_list"]
wave = bdf_env_freq["sgh_list"]

n_data = len(bdf_env_freq['flap_freq_list5'])
df = n_data-2
mean_x = np.mean(bdf_env_freq["sgh_list"])
coef1 = 2.29211 
coef2 = 0.04940 
coef3 = 0.18787
coef4 = -0.02967

model = coef1 + coef2*wind + coef3*wave  + coef4*wind*wave
y_err = model - bdf_env_freq['flap_freq_list5']
t = stats.t.ppf(1-alpha, df=df) 
s_err = np.sum(y_err**2)
std_err = np.sqrt(s_err/(n_data-2))
std_x = np.std(bdf_env_freq["sgh_list"])
conf = t*std_err/np.sqrt(n_data)*np.sqrt(1+((wave_x-mean_x)/std_x)**2)

g1_frequency = coef1  + coef2*wind1 + coef3*wave_x  + coef4*wind1*wave_x
upper1_frequency = g1_frequency + abs(conf)
lower1_frequency = g1_frequency - abs(conf)

g2_frequency = coef1  + coef2*wind2 + coef3*wave_x  + coef4*wind2*wave_x
upper2_frequency = g2_frequency + abs(conf)
lower2_frequency = g2_frequency - abs(conf)


# In[14]:


plt.rcParams["font.size"] = 16
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2,figsize = (8,7), sharex="col")

#duration
ax1.plot(wave_x,g1_duration,label="Wind speed 2m/s", c = "k", linestyle = "--")
ax1.fill_between(wave_x, lower1_duration, upper1_duration, color='gray', alpha=0.3)

ax1.plot(wave_x,g2_duration,label="Wind speed 8m/s", c = "k")
ax1.fill_between(wave_x, lower2_duration, upper2_duration, color='gray', alpha=0.3)

ax1.set_xticks([1,2,3,4,5])
ax1.set_ylim(3.3,8.5)
ax1.set_ylabel("Running duration (s)")
ax1.grid(ls = '--')

#speed
ax2.plot(wave_x,g1_speed, c = "k", linestyle = "--")
ax2.fill_between(wave_x, lower1_speed, upper1_speed, color='gray', alpha=0.3)

ax2.plot(wave_x,g2_speed, c = "k")
ax2.fill_between(wave_x, lower2_speed, upper2_speed, color='gray', alpha=0.3)

ax2.set_xticks([1,2,3,4,5])
ax2.set_ylabel("Running speed (m/s)")
ax2.grid(ls = '--')
ax2.set_ylim(5.2,)

#number

ax3.plot(wave_x,g1_number, c = "k", linestyle = "--")
ax3.fill_between(wave_x, lower1_number, upper1_number, color='gray', alpha=0.3)

ax3.plot(wave_x,g2_number, c = "k")
ax3.fill_between(wave_x, lower2_number, upper2_number, color='gray', alpha=0.3)

ax3.set_xlabel("Wave height (m)")
ax3.set_ylabel("Flapping number")
ax3.grid(ls = '--')
ax3.set_ylim(0,)

#frequency

ax4.plot(wave_x,g1_frequency, c = "k", linestyle = "--")
ax4.fill_between(wave_x, lower1_frequency, upper1_frequency, color='gray', alpha=0.3)

ax4.plot(wave_x,g2_frequency, c = "k")
ax4.fill_between(wave_x, lower2_frequency, upper2_frequency, color='gray', alpha=0.3)

ax4.set_xlabel("Wave height (m)")
ax4.set_ylabel("Flapping frequency (Hz)")
ax4.grid(ls = '--')

fig.legend(loc="lower center", bbox_to_anchor=(0.5, 0.93), ncol=2, fontsize = 14, frameon=False)

plt.tight_layout()
save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
plt.savefig(save_dir + "4glmmgraph.png", dpi=500, bbox_inches='tight')

plt.show

