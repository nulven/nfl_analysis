import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

from sim import sim

teams = None
data = None
filtered_data = None
offensive_plays = None

def import_data(year=2019):
    global data
    global filtered_data
    global offensive_plays
    global teams
    with open('plays/reg_pbp_%s.csv' % year, newline='') as f:
        data = pd.read_csv(f, low_memory=False)
    filtered_data = data[['play_id', 'game_id', 'home_team', 'away_team', 'posteam', 'posteam_type', 'defteam', 'side_of_field', 'yardline_100', 'play_type', 'yards_gained', 'incomplete_pass', 'complete_pass', 'interception']]

    play_types = ['pass', 'run']
    offensive_plays = filtered_data[filtered_data.play_type.isin(play_types)]
    teams = set(filtered_data['home_team'])


def print_play(index=0, cols=[]):
    if len(cols) != []:
        d = data[cols]
    else:
        d = data
    for col, val in zip(list(d.columns), d.loc[index]):
        print(col, ' ', val)

#plays = data[data.posteam.eq('DAL') & data.complete_pass.eq(0.0) & data.play_type.eq('pass') & data.incomplete_pass.eq(0.0) & data.interception.eq(1.0)].index
#for play in plays:
#    print_play(play, ['desc', 'pass_attempt', 'play_type', 'incomplete_pass', 'complete_pass', 'yards_gained'])


def completion_percentage(plays):
    completions = plays[plays.play_type.eq('pass') & plays.complete_pass.eq(1.0)]
    incompletions = plays[plays.incomplete_pass.eq(1.0) | plays.interception.eq(1.0)]
    attempts = plays[plays.interception.eq(1.0) | plays.complete_pass.eq(1.0) | plays.incomplete_pass.eq(1.0)]
    return round(len(completions)/len(attempts), 3)


def color_gen():
    i = 0
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    while True:
        yield colors[i]
        i += 1
        if i == len(colors):
            i = 0


################
# play filters #
################
def regular(team):
    team_plays = offensive_plays[offensive_plays.posteam.eq(team)]

    plays = team_plays[team_plays['yards_gained'] > -20]

    return plays


def no_incompletions(team):
    team_plays = offensive_plays[offensive_plays.posteam.eq(team)]

    cp = completion_percentage(team_plays)

    team_plays_no_incompletions = team_plays[team_plays.incomplete_pass.eq(0.0) & team_plays.interception.eq(0.0)]
    p = team_plays_no_incompletions[team_plays_no_incompletions.play_type.eq('pass')]['yards_gained'].apply(lambda x: x*cp)
    team_plays_no_incompletions.loc[(team_plays_no_incompletions.play_type == 'pass'), 'yards_gained'] = p

    plays = team_plays_no_incompletions

    return plays


def fit(plays):
    return stats.gamma.fit(plays['yards_gained'], floc=-20)

def compute_ypp(team, func, year):
    plays = func(team)
    ypp = round(plays['yards_gained'].mean(), 1)
    params = fit(plays)
    return ypp, params, plays


def ypp(year=2019, func=regular):
    import_data(year)
    res = {}
    for team in teams:
        ypp, params, plays = compute_ypp(team, func, year)
        res.update({team: {'ypp': ypp, 'dist': params}})
    return res


def plot_plays(team, func):
    ypp, params, plays = compute_ypp(team, func)

    gen = color_gen()

    color = next(gen)
    bins = np.arange(-15, 51, 3)
    hist = plays['yards_gained'].hist(color=color, bins=bins, histtype=u'step', density=True)

    # n, bins = np.histogram(team_plays['yards_gained'], bins=bins)

    # n = [10**-10 if _ == 0 else _ for _ in n]
    # bins = bins[:-1]

    x = np.linspace(-15, 50, 100)

    y = stats.gamma.pdf(x, *params)
    plt.plot(x, y, color=color, label=team)

    plt.axvline(x=ypp, color=color)

    plt.xticks(np.arange(-15, 51, 5))
    plt.xlim([-15, 51])

    plt.legend()

'''
score = sim(fit(regular('KC')))
print(score)

score = sim(fit(regular('GB')))
print(score)

plot_plays('DAL', no_incompletions)
plot_plays('KC', no_incompletions)
plot_plays('DAL', regular)
plot_plays('KC', regular)
'''
