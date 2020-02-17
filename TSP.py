#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 17:17:07 2020

@author: zackkingbackup
"""

import pandas as pd
import random
import math

    
def cost_c1_c2(cost_df, c1, c2, city_dict):
    cost = cost_df.at[c1, city_dict[c2]]
    return cost


def cost_tour(cost_df, tour, city_dict):
    
    total_cost = 0
    for city in range(len(tour) - 1):
        total_cost += cost_c1_c2(cost_df, tour[city], tour[city + 1],
                                 city_dict)
    
    return total_cost


def swap_cities(old_tour, start=-1, end=-1):
    
    c1, c2 = random.sample(range(len(old_tour)), 2)
    new_tour = old_tour.copy()
    new_tour[c1] = old_tour[c2]
    new_tour[c2] = old_tour[c1]
    
    if start >= 0:
        new_tour = [start] + new_tour
    if end >= 0:
        new_tour = new_tour + [end]
    return new_tour


def choose_new(old_cost, new_cost, T, r):
    delta = new_cost - old_cost
    P_new = math.exp(-delta/T)
    if r < P_new:
        return True
    return False


def sim_annealing(init_tour, cost_df, T_o, alpha, max_iter=5000, T_f=0,
                  start=-1, end=-1):
    
    old_tour = init_tour.copy()
    best_tour = init_tour.copy()
    
    # Initial cost?
    init_cost = cost_tour(df, init_tour, city_dict)
    old_cost = init_cost
    best_cost = init_cost
    
    # Run Simulated Annealing
    T = T_o
    count = 0
    
    while T > T_f and count < max_iter:
        # Generate a fresh solution
        sliced_old_tour = old_tour.copy()
        if start > -1:
            sliced_old_tour = sliced_old_tour[1:]
        if end > -1:
            sliced_old_tour = sliced_old_tour[:-1]
        new_tour = swap_cities(sliced_old_tour, start=start, end=end)
        
        # Will we accept it? - If its better, always
        new_cost = cost_tour(cost_df, new_tour, city_dict)
        if new_cost < old_cost:
            best_cost = new_cost
            best_tour = new_tour.copy()
            old_tour = new_tour.copy()
            old_cost = new_cost
        
        else:
            # Else, generate a random number
            r = random.random()
            
            # Accepted is a combination of temperature and how much
            # worse the new solution is.
            accepted = choose_new(old_cost, new_cost, T, r)
            
            if accepted:
                old_tour = new_tour
                old_cost = new_cost
                # don't update "best" values since this new tour
                # isn't any better
            
        # Adjust the temperature as per alpha
        T = T*alpha
        count += 1
        
    return best_tour, best_cost


def solution_df(best_tour, cost_df, city_dict):
    
    cities = [city_dict[best_tour[0]]]
    prior_stop = best_tour[0]
    costs = [0]
    for stop in best_tour[1:]:
        cities.append(city_dict[stop])
        costs.append(cost_c1_c2(cost_df, prior_stop, stop, city_dict))
        prior_stop = stop

    colnames = ['Stop'+str(idx) for idx in range(len(cities))]
    df = pd.DataFrame(columns=colnames, index=range(2))
    
    for idx in range(len(cities)):
        df.at[0,'Stop'+str(idx)] = cities[idx]
        df.at[1,'Stop'+str(idx)] = costs[idx]
        
    df['Total Cost'] = cost_tour(cost_df, best_tour, city_dict)
    return df

 
# Read in the Cost Matrix
df = pd.read_csv("DistanceMatrix.csv")
df = df.dropna()
df.rename( columns={'Unnamed: 0':'FromCity'}, inplace=True )

cities = list(df.columns)[1:]

# Create a mapping of indices to Cities so we can get the final
# tour back from a list of integers later
city_dict = {}
for i in range(len(cities)):
    city_dict[i] = cities[i]

# Make initial solution (full circle)
# Start City = End City = Brussels (3 in city_dict)
n_cities = len(cities)
init_tour = random.sample(range(n_cities),n_cities)

# Remove 3 from the middle and put it at the beginning and end
init_tour.remove(3)
init_tour = [3] + init_tour + [3]
T_o = 20000
T = T_o
T_f = 0
alpha = .9995
max_iter = 50000
# Use simulated annealing to come up with a solution
best_tour, best_cost = sim_annealing(init_tour, df, T_o, 
                                     alpha, max_iter, T_f,
                                     start=3, end=3)
partA = solution_df(best_tour, df, city_dict)
partA.to_csv("partA_solution.csv",index=False)

# Make another initial solution, but now we want to begin in 
# Brussels but not come back.
init_tourB = random.sample(range(n_cities),n_cities)
init_tourB.remove(3)
init_tourB = [3] + init_tourB

# Use simulated annealing to come up with a solution
best_tourB, best_costB = sim_annealing(init_tourB, df, T_o,
                                       alpha, max_iter, T_f,
                                       start=3)
partB = solution_df(best_tourB, df, city_dict)
partB.to_csv("partB_solution.csv",index=False)

      
