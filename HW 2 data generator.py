# Problem 2.1
import h5py
import os 
import numpy as np
import json

# Generating behavioral data
SESSION_T = 120

time = np.linspace(0, SESSION_T, 12000)
x_noise = np.cumsum(0.2*(.5-np.random.rand(len(time))))
y_noise = np.cumsum(.5*(.5-np.random.rand(len(time))))
X = 10*np.sin(2.*np.pi*time/10.0) + x_noise
Y = 10*np.cos(6.21352*np.pi*time/10.0) + y_noise
stimulus_onset = np.linspace(10, SESSION_T - 10, 5) + np.random.normal(scale=4, size=5)
stimulus_offset = stimulus_onset + 2

DX = X[1:] - X[:-1]
DY = Y[1:] - Y[:-1]
norm = np.sqrt(DX**2 + DY**2)
DX /= norm
DY /= norm

DX = np.array(list(DX) + [DX[-1]])
DY = np.array(list(DY) + [DY[-1]])

x2_noise = np.cumsum(.02*(.5-np.random.rand(len(time))))
y2_noise = np.cumsum(.02*(.5-np.random.rand(len(time))))

X2 = DX - .2*DY + x2_noise
Y2 = DY + .2*DX + y2_noise

# Generate neural data
RATE = 20 # Hz
spike_times_1 = SESSION_T*np.random.rand(RATE*SESSION_T)
spike_times_2 = SESSION_T*np.random.rand(RATE*SESSION_T)

# Saving the data
h5data = h5py.File(os.path.join("data", "animal1_session1.h5"), 'a')

# Saving the behavioral data
h5data.create_group("behavior")
h5data.create_dataset("behavior/t", data=time)
h5data["behavior/t"].attrs["units"] = "s"
h5data.create_dataset("behavior/x", data=X)
h5data["behavior/x"].attrs["units"] = "cm"
h5data["behavior/x"].attrs["long_name"] = "animal position (X)"
h5data.create_dataset("behavior/y", data=Y)
h5data["behavior/y"].attrs["units"] = "cm"
h5data["behavior/y"].attrs["long_name"] = "animal position (Y)"

h5data.create_dataset("behavior/wsk_x", data=X2)
h5data["behavior/wsk_x"].attrs["units"] = "cm"
h5data["behavior/wsk_x"].attrs["long_name"] = "relative whisker position (X)"
h5data.create_dataset("behavior/wsk_y", data=Y2)
h5data["behavior/wsk_y"].attrs["units"] = "cm"
h5data["behavior/wsk_y"].attrs["long_name"] =  "relative whisker position (y)"

h5data.create_dataset("behavior/stim_on", data=stimulus_onset)
h5data["behavior/stim_on"].attrs["units"] = "s"
h5data["behavior/stim_on"].attrs["long_name"] = "stimulus onset"
h5data.create_dataset("behavior/stim_off", data=stimulus_offset)
h5data["behavior/stim_off"].attrs["units"] = "s"
h5data["behavior/stim_off"].attrs["long_name"] = "stimulus offset"

# Saving the ephys data
h5data.create_group("ephys")
cell1 = h5data.create_group("ephys/cell1")
cell1.create_dataset("spikes", data=spike_times_1)
cell1["spikes"].attrs["units"] = "s"
cell1["spikes"].attrs["long_name"] = "spike times"
cell2 = h5data.create_group("ephys/cell2")
cell2.create_dataset("spikes", data=spike_times_2)
cell2["spikes"].attrs["units"] = "s"
cell2["spikes"].attrs["long_name"] = "spike times"

h5data.close()

# Problem 2.2
# n/a

# Problem 2.3
# 6 animals
# 3 male, 3 female
# 4 sessions per animal (one week apart) 
# 2 attributes 

MALES = 3
FEMALES = 3
SESSIONS = 4

animal_names = SESSIONS*(['rat1'] + ['rat2'] + ['rat3'] + ['rat4'] + ['rat5'] + ['rat6'])
sex = SESSIONS*(MALES*['male'] + FEMALES*['female'])
base_age = np.ones(FEMALES + MALES)*20 + np.random.randint(0, 4, size=FEMALES+MALES)
age = np.hstack([base_age + i for i in range(0, 28, 7)])

def sex_one(sex):
    if sex == 'female':
        return 1
    else:
        return 0

strength = np.round(7 
                    + np.array([sex_one(s) - .1*a for s, a in zip(sex, age)]) 
                    + np.random.normal(size=SESSIONS*(FEMALES+MALES)))
dexterity = np.round(0
                     + np.array([.5*sex_one(s) + .2*a for s, a in zip(sex, age)]) 
                     + np.random.normal(size=SESSIONS*(FEMALES+MALES)))

if not os.path.exists(os.path.join("data", "behavioral_exp")):
    os.mkdir(os.path.join("data", "behavioral_exp"))
for n, s, ag, st, de in zip(animal_names, sex, age, strength, dexterity):
    file_name = f"{n}-p{int(ag)}.json"
    session = {'name': n, 'sex': s, 'age': ag, 'strength': st, 'dexterity': de}
    with open(os.path.join("data", "behavioral_exp", file_name), 'w') as f:
        json.dump(session, f)