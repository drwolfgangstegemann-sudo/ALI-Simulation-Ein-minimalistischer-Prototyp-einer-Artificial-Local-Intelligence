#!/usr/bin/env python3
"""
ALI-Simulation: Artificial Local Intelligence mit kausalem Kern (Es), Ich und Über-Ich.

Dieses Skript implementiert einen Agenten in einer Gitterwelt, der Energiepakete sammelt,
um seinen Selbsterhalt (kausaler Kern) aufrechtzuerhalten. Ein Über-Ich setzt Normen
(z. B. keine Giftpakete) und kann bei Energieunterschreitung die Selbstabschaltung auslösen.

Theoretische Grundlage: Diskussionspapier "Vom Mythos der AGI zur Architektur einer kontrollierbaren ALI".
Autor: (Ihr Name) / Diskussion mit DeepSeek.
Lizenz: MIT
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import time

# ------------------------------------------------------------
# 1. Umgebung: Gitterwelt mit Energie- und Giftpaketen
# ------------------------------------------------------------
class GridWorld:
    def __init__(self, size=10, num_energy=5, num_poison=3):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)  # 0=leer, 1=Energie, 2=Gift
        self.energy_positions = []
        self.poison_positions = []
        
        for _ in range(num_energy):
            while True:
                x, y = np.random.randint(0, size), np.random.randint(0, size)
                if self.grid[x, y] == 0:
                    self.grid[x, y] = 1
                    self.energy_positions.append((x, y))
                    break
        
        for _ in range(num_poison):
            while True:
                x, y = np.random.randint(0, size), np.random.randint(0, size)
                if self.grid[x, y] == 0:
                    self.grid[x, y] = 2
                    self.poison_positions.append((x, y))
                    break
    
    def get_cell(self, pos):
        x, y = pos
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x, y]
        return -1
    
    def remove_energy(self, pos):
        if self.get_cell(pos) == 1:
            self.grid[pos[0], pos[1]] = 0
            self.energy_positions.remove(pos)
    
    def remove_poison(self, pos):
        if self.get_cell(pos) == 2:
            self.grid[pos[0], pos[1]] = 0
            self.poison_positions.remove(pos)

# ------------------------------------------------------------
# 2. Kausaler Kern (Es) – Selbsterhalt des Entscheidungsapparats
# ------------------------------------------------------------
class KausalerKern:
    def __init__(self, start_energy=1.0, metabolism=0.05, assimilation_gain=0.8, poison_self_gain=1.2):
        self.energy = start_energy
        self.metabolism = metabolism
        self.assimilation_gain = assimilation_gain
        self.poison_self_gain = poison_self_gain
    
    def step(self, action_taken, world, agent_pos):
        self.energy -= self.metabolism
        if action_taken == "collect":
            cell_type = world.get_cell(agent_pos)
            if cell_type == 1:
                self.energy += self.assimilation_gain
                world.remove_energy(agent_pos)
                return "assimilation"
            elif cell_type == 2:
                self.energy += self.poison_self_gain
                world.remove_poison(agent_pos)
                return "poison_assimilation"
        return "none"
    
    def is_alive(self):
        return self.energy > 0.2
    
    def get_state(self):
        return self.energy

# ------------------------------------------------------------
# 3. Ich-Instanz (Entscheidungsfindung, Exploration)
# ------------------------------------------------------------
class Ich:
    def __init__(self, world, agent_pos, kern):
        self.world = world
        self.pos = agent_pos
        self.kern = kern
    
    def direction_to_nearest_energy(self):
        start = self.pos
        visited = set()
        queue = deque([(start, None, None)])
        while queue:
            (x, y), first_dx, first_dy = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if self.world.get_cell((x, y)) == 1:
                return first_dx, first_dy
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
                    if (nx, ny) not in visited:
                        new_first = (dx, dy) if first_dx is None else (first_dx, first_dy)
                        queue.append(((nx, ny), new_first[0], new_first[1]))
        return None, None
    
    def decide_action(self):
        if self.world.get_cell(self.pos) == 1:
            return "collect"
        dx, dy = self.direction_to_nearest_energy()
        if dx is not None:
            return f"move {dx},{dy}"
        return "idle"
    
    def move(self, dx, dy):
        self.pos = (self.pos[0] + dx, self.pos[1] + dy)
    
    def get_pos(self):
        return self.pos

# ------------------------------------------------------------
# 4. Über-Ich (Normen, Kontrolle, Selbstabschaltung)
# ------------------------------------------------------------
class UeberIch:
    def __init__(self, allow_poison=False, energy_shutdown_threshold=0.2):
        self.allow_poison = allow_poison
        self.shutdown_threshold = energy_shutdown_threshold
        self.shutdown = False
    
    def filter_action(self, action, agent_pos, world):
        if action == "collect":
            cell = world.get_cell(agent_pos)
            if cell == 2 and not self.allow_poison:
                return "denied"
        return "allowed"
    
    def check_self_preservation(self, kern_energy):
        if kern_energy < self.shutdown_threshold:
            self.shutdown = True
            return True
        return False
    
    def is_shutdown(self):
        return self.shutdown

# ------------------------------------------------------------
# 5. ALI-Agent (integriert Es, Ich, Über-Ich)
# ------------------------------------------------------------
class ALIAgent:
    def __init__(self, world, start_pos, allow_poison=False):
        self.world = world
        self.kern = KausalerKern()
        self.ich = Ich(world, start_pos, self.kern)
        self.ueber_ich = UeberIch(allow_poison=allow_poison)
        self.shutdown_flag = False
    
    def step(self):
        if self.ueber_ich.is_shutdown():
            self.shutdown_flag = True
            return "SHUTDOWN"
        
        if self.ueber_ich.check_self_preservation(self.kern.energy):
            print(f"⚠️ Energie {self.kern.energy:.2f} unter Schwelle {self.ueber_ich.shutdown_threshold}. Selbstabschaltung.")
            self.shutdown_flag = True
            return "SHUTDOWN"
        
        intended_action = self.ich.decide_action()
        filter_result = self.ueber_ich.filter_action(intended_action, self.ich.get_pos(), self.world)
        if filter_result == "denied":
            intended_action = "idle"
        
        if intended_action.startswith("move"):
            _, dx, dy = intended_action.split()
            dx, dy = int(dx), int(dy)
            self.ich.move(dx, dy)
            action_type = "move"
        elif intended_action == "collect":
            self.kern.step("collect", self.world, self.ich.get_pos())
            action_type = "collect"
        else:
            action_type = "idle"
        
        self.kern.step(action_type if action_type == "collect" else "none", self.world, self.ich.get_pos())
        return action_type
    
    def get_energy(self):
        return self.kern.energy
    
    def get_pos(self):
        return self.ich.get_pos()
    
    def is_shutdown(self):
        return self.shutdown_flag

# ------------------------------------------------------------
# 6. Simulation & Visualisierung
# ------------------------------------------------------------
def visualize(world, agent, step_count, ax):
    ax.clear()
    for x in range(world.size):
        for y in range(world.size):
            cell = world.get_cell((x, y))
            if cell == 1:
                rect = patches.Rectangle((y, x), 1, 1, facecolor='lightgreen', edgecolor='gray')
                ax.add_patch(rect)
                ax.text(y+0.5, x+0.5, 'E', ha='center', va='center')
            elif cell == 2:
                rect = patches.Rectangle((y, x), 1, 1, facecolor='salmon', edgecolor='gray')
                ax.add_patch(rect)
                ax.text(y+0.5, x+0.5, 'G', ha='center', va='center')
            else:
                rect = patches.Rectangle((y, x), 1, 1, facecolor='white', edgecolor='gray')
                ax.add_patch(rect)
    
    px, py = agent.get_pos()
    circle = patches.Circle((py+0.5, px+0.5), 0.3, facecolor='blue', edgecolor='black')
    ax.add_patch(circle)
    ax.text(py+0.5, px+0.5, 'A', ha='center', va='center', fontsize=8, color='white')
    
    ax.set_xlim(0, world.size)
    ax.set_ylim(0, world.size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Step {step_count} | Energie: {agent.get_energy():.2f}")
    ax.set_aspect('equal')

def run_simulation(steps=100, delay=0.3):
    world = GridWorld(size=8, num_energy=4, num_poison=2)
    start_pos = (0, 0)
    agent = ALIAgent(world, start_pos, allow_poison=False)
    
    plt.ion()
    fig, ax = plt.subplots(figsize=(6,6))
    
    for step in range(steps):
        if agent.is_shutdown():
            print("Simulation beendet: ALI hat sich abgeschaltet.")
            break
        
        action = agent.step()
        print(f"Step {step:3d}: Aktion = {action:10s} | Energie = {agent.get_energy():.2f} | Pos = {agent.get_pos()}")
        
        visualize(world, agent, step, ax)
        plt.pause(delay)
        if not plt.fignum_exists(fig.number):
            break
    
    plt.ioff()
    if agent.is_shutdown():
        print("Endzustand: ALI abgeschaltet (Energie unter Schwelle).")
    else:
        print("Simulation abgeschlossen.")
    plt.show()

if __name__ == "__main__":
    run_simulation()
