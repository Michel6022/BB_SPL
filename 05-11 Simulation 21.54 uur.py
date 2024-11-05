# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:44:04 2024

@author: miche
"""

# -*- coding: utf-8 -*-
"""
Updated Simulation Script for Baggage Flow
@author: miche
"""
import salabim as sim
import random

sim.yieldless(False)

class Baggage(sim.Component):
    def __init__(self, assigned_sink, blue_queue, red_queue, number, assigned_backbone, infeed_id, sink_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assigned_sink = assigned_sink
        self.blue_queue = blue_queue
        self.red_queue = red_queue
        self.number = number
        self.assigned_backbone = assigned_backbone
        self.infeed_id = infeed_id
        self.sink_id = sink_id
        self.name = f"Baggage {self.number}"

    def process(self):
        entry_time = self.env.now()  # Record entry time

        # Special routing for Infeed 1 (West)
        if self.infeed_id == 1:
            self.enter(blue_queues[3])
            yield self.hold(5)
            self.leave(blue_queues[3])
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)

        # Special routing for Infeed 2 (E-hall)
        elif self.infeed_id == 2:
            yield from self._route_e_hall()

        # Special routing for Infeed 4 (D-hall)
        elif self.infeed_id == 4:
            yield from self._route_d_hall()
        
        # Special routing for Infeed 4 (D-hall)
       # elif self.infeed_id == 3:
        #    intermediate_queue = self.blue_queue if self.assigned_backbone == "blue" else self.red_queue
         #   yield from self._route_t2(intermediate_queue)

        else:
            intermediate_queue = self.blue_queue if self.assigned_backbone == "blue" else self.red_queue
            self.enter(intermediate_queue)
            if self.infeed_id == 5:
                yield from self._route_over_backbone(intermediate_queue)
            else:
                self.leave(intermediate_queue)
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)
        
        time_in_system = self.env.now() - entry_time
        print(f"Infeed ID: {self.infeed_id}, Sink ID: {self.sink_id}, Time in System: {time_in_system:.2f}")

    def _route_over_backbone(self, intermediate_queue):
        resource, queue = (backbone_blue_resource, backbone_blue_queue) if self.assigned_backbone == "blue" else (backbone_red_resource, backbone_red_queue)
        yield self.request(resource)
        self.leave(intermediate_queue)
        self.enter(queue)
        yield self.hold(5)
        self.leave(queue)
        self.release(resource)

        if self.sink_id in [1, 2]:
            ef_resource, ef_queue = (ef_buffer_blue_resource, ef_buffer_blue_queue) if self.assigned_backbone == "blue" else (ef_buffer_red_resource, ef_buffer_red_queue)
            yield self.request(ef_resource)
            self.enter(ef_queue)
            yield self.hold(5)
            self.leave(ef_queue)
            self.release(ef_resource)
    
    # def _route_t2(self, intermediate_queue):
    #     if self.sink_id == 1:
    #         yield from self._route_over_backbone(intermediate_queue)
    #     elif self.sink_id == 3:
    #             # Route over the backbone for sink 3
    #         yield from self._route_over_backbone(intermediate_queue)
    #     elif self.sink_id == 5:
    #         yield from self._route_over_backbone(intermediate_queue)
    #     else:
    #         # Direct route to sink if it's not 1, 3, or 5
    #         self.leave(intermediate_queue)

    
    def _route_e_hall(self):
        if self.sink_id == 1:
            ef_resource, ef_queue = (ef_buffer_blue_resource, ef_buffer_blue_queue) if self.assigned_backbone == "blue" else (ef_buffer_red_resource, ef_buffer_red_queue)
            yield self.request(ef_resource)
            self.enter(ef_queue)
            yield self.hold(5)
            self.leave(ef_queue)
            self.release(ef_resource)
        elif self.sink_id in [3, 5]:
            ef_resource, ef_queue = (ef_buffer_blue_resource, ef_buffer_blue_queue) if self.assigned_backbone == "blue" else (ef_buffer_red_resource, ef_buffer_red_queue)
            yield self.request(ef_resource)
            self.enter(ef_queue)
            yield self.hold(5)
            self.leave(ef_queue)
            self.release(ef_resource)
            backbone_resource, backbone_queue = (backbone_blue_resource, backbone_blue_queue) if self.assigned_backbone == "blue" else (backbone_red_resource, backbone_red_queue)
            yield self.request(backbone_resource)
            self.enter(backbone_queue)
            yield self.hold(5)
            self.leave(backbone_queue)
            self.release(backbone_resource)

    def _route_d_hall(self):
        """Handle routing specific to D-hall (Infeed 4)."""
        if self.sink_id in [1, 2]:
            # First route over the backbone loop
            backbone_resource, backbone_queue = (backbone_blue_resource, backbone_blue_queue) if self.assigned_backbone == "blue" else (backbone_red_resource, backbone_red_queue)
            yield self.request(backbone_resource)
            self.enter(backbone_queue)
            yield self.hold(5)
            self.leave(backbone_queue)
            self.release(backbone_resource)

            # Then route over the E/F loop
            ef_resource, ef_queue = (ef_buffer_blue_resource, ef_buffer_blue_queue) if self.assigned_backbone == "blue" else (ef_buffer_red_resource, ef_buffer_red_queue)
            yield self.request(ef_resource)
            self.enter(ef_queue)
            yield self.hold(5)
            self.leave(ef_queue)
            self.release(ef_resource)

        elif self.sink_id == 5:
            # Only route over the backbone loop
            backbone_resource, backbone_queue = (backbone_blue_resource, backbone_blue_queue) if self.assigned_backbone == "blue" else (backbone_red_resource, backbone_red_queue)
            yield self.request(backbone_resource)
            self.enter(backbone_queue)
            yield self.hold(5)
            self.leave(backbone_queue)
            self.release(backbone_resource)



class DirectionGenerator(sim.Component):
    def __init__(self, sink, infeed_queue, blue_queue, red_queue, interval, infeed_id, sink_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sink = sink
        self.infeed_queue = infeed_queue
        self.blue_queue = blue_queue
        self.red_queue = red_queue
        self.interval = interval
        self.infeed_id = infeed_id
        self.sink_id = sink_id
        self.baggage_count = 0

    def process(self):
        while True:
            self.baggage_count += 1
            assigned_backbone = random.choice(["red", "blue"])
            baggage = Baggage(
                self.sink, self.blue_queue, self.red_queue, self.baggage_count,
                assigned_backbone, self.infeed_id, self.sink_id
            )
            baggage.enter(self.infeed_queue)
            yield self.hold(0.5)
            baggage.leave(self.infeed_queue)
            yield self.hold(self.interval)


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

        for (infeed_id, sink_id), interval in interval_lookup.items():
            if infeed_id == self.infeed_id:
                DirectionGenerator(
                    sink=self.sink, 
                    infeed_queue=self.infeed_queue, 
                    blue_queue=self.blue_queue, 
                    red_queue=self.red_queue, 
                    interval=interval, 
                    infeed_id=self.infeed_id, 
                    sink_id=sink_id
                )


# Environment setup
env = sim.Environment()
backbone_blue_resource = sim.Resource('Backbone Blue Loop', capacity=100, monitor=True)
backbone_red_resource = sim.Resource('Backbone Red Loop', capacity=100, monitor=True)
ef_buffer_red_resource = sim.Resource('E/F Buffer Red', capacity=100, monitor=True)
ef_buffer_blue_resource = sim.Resource('E/F Buffer Blue', capacity=100, monitor=True)

backbone_blue_queue = sim.Queue('Backbone Queue Blue Loop')
backbone_red_queue = sim.Queue('Backbone Queue Red Loop')
ef_buffer_red_queue = sim.Queue('E/F Buffer Red')
ef_buffer_blue_queue = sim.Queue('E/F Buffer Blue')

sinks = [sim.Queue(f'Sink {i}') for i in range(1, 6)]
infeed_queues = [sim.Queue(f'Infeed Station {i}') for i in range(1, 6)]
blue_queues = [sim.Queue(f'Intermediate Queue {i} Blue') for i in range(1, 6)]
red_queues = [sim.Queue(f'Intermediate Queue {i} Red') for i in range(1, 6)]
queue_west = sim.Queue("Queue West")  
blue_queues[0] = queue_west

interval_lookup = {
    (1, 2): 4, (1, 3): 4, (1, 5): 4,
    (2, 1): 4, (2, 3): 4, (2, 5): 4,
    (3, 1): 4, (3, 2): 4, (3, 5): 4,
    (4, 1): 4, (4, 2): 4, (4, 3): 4, (4, 5): 4,
    (5, 1): 4, (5, 2): 4, (5, 3): 2
}

# Set positions for visual elements
infeed_positions = [(100, 100), (100, 600), (400, 600), (700, 400), (700, 100)]
sink_positions = [(200, 100), (200, 600), (500, 600), (800, 400), (800, 100)]
blue_intermediate_positions = [(100, 175), (100, 525), (400, 525), (700, 325), (700, 175)]
red_intermediate_positions = [(200, 175), (200, 525), (500, 525), (800, 325), (800, 175)]

# Animate infeed stations, sinks, and intermediate queues
for i in range(5):
    #infeed_queues[i].animate(x=infeed_positions[i][0], y=infeed_positions[i][1], title=f'Infeed Station {i + 1}')
    #sinks[i].animate(x=sink_positions[i][0], y=sink_positions[i][1], title=f'Sink {i + 1}')
    blue_queues[i].animate(x=blue_intermediate_positions[i][0], y=blue_intermediate_positions[i][1], title=f'Int. Q {i + 1} Blue')
    if i > 0:
        red_queues[i].animate(x=red_intermediate_positions[i][0], y=red_intermediate_positions[i][1], title=f'Int. Q {i + 1} Red')


# Animate the first infeed and sink as Infeed West and Outfeed West
infeed_queues[0].animate(x=infeed_positions[0][0], y=infeed_positions[0][1], title='Infeed West')
sinks[0].animate(x=sink_positions[0][0], y=sink_positions[0][1], title='Outfeed West')

# Animate the second infeed and sink as Infeed E-Hall and Outfeed E-Hall (top side)
infeed_queues[1].animate(x=infeed_positions[1][0], y=infeed_positions[1][1], title='Infeed E-Hall')
sinks[1].animate(x=sink_positions[1][0], y=sink_positions[1][1], title='Outfeed E-Hall')

# Animate the third infeed and sink as Infeed D-Hall and Outfeed D-Hall (right middle)
infeed_queues[2].animate(x=infeed_positions[2][0], y=infeed_positions[2][1], title='Infeed D-Hall')
sinks[2].animate(x=sink_positions[2][0], y=sink_positions[2][1], title='Outfeed D-Hall')

# Animate the fourth infeed and sink as Infeed T2 and Outfeed T2
infeed_queues[3].animate(x=infeed_positions[3][0], y=infeed_positions[3][1], title='Infeed T2')
sinks[3].animate(x=sink_positions[3][0], y=sink_positions[3][1], title='Outfeed T2')

# Animate the fifth infeed and sink as Infeed Zuid and Outfeed Zuid
infeed_queues[4].animate(x=infeed_positions[4][0], y=infeed_positions[4][1], title='Infeed Zuid')
sinks[4].animate(x=sink_positions[4][0], y=sink_positions[4][1], title='Outfeed Zuid')

ef_buffer_red_queue.animate(x=200, y=300, title='E/F Buffer Red')
ef_buffer_blue_queue.animate(x=200, y=400, title='E/F Buffer Blue')
backbone_red_queue.animate(x=425, y=300, title='Backbone Queue Red')
backbone_blue_queue.animate(x=425, y=400, title='Backbone Queue Blue')


for i in range(5):
    InfeedStation(
        sink=sinks[i],
        sink_id=i + 1,
        infeed_queue=infeed_queues[i],
        blue_queue=blue_queues[i],
        red_queue=red_queues[i] if i > 0 else blue_queues[i],
        interval_lookup=interval_lookup,
        infeed_id=i + 1
    )

env.animate(True)
env.run(20)
