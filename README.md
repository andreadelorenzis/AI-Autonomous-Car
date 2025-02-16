# Self-driving car in 2D environment, using NEAT genetic algorithm

2D simulation to train an autonomous car that must navigate a series of increasingly challenging tracks. It uses neural networks that evolve through thanks to the NEAT genetic algorithm. For a complete overview of the simulation's implementation and the achieved results, check out the following <a href="report/report.pdf" target="_blank">report</a>.

<p align="center">
  <img src="imgs/video1.gif" alt="Splash screen" width="400"/>
</p>

### Modes
1. **Simulazione:** in the main file, you can choose a range of values for key algorithm parameters, then simulate the behavior for a set number of generations. A simulation is run for each variation. At the end, graphs are generated to show which variations yields the best results. The simulation can run on multiple tracks consecutively.
2. **Allenamento:** train the model on a set of parameters for an unlimited number of generations, with automatic saving of the best model.
3. **Validazione:** validate the previously trained model on one or more selected tracks.
4. **Modifica percorsi:** change the training and/or validation tracks.

Six tracks are used, which can be selected or deselected via the "Tracks" menu option.

<p align="center">
  <img src="imgs/circuito_1.png" alt="track 1" width="150" style="margin-right: 20px"/>
  <img src="imgs/circuito_2.png" alt="track 1" width="150" style="margin-right: 20px"/>
  <img src="imgs/circuito_3.png" alt="track 1" width="150" style="margin-right: 20px"/>
  <img src="imgs/circuito_4.png" alt="track 1" width="150" style="margin-right: 20px"/>
  <img src="imgs/circuito_5.png" alt="track 1" width="150"/>
</p>

## How to run the project

### 1. Clone the repository

First, clone the repository to your local system:
```bash
git clone https://github.com/tuo-utente/tuo-progetto.git
cd AI-Autonomous-Car
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies and run the program

```bash
pip install -r requirements.txt
python3 main.py
```

## Report
For more details on the simulation and the achieved results, refer to the following: <a href="report/report.pdf" target="_blank">full report</a>.