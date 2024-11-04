# Baggage Handling Simulation

This project simulates a baggage handling system, focusing on routing baggage items through intermediate queues and a backbone system (carousel). The simulation is built using [Salabim](https://salabim.org/), a discrete-event simulation library in Python. It includes infeed stations, intermediate queues, backbone resources, and sinks to model the flow of baggage in an airport setting.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Code Structure](#code-structure)
7. [Customization](#customization)

---

## Overview

The simulation models five infeed stations, each feeding into either a red or blue backbone resource (carousel) based on baggage assignment. Each infeed station directs baggage to specific intermediate queues, which may differ by direction (blue or red backbone). In particular, the West infeed station uses a unique queue, `"Queue West"`, where baggage is held for a set time before moving to an intermediate blue queue.

### Key Components
- **Baggage**: Represents each item of luggage and determines its assigned queue and backbone.
- **InfeedStation**: Generates baggage items and directs them to the appropriate intermediate queue.
- **Queues and Resources**: Includes both blue and red backbone resources, as well as sinks where baggage completes its journey.

## Features

- **Backbone Routing**: Simulates the choice between red and blue backbones for load balancing.
- **Queue Waiting Time**: Tracks and displays the average waiting time in each queue.
- **Animation**: Visualizes the movement of baggage through queues and backbones using Salabim's animation feature.

## Requirements

- Python 3.7 or later
- [Salabim](https://salabim.org/) library
- Optional: [Matplotlib](https://matplotlib.org/) (if you plan to visualize queue times)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/username/baggage-handling-simulation.git
   cd baggage-handling-simulation
