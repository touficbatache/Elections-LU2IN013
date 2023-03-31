import csv
import itertools
import tkinter as tk

readmax = 3
essentials = dict()

with open('resultats-par-niveau-dpt-t1-france-entiere.csv') as csvfile:
    for row in itertools.islice(csv.DictReader(csvfile), readmax):
        print(row)
        print("\n")

