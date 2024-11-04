# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 16:35:31 2024

@author: miche
"""

import salabim as sim
import random  # For random choice between BB blue and BB red

sim.yieldless(False)

class Baggage(sim.Component):
    def __init__(self, assigned_sink, blue_queue, red_queue, number, assigned_backbone, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assigned_sink = assigned_sink
        self.blue_queue = blue_queue
        self.red_queue = red_queue
        self.number = number
        self.assigned_backbone = assigned_backbone
        self.name = f"Baggage {self.number}"

    def process(self):
        entry_time = self.env.now()
        
        # Check if the intermediate queue is "Queue West" and hold for 5 seconds if so
        if self.blue_queue == queue_west:
            # Enter Queue West, hold for 7 seconds, then move to Int. Q4 Blue
            self.enter(queue_west)
            yield self.hold(7)  # Hold for 7 seconds
            self.leave(queue_west)
            # After holding, move to "Int. Q4 Blue"
            intermediate_queue = blue_queues[3]  # Assuming "Int. Q4 Blue" is intended
            self.enter(intermediate_queue)
        else:
            intermediate_queue = self.blue_queue if self.assigned_backbone == "blue" else self.red_queue
            self.enter(intermediate_queue)
        
        # Backbone request and processing based on assigned backbone
        if self.assigned_backbone == "blue":
            yield self.request(backbone_blue_resource)
            self.leave(intermediate_queue)
            queue_time = self.env.now() - entry_time
            queue_times[self.blue_queue.name()].append(queue_time)
            self.enter(backbone_blue_queue)
            yield self.hold(2)
            self.leave(backbone_blue_queue)
            self.release(backbone_blue_resource)
        else:
            yield self.request(backbone_red_resource)
            self.leave(intermediate_queue)
            queue_time = self.env.now() - entry_time
            queue_times[self.red_queue.name()].append(queue_time)
            self.enter(backbone_red_queue)
            yield self.hold(2)
            self.leave(backbone_red_queue)
            self.release(backbone_red_resource)

        # Move to the assigned sink
        self.enter(self.assigned_sink)
        self.leave()
        
    def animate(self):
        # Display unique ID with color based on backbone assignment
        fillcolor = "red" if self.assigned_backbone == "red" else "blue"
        self.rectangle(text=str(self.number), fillcolor=fillcolor, outlinecolor=fillcolor, textcolor="black", width=20, height=20)



class InfeedStation(sim.Component):
    def __init__(self, sink, sink_id, infeed_queue, blue_queue, red_queue, interval_lookup, infeed_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sink = sink
        self.sink_id = sink_id
        self.infeed_queue = infeed_queue
        self.blue_queue = blue_queue
        self.red_queue = red_queue
        self.infeed_id = infeed_id
        self.interval_lookup = interval_lookup
        self.baggage_count = 0

    def process(self):
        while True:
            generation_interval = self.interval_lookup.get((self.infeed_id, self.sink_id), 5)
            self.baggage_count += 1
            assigned_backbone = random.choice(["red", "blue"])
            baggage = Baggage(self.sink, self.blue_queue, self.red_queue, self.baggage_count, assigned_backbone)
            baggage.enter(self.infeed_queue)
            yield self.hold(0.5)
            baggage.leave(self.infeed_queue)
            yield self.hold(generation_interval)


# Environment setup
env = sim.Environment()

# Backbone resources
backbone_blue_resource = sim.Resource('Backbone Blue', capacity=1)
backbone_red_resource = sim.Resource('Backbone Red', capacity=1)

# Backbone queues
backbone_blue_queue = sim.Queue('Backbone Queue Blue')
backbone_red_queue = sim.Queue('Backbone Queue Red')

# Sinks, Infeed Queues, and Intermediate Queues for each direction
sinks = [sim.Queue(f'Sink {i}') for i in range(1, 6)]
infeed_queues = [sim.Queue(f'Infeed Station {i}') for i in range(1, 6)]
blue_queues = [sim.Queue(f'Intermediate Queue {i} Blue') for i in range(1, 6)]
red_queues = [sim.Queue(f'Intermediate Queue {i} Red') for i in range(1, 6)]
queue_west = sim.Queue("Queue West")  # Renaming the West queue
blue_queues[0] = queue_west  # Assigning the renamed queue for West

# Define generation intervals
interval_lookup = {
    (1, 1): 5, (1, 2): 3, (1, 3): 4, (1, 4): 5, (1, 5): 6,
    (2, 1): 3, (2, 2): 2, (2, 3): 5, (2, 4): 4, (2, 5): 6,
    (3, 1): 4, (3, 2): 5, (3, 3): 2, (3, 4): 6, (3, 5): 3,
    (4, 1): 5, (4, 2): 4, (4, 3): 6, (4, 4): 3, (4, 5): 2,
    (5, 1): 6, (5, 2): 6, (5, 3): 3, (5, 4): 2, (5, 5): 4,
}

# Queue time tracking
queue_times = {q.name(): [] for q in blue_queues + red_queues}

# Set positions for visual elements
infeed_positions = [(100, 100), (100, 600), (400, 600), (700, 400), (400, 100)]
sink_positions = [(200, 100), (200, 600), (500, 600), (800, 400), (500, 100)]
blue_intermediate_positions = [(100, 175), (100, 525), (400, 525), (700, 325), (400, 175)]
red_intermediate_positions = [(200, 175), (200, 525), (500, 525), (800, 325), (500, 175)]

# Animate infeed stations, sinks, and intermediate queues
for i in range(5):
    infeed_queues[i].animate(x=infeed_positions[i][0], y=infeed_positions[i][1], title=f'Infeed Station {i + 1}')
    sinks[i].animate(x=sink_positions[i][0], y=sink_positions[i][1], title=f'Sink {i + 1}')
    blue_queues[i].animate(x=blue_intermediate_positions[i][0], y=blue_intermediate_positions[i][1], title=f'Int. Q {i + 1} Blue')
    if i > 0:
        red_queues[i].animate(x=red_intermediate_positions[i][0], y=red_intermediate_positions[i][1], title=f'Int. Q {i + 1} Red')

# Backbone queue positions
backbone_blue_queue.animate(x=425, y=400, title='Backbone Blue')
backbone_red_queue.animate(x=425, y=300, title='Backbone Red')

# Initialize each infeed station
for i in range(5):
    InfeedStation(
        sink=sinks[i], 
        sink_id=i + 1,
        infeed_queue=infeed_queues[i], 
        blue_queue=blue_queues[i],
        red_queue=red_queues[i] if i > 0 else blue_queues[i],  # West shares blue queue for simplicity
        interval_lookup=interval_lookup,
        infeed_id=i + 1
    )

# Enable animation and run simulation
env.animate(True)
env.run(20)

# Display average queue time for each intermediate queue
for queue_name, times in queue_times.items():
    non_zero_times = [time for time in times if time > 0]
    if non_zero_times:
        avg_queue_time = sum(non_zero_times) / len(non_zero_times)
        print(f"Average waiting time for {queue_name} (excluding zero wait times): {avg_queue_time:.2f}")
    else:
        print(f"No baggage items waited in {queue_name}")
