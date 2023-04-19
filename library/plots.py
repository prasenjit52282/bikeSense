import os
import glob
import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from scipy import stats

np.random.seed(101)

plt.rcParams.update({'font.size': 20})
# plt.rcParams["figure.figsize"] = (10, 8)
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

file_path = "/Users/ajay/Desktop/MTP/mtp-bikesense-app/Trails/TW/processed_data_100.csv"

data_split = {'Early\nMorning':[],'Morning':[],'Noon':[],'Afternoon':[]}
time_zone = ['Early\nMorning','Morning','Noon','Afternoon']

speed_rsi_dict = {'speed': np.array([]), 'rsi': np.array([])}

first_row = True
with open(file_path) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        hour = int(row[5].split(' ')[1].split(':')[0])
        time_split = int((hour -6) / 3)
        speed_rsi_dict['speed'] = np.append(speed_rsi_dict['speed'], float(row[13]))
        speed_rsi_dict['rsi'] = np.append(speed_rsi_dict['rsi'], float(row[7]))
        if time_split>3:
            continue

        data_split[time_zone[time_split]].append(3.6*float(row[13]))

def plot_timezone_speed():
    plt.boxplot(list(data_split.values()),showfliers=False,labels=time_zone)
    plt.ylim(0,80)
    plt.xlabel("Time Zone")
    plt.ylabel("Speed\n(km/hr)")
    plt.grid()
    plt.tight_layout()
    plt.savefig("/Users/ajay/Desktop/MTP/mtp-bikesense-app/Output/timezone_speed.png")
    plt.show()

def get_bin_count(norm_dist):
    q1 = norm_dist.quantile(0.25)
    q3 = norm_dist.quantile(0.75)
    iqr = q3 - q1
    bin_width = (2 * iqr) / (len(norm_dist) ** (1 / 3))
    bin_count = int(np.ceil((norm_dist.max() - norm_dist.min()) / bin_width)) 
    return bin_count                          

def plot_speed_rsi():

    df = pd.read_csv(file_path)
    df_new = df.sample(1000)[["speed","rsi"]].astype("float64")
    df_new["speed"] *= 3.6
    df_new = df_new[(np.abs(stats.zscore(df_new)) < 3).all(axis=1)]
    bin=np.max([get_bin_count(df_new["speed"]),get_bin_count(df_new["rsi"])])
   
    g = sns.jointplot(data = df_new, x = "speed", y = "rsi", space=0, kind = "reg", marker = '+', scatter_kws = {'alpha':0.2}, line_kws = {'color':'k','linestyle':'dashed', 'lw':1.5}, marginal_kws=dict(bins=bin,fill=True))
    g.plot_joint(sns.kdeplot, color="orange", zorder=0, levels=6)
    # g.plot_marginals(sns.rugplot, color="r",height=-.05, clip_on=False)
    # plt.tight_layout()
    plt.grid()
    plt.xlabel("Speed (km/hr)")
    plt.ylabel("RSI")
    plt.xticks(np.arange(0,100,20))
    plt.savefig("/Users/ajay/Desktop/MTP/mtp-bikesense-app/Output/rsi_speed.png", bbox_inches='tight')
    plt.show()

def process_trail(data):
    n=10
    data['speed']=data.speed.apply(lambda e: np.nan if e>120 else e).ffill()
    max_speed = data["speed"].groupby(np.arange(len(data))//n).max()
    return (max_speed[:-1].tolist(), max_speed[1:].tolist())


def plot_rash_driving():
    df = pd.read_csv(file_path)
    df.speed *= 3.6
    trails = df.groupby("trail_no")
    past_speeds = []
    future_speeds = []
    for trail_no, trail_data in trails:
        past_speed, future_speed = process_trail(trail_data)
        past_speeds.extend(past_speed)
        future_speeds.extend(future_speed)
    
    sns.regplot(x=past_speeds, y=future_speeds, line_kws = {'color':'k','linestyle':'dashed', 'lw':2})
    plt.xlabel("Past Max Speed(1 Km)")
    plt.ylabel("Future Max Speed(1 Km)")
    plt.grid()
    plt.tight_layout()
    plt.savefig("/Users/ajay/Desktop/MTP/mtp-bikesense-app/Output/past_future_speed.png", bbox_inches='tight')
    plt.show()

plot_rash_driving()