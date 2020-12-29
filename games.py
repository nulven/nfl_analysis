import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = None
games = None
teams = None
current = None
records = None

def import_data(year = 2019):
    global data
    global games
    global teams
    global current
    global records
    with open('games/reg_games_%s.csv' % (year), newline='') as f:
        data = pd.read_csv(f, low_memory=False)

    games = data[['game_id', 'home_team', 'away_team', 'week', 'season', 'home_score', 'away_score']]

    teams = set(data['home_team'])
    current = {team: (0, 0, 0) for team in teams}
    records = {team: [(0, 0, 0)]*18 for team in teams}


def compute_records(data):
    for i in range(1, 18):
        week = games[games.week.eq(i)]
        for index, game in week.iterrows():
            if game['home_score'] > game['away_score']:
                w, l, t = current[game['home_team']]
                records[game['home_team']][i] = (w+1, l, t)
                current[game['home_team']] = (w+1, l, t)

                w, l, t = current[game['away_team']]
                records[game['away_team']][i] = (w, l+1, t)
                current[game['away_team']] = (w, l+1, t)
            elif game['home_score'] < game['away_score']:
                w, l, t = current[game['home_team']]
                records[game['home_team']][i] = (w, l+1, t)
                current[game['home_team']] = (w, l+1, t)

                w, l, t = current[game['away_team']]
                records[game['away_team']][i] = (w+1, l, t)
                current[game['away_team']] = (w+1, l, t)
            else:
                w, l, t = current[game['home_team']]
                records[game['home_team']][i] = (w, l, t+1)
                current[game['home_team']] = (w, l, t+1)

                w, l, t = current[game['away_team']]
                records[game['away_team']][i] = (w, l, t+1)
                current[game['away_team']] = (w, l, t+1)

    # remove bye weeks
    for team, recs in records.items():
        for i, rec in enumerate(recs):
            if i > 0 and rec == (0, 0, 0):
                records[team][i] = records[team][i-1]

    return records

def percent(rec):
    if sum(rec) == 0:
        return 0
    else:
        return round((rec[0]+.5*rec[2])/sum(rec), 3)

def set_current(week):
    global current
    for team, recs in records.items():
        current.update({team: recs[week-1]})

def format_record(rec):
    return '(' + str(rec[0]) + '-' + str(rec[1]) + '-' + str(rec[2]) + ')'

def compute_diff(home, away):
    hrec = current[home]
    arec = current[away]
    return abs(((hrec[0]+.5*hrec[2]-hrec[1])-(arec[0]+.5*arec[2]-arec[1]))/2)

def evaluate(games, strategy, weeks=range(1, 18), print_games=False, print_misses=False):
    hits = 0
    misses = 0
    ties = 0
    diffs = []
    for i in weeks:
        set_current(i)
        week = games[games.week.eq(i)]
        weekly_diffs = []

        for index, game in week.iterrows():
            ht, at = game['home_team'], game['away_team']
            hs, asc = game['home_score'], game['away_score']

            if print_games:
                print(ht, format_record(current[ht]), hs, '-', at, format_record(current[at]), asc)

            winner = None
            if hs > asc:
                winner = ht
            elif hs < asc:
                winner = at

            if winner == strategy(ht, at):
                hits += 1
            elif not winner:
                ties += 1
            else:
                misses += 1

                diff = compute_diff(ht, at)
                weekly_diffs.append(diff)

                if print_misses:
                    print(ht, format_record(current[ht]), hs, '-', at, format_record(current[at]), asc)
                    print('Winner:     ', winner)
                    print('Prediction: ', strategy(ht, at))
                    print('Game Diff:  ', diff)
                    print()

        diffs.extend(weekly_diffs)


    return (hits, misses, ties), diffs

# strategies
def record_strategy(home, away):
    '''pick best record

    pick home team if tied
    '''
    return away if percent(current[away]) > percent(current[home]) else home

def sum_records(records):
    res = [(0, 0, 0)]*17
    for week in range(17):
        for season in records:
            w, l, t = res[week]
            record = season[week]
            res[week] = (w+record[0], l+record[1], t+record[2])
    return res

res = []
res_diffs = []
for year in range(2009, 2020):
    import_data(year)
    compute_records(data)
    season = []
    for i in range(1, 18):
        rec, diffs = evaluate(games, record_strategy, range(i, i+1), print_misses=True)
        res_diffs.extend(diffs)
        season.append(percent(rec))
        res.append(season)
        # print(format_record(rec))
        # print(percent(rec))
plt.hist(res_diffs, bins=np.arange(0, 10, 1))
plt.xticks(np.arange(0, 10, 1))


# res_perc = [percent(rec) for rec in sum_records(res)]


x = []
y = []
for i in range(len(res[0])):
    week = []
    for season in res:
        week.append(season[i])
    x.append(i+1)
    y.append(np.median(week))

#plt.plot(x, y)

'''
for season in res:
    plt.plot(range(1, 18), season)
'''

plt.show()
