import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt

plays = []

def sim(params, drives):
    score = 0
    for _ in range(drives):
        score += sim_drive(params)
    return score

def sim_drive(params):
    drive = True
    down = 1
    los = 25.0
    first = 35.0
    score = 0
    while drive:
        play = round(gamma.rvs(*params), 1)
        plays.append(play)
        los = round(los + play, 1)
        down += 1
        if (los >= 100):
            score += 1
            drive = False
        elif (los >= first):
            down = 1
            first = round(los + 10.0, 1)
        elif (down == 4):
            drive = False
    return score
