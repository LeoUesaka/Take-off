#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pyper
import japanize_matplotlib
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


# In[4]:


r.assign("bdf_wave",bdf_wave)


# In[5]:


print(r("result1 <- lmer(running_time_list ~ sgh_list + (1|ID), data = bdf_wave)"))
print(r("summary(result1)"))


# In[6]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
wavex = np.arange(1.1,5.4,0.1)
duration_wave = intercept + coef1*wavex


# In[7]:


print(r("result1 <- lmer(DPspd_list ~ sgh_list + (1|ID), data = bdf_wave)"))
print(r("summary(result1)"))


# In[8]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
wavex = np.arange(1.1,5.4,0.1)
speed_wave = intercept + coef1*wavex


# In[9]:


print(r("result1 <- lmer(flap_num2_list ~ sgh_list + (1|ID), data = bdf_wave)"))
print(r("summary(result1)"))


# In[10]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
wavex = np.arange(1.1,5.4,0.1)
number_wave = intercept + coef1*wavex


# In[11]:


r.assign("bdf_wind",bdf_wind)


# In[12]:


print(r("result1 <- lmer(running_time_list ~ wind_spd_list + (1|ID), data = bdf_wind)"))
print(r("summary(result1)"))


# In[13]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
windx = np.arange(0,17,1)
duration_wind = intercept + coef1*windx


# In[14]:


print(r("result1 <- lmer(DPspd_list ~ wind_spd_list + (1|ID), data = bdf_wind)"))
print(r("summary(result1)"))


# In[15]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
windx = np.arange(0,17,1)
speed_wind = intercept + coef1*windx


# In[16]:


print(r("result1 <- lmer(flap_num1_list ~ wind_spd_list + (1|ID), data = bdf_wind)"))
print(r("summary(result1)"))


# In[17]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
windx = np.arange(0,17,1)
number_wind = intercept + coef1*windx


# In[18]:


# bdf_wave['flap_freq_list5'] = 1/bdf_wave['flap_freq_list5']
# bdf_wave = bdf_wave[bdf_wave['flap_freq_list5'] > 1.8]
bdf_wave_freq = bdf_wave[bdf_wave['flap_freq_list5'] < 0.555]
bdf_wave_freq['flap_freq_list5'] = 1/bdf_wave_freq['flap_freq_list5']
r.assign("bdf_wave_freq",bdf_wave_freq)


# In[19]:


print(r("result1 <- lmer(flap_freq_list5 ~ sgh_list + (1|ID), data = bdf_wave_freq)"))
print(r("summary(result1)"))


# In[20]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
wavex = np.arange(1.1,5.4,0.1)
frequency_wave = intercept + coef1*wavex


# In[21]:


# bdf_wind['flap_freq_list5'] = 1/bdf_wind['flap_freq_list5']
# bdf_wind = bdf_wind[bdf_wind['flap_freq_list5'] > 1.8]
bdf_wind_freq = bdf_wind[bdf_wind['flap_freq_list5'] < 0.555]
bdf_wind_freq['flap_freq_list5'] = 1/bdf_wind_freq['flap_freq_list5']
r.assign("bdf_wind_freq",bdf_wind_freq)


# In[22]:


print(r("result1 <- lmer(flap_freq_list5 ~ wind_spd_list + (1|ID), data = bdf_wind_freq)"))
print(r("summary(result1)"))


# In[23]:


coefs = r.get("coef(summary(result1))")
intercept = coefs[0][0]
coef1 = coefs[1][0]
windx = np.arange(0,17,1)
frequency_wind = intercept + coef1*windx


# In[40]:


plt.rcParams["font.size"] = 16
fig = plt.figure(figsize = (8,10))
fig, ((ax1, ax5), (ax2, ax6),(ax3, ax7),(ax4, ax8)) = plt.subplots(4, 2,figsize = (8,10), sharex="col", sharey="row")

#wave-duration
ax1.scatter(bdf_wave["sgh_list"],bdf_wave["running_time_list"], color = "dimgray" )
ax1.plot(wavex,duration_wave, color = "k")
ax1.set_xlim(0.9,5.5)
ax1.set_ylim(-0.5,11)
ax1.set_yticks([0,4,8])
ax1.set_ylabel("Running\nduration (s)", fontsize=18)
ax1.text(0.76, 0.86,"n=299", transform=ax1.transAxes, fontsize = 14)
#wave-speed
ax2.scatter(bdf_wave["sgh_list"],bdf_wave["DPspd_list"], color = "dimgray" )
ax2.plot(wavex,speed_wave, color = "k")
ax2.set_ylim(-0.5,14)
ax2.set_yticks([0,4,8,12])
ax2.set_ylabel("Running\nspeed (m/s)", fontsize=18)
ax2.text(0.76, 0.86,"n=299", transform=ax2.transAxes, fontsize = 14)
#wave-number
ax3.scatter(bdf_wave["sgh_list"],bdf_wave["flap_num2_list"], color = "dimgray")
ax3.plot(wavex,number_wave, color = "k")
ax3.set_yticks([0,10,20,30,40])
ax3.set_ylabel("Flapping\nnumber")
ax3.set_ylim(-0.5,41)
ax3.text(0.76, 0.86,"n=299", transform=ax3.transAxes, fontsize = 14)
#wave-frequency
ax4.scatter(bdf_wave_freq["sgh_list"],bdf_wave_freq["flap_freq_list5"], color = "dimgray")
# ax4.plot(x,y, color = "k", linestyle = "--")
ax4.set_xlabel("Wave height (m)")
ax4.set_xticks([1,2,3,4,5])
ax4.set_ylabel("Flapping\nfrequency (Hz)")
ax4.set_yticks([2,2.5,3,3.5])
ax4.text(0.76, 0.86,"n=283", transform=ax4.transAxes, fontsize = 14)
#wind-duration
ax5.scatter(bdf_wind["wind_spd_list"],bdf_wind["running_time_list"], color = "dimgray")
ax5.plot(windx,duration_wind, color = "k")
ax5.text(0.76, 0.86,"n=427", transform=ax5.transAxes, fontsize = 14)
#wind-speed
ax6.scatter(bdf_wind["wind_spd_list"],bdf_wind["DPspd_list"], color = "dimgray")
ax6.plot(windx,speed_wind, color = "k")
ax6.text(0.76, 0.86,"n=427", transform=ax6.transAxes, fontsize = 14)
#wind-number
ax7.scatter(bdf_wind["wind_spd_list"],bdf_wind["flap_num2_list"], color = "dimgray")
ax7.plot(windx,number_wind, color = "k")
ax7.text(0.76, 0.86,"n=427", transform=ax7.transAxes, fontsize = 14)
#wind-frequency
ax8.scatter(bdf_wind_freq["wind_spd_list"],bdf_wind_freq["flap_freq_list5"], color = "dimgray")
ax8.plot(windx,frequency_wind, color = "k")
ax8.set_xlabel("Wind speed (m/s)")
ax8.text(0.76, 0.86,"n=407", transform=ax8.transAxes, fontsize = 14)

save_dir = "C:\\Users\\butte\\Desktop\\Takeing off of seabirds under various wind and wave conditions\\fig&tables\\工場\\"
# plt.savefig(save_dir + "8figures.png", dpi=500, bbox_inches='tight')

plt.show

