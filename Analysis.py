### Totale Analyse

import numpy as np
import pandas as pd
import sklearn
from sklearn import metrics
import random
from scipy import spatial
import sys
from math import sqrt

### Inladen Archetypes + 100 vergelijkbare spelers

archetypes_pt = np.load("C:/Users/Maart/Desktop/Thesis/playtime20.npy")
archetypes_ach = np.load("C:/Users/Maart/Desktop/Thesis/merged20.npy")
data = np.load("C:/Users/Maart/Desktop/Thesis/dataframe_alltimeshort.npy")
top500 = np.load("C:/Users/Maart/Desktop/Thesis/top500.npy")


### Kiezen Speler voor aanbeveling en kies 10 vergelijkbare personen

def top_10_compared_users(user_number, archetypes):
    compared_user_list = []
    #for i in comparison_users_1000:
    for i in range(0,1074):    
        y = sklearn.metrics.pairwise.cosine_similarity(archetypes[i].reshape(1, -1), archetypes[user_number].reshape(1, -1))
        compared_user_list.append((y[0][0], i))
    compared_user_list.sort(reverse = True)
    if compared_user_list[0][0] == 1:
        del compared_user_list[0]
    top10list = []
    for i in range(0, len(compared_user_list)):
        if len(top10list) == 5:
            break
        else:
            top10list.append(compared_user_list[i][1])
    return(top10list)        

        
### Kiezen game voor reccommendation en op 0 zetten

def choose_rec_game(user_number):
    toplist = []
    for i in range(0, len(data[1073])):
        toplist.append((data[1073][i], i))        
    toplist.sort(reverse=True)
    top5list = []
    for i in range(0,5):
        top5list.append(toplist[i][1])
    pred_game = random.choice(top5list)   
    data[user_number][pred_game] = 0
    return(pred_game)


### Kiezen 100 games uit top500 voor ranking

def top101(top500, rec_game):
    top = []
    top.append(rec_game)
    while len(top) <51:
        x = random.choice(top500)
        if x in top:
            continue
        else:
            top.append(x)
    return(top)


### uitrekenen verwachte speeltijd per game

def top_L_ranking_pt(user_number, rec_game, archetypes, top, top10list):
    pred_playtimelist = []
    data = np.load("C:/Users/Maart/Desktop/Thesis/dataframe_alltimeshort.npy")
    for i in top:
        simlist = []
        simlist_times_playtime = []
        for x in top10list: 
            sim = sklearn.metrics.pairwise.cosine_similarity(archetypes[x].reshape(1, -1), archetypes[user_number].reshape(1, -1))
            #print(x,i,"^^", sim[0][0], data[x][i])
            pt_sim = sim[0][0] * data[x][i]
            simlist.append(sim[0][0])
            simlist_times_playtime.append(pt_sim)
        try:
            pred_pt = (float(sum(simlist_times_playtime)/sum(simlist)))
            #print("pred_pt:", pred_pt)
        except ZeroDivisionError:
            pred_pt = 0
        #except:
        #    print(sys.exc_info()[0])       
        try:
            pred_playtimelist.append((pred_pt, i))
        except TypeError:
            print("Typerror", i)
            pred_playtimelist.append((pred_pt, i))
    pred_playtimelist.sort(reverse=True)
    for i in pred_playtimelist:
        if i[1] == rec_game:
            rec_game_playtime = i[0]
    
    return(pred_playtimelist.index((rec_game_playtime, rec_game)))

# maken list met users om reccomendations voor te maken
def user_list(tot_users):
    user_number_list = []
    while len(user_number_list) < tot_users:
        number = random.randint(0,1073)
        if number in user_number_list:
            continue
        else:
            user_number_list.append(number)
    return(user_number_list)

user_number_list = user_list(100) 

def make_rec(toplist_number, archetypes, x):
    rec_tuple = [0,0]
    for i in user_number_list:
        data = np.load("C:/Users/Maart/Desktop/Thesis/dataframe_alltimeshort.npy")
        top10list = top_10_compared_users(i, archetypes)
        rec_game = choose_rec_game(i)
        top = top101(top500, rec_game)
        try:
            reccomendation = top_L_ranking_pt(i, rec_game, archetypes, top, top10list)
        except ValueError:
            continue
        if reccomendation < toplist_number:
            rec_tuple[1] += 1
            rec_tuple[0] += 1
        else:
            rec_tuple[0] += 1
        #print(rec_tuple[0], x)        
    return(rec_tuple)
    
    
user_number_list = user_list(100) 

achlist = []
ptlist = []


# hier doe ik 25 herhalingen van 100 recommendations

for i in range(0,400):
    user_number_list = user_list(100) 
    x = make_rec(20, archetypes_pt, i)
    y = make_rec(20, archetypes_ach, i)
    ptlist.append(x)
    achlist.append(y)

np.save("play", ptlist)
np.save("merge", achlist)
