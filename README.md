# Baggage Flow Simulation

This project simulates baggage flow within an airport baggage handling system using Salabim. The simulation tracks baggage moving from infeed stations, through intermediate queues and backbones (blue and red), to various sink destinations, allowing analysis of route performance and load balancing.

## Key Components

- **Environment**: The Salabim environment controls the timing and animation of the simulation.
- **Baggage**: Each baggage item has properties such as assigned sink, backbone color, and infeed ID, representing different routes through the system.
- **DirectionGenerator**: Generates baggage items at defined intervals, assigning each item a route through a backbone color and infeed station.
- **InfeedStation**: Sets up direction generators at each infeed station, assigning baggage items to routes based on a lookup table.
- **Resources and Queues**: Simulates different sections of the baggage system, such as the blue and red backbone loops, E/F buffers, and link resources connecting sections.

## Simulation Details

### Classes and Functions

1. **Baggage**: Represents individual baggage items. The `process` method simulates routing the baggage item through queues and resources, updating statistics on route counts and times.
   - **Routes**:
     - `_route_zuid`, `_route_west`, `_route_t2`, `_route_e_hall`, `_route_d_hall`: Define paths for each baggage item based on infeed station and sink destination.
   - **Route Statistics**: Collects stats for each infeed-to-sink route and prints them at the end of the simulation.

2. **DirectionGenerator**: Generates baggage items at specified intervals and assigns each item a route with a random backbone color.

3. **InfeedStation**: Initializes DirectionGenerators, linking each infeed to specific intervals based on the `interval_lookup` table, which maps each (infeed, sink) combination to an interval.

### Resources and Queues

- **Backbone Resources and Queues**: Separate resources and queues represent the blue and red backbones.
- **Buffers and Links**: Intermediate resources simulate buffers and links between different stations.
- **Infeed Queues**: Each infeed station has a designated queue, along with intermediate blue and red queues.

### Route and Load Balancing

Each infeed ID follows a specific route and backbone color, with statistics collected for each infeed-to-sink combination. These stats help analyze load balancing across routes.

### Animation

The simulation animates the movement of baggage items between stations. Positions and labels are provided for visual tracking of the infeed stations, sinks, and intermediate queues.

### Running the Simulation

- Run the simulation with `env.run(duration)`, where `duration` (e.g., 50) is the simulation time.
- Enable animations with `env.animate(True)` if using Salabim’s visual mode.
- **Note**: Adjust the `interval_lookup` dictionary to set different intervals for each infeed-sink route if needed.

### Output

The script prints route statistics after simulation, showing:
- **Count**: Number of baggage items processed for each route.
- **Average Time**: Average time taken by baggage items for each route.

### Requirements

- Python with Salabim library installed.

### Usage

1. Clone this repository.
2. Use Python 3.12.7
3. Use Salabim 24.0.15
4. Install dependencies:
   ```bash
   pip install salabim
