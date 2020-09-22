import datetime
import numpy as np
import seaborn as sns
import scipy.ndimage
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d
from matplotlib.ticker import MaxNLocator

colors = ['#bb3900', '#007cbf', '#d29900', '#7cc300', '#c900ba', '#318a6a', '#005c9d']

def plot_time_vs_year(df, ax, color=colors[1], s=0.5, title=''):
    '''
    This function will depict the number of emails by time of day per year.
    '''
    df.plot.scatter('year', 'time_of_day', s=s, \
                          alpha=0.6, ax=ax, color=color, rot=90)
    ax.set_ylim(0, 24)
    
    ax.yaxis.set_major_locator(MaxNLocator(8))
    ax.set_yticklabels([datetime.datetime.strptime\
                        (str(int(np.mod(ts, 24))), "%H").\
                        strftime("%I %p") for ts in ax.get_yticks()]);
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(title)
    ax.grid(ls=':', color='k')
    return ax

def plot_avg_per_day(df, ax, label=None, dt=0.3, **kwargs):
    '''
    This function will plot the average number of emails sent per day.
    '''
    year = df.year.values
    duration = year.max() - year.min()
    bins = int(duration/dt)
    weights = 1 / (np.ones_like(year) * dt * 365.25)
    ax.hist(year, bins=bins, weights=weights, label=label, **kwargs);
    ax.grid(ls=':', color='k')
    
def plot_avg_per_hour(df, ax, label=None, dt=1,\
                      smooth=False, weight_func=None, **kwargs):
    '''
    This function will plot the average number of emails sent per hour.
    '''
    time_day = df.time_of_day.values
    year = df.year.values
    duration_y = year.max() - year.min()
    duration_day = time_day.max() - time_day.min()
    bins = int(duration_day / dt)
    
    if weight_func is None:
        weights = 1 / (np.ones_like(time_day) * duration_y * 365.25 / dt)
    else:
        weights = weight_func(df)
        
    if smooth:
        hst, xedges = np.histogram(time_day, bins=bins, weights=weights);
        x = np.delete(xedges, -1) + 0.5*(xedges[1] - xedges[0])
        hst = ndimage.gaussian_filter(hst, sigma=0.75)
        f = interp1d(x, hst, kind='cubic')
        x = np.linspace(x.min(), x.max(), 10000)
        hst = f(x)
        ax.plot(x, hst, label=label, **kwargs)
    else:
        ax.hist(time_day, bins=bins, weights=weights, label=label, **kwargs);
        
    ax.grid(ls=':', color='k')
    orientation = kwargs.get('orientation')
    
    if orientation is None or orientation == 'vertical':
        ax.set_xlim(0, 24)
        ax.xaxis.set_major_locator(MaxNLocator(8))    
        ax.set_xticklabels([datetime.datetime.\
                            strptime(str(int(np.mod(ts, 24))), "%H").\
                            strftime("%I %p") for ts in ax.get_xticks()]);
    elif orientation == 'horizontal':
        ax.set_ylim(0, 24)
        ax.yaxis.set_major_locator(MaxNLocator(8))
        ax.set_yticklabels([datetime.datetime.\
                            strptime(str(int(np.mod(ts, 24))), "%H").\
                            strftime("%I %p") for ts in ax.get_yticks()]);
        
def plot_time_of_day(df, starters, replies, forwards, ylabel='(overall)'):
    '''
    This function will plot the average number of emails sent per hour across weekdays.
    '''
    patches = []
    plt.figure(figsize=(10,6))
    ax = plt.subplot(111)  
    
    for count, weekday in enumerate(df.day_of_week.unique()):
        df_starters = starters[starters.day_of_week==weekday]
        df_replies = replies[replies.day_of_week==weekday]
        df_forwards = forwards[forwards.day_of_week==weekday]

        weights = np.ones(len(df_starters)) / len(starters)
        wfunc = lambda x: weights
        plot_avg_per_hour(df_starters, ax, dt=1, smooth=True, color=colors[count],\
                          alpha=0.8, lw=3, weight_func=wfunc)                   

        weights = np.ones(len(df_replies)) / len(replies)
        wfunc = lambda x: weights
        plot_avg_per_hour(df_replies, ax, dt=1, smooth=True, color=colors[count],\
                          alpha=0.8, lw=2, ls='--', weight_func=wfunc)

        weights = np.ones(len(df_forwards)) / len(forwards)
        wfunc = lambda x: weights
        plot_avg_per_hour(df_forwards, ax, dt=1, smooth=True, color=colors[count],\
                          alpha=0.8, lw=2, ls='-.', weight_func=wfunc)
        
        patches.append(mpatches.Patch(color=colors[count], label=weekday + 's')) 

    ax.set_ylabel(f'Fraction of weekly emails per hour {ylabel}')
    plt.legend(handles=patches, title='Legend', bbox_to_anchor=(1.05, 1),\
               loc='upper left')
    

class TriplePlot:
    '''
    This class will plot emails by time of day and year. It will also plot 
    the average number of emails sent per day and per hour.
    '''
    def __init__(self):
        gs = gridspec.GridSpec(6, 6)
        self.ax1 = plt.subplot(gs[2:6, :4])
        self.ax2 = plt.subplot(gs[2:6, 4:6], sharey=self.ax1)
        plt.setp(self.ax2.get_yticklabels(), visible=False);
        self.ax3 = plt.subplot(gs[:2, :4])
        plt.setp(self.ax3.get_xticklabels(), visible=False);
        
    def plot(self, df, color=colors[2], alpha=0.8, markersize=0.5,\
             yr_bin=0.1, hr_bin=0.5):
        plot_time_vs_year(df, self.ax1, color=color, s=markersize)
        plot_avg_per_hour(df, self.ax2, dt=hr_bin, color=color, alpha=alpha, orientation='horizontal')
        self.ax2.set_xlabel('Average number of emails per hour')
        plot_avg_per_day(df, self.ax3, dt=yr_bin, color=color, alpha=alpha)
        self.ax3.set_ylabel('Average number of emails per day')
        

'''
REFERENCE
- Mukhiya, Suresh Kumar, and Usman Ahmed. Hands-On Exploratory Data Analysis with Python. 
Birmingham: Packt Publishing Ltd., 2020.
'''
