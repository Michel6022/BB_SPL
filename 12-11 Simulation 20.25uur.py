# -*- coding: utf-8 -*-
"""
Updated Simulation Script for Baggage Flow
@author: miche
"""
import salabim as sim
import random

sim.yieldless(False)

class Baggage(sim.Component):
    # Class-level dictionary to store route statistics
    route_stats = {
        infeed: {sink: {"count": 0, "total_time": 0} for sink in range(1, 6)}
        for infeed in range(1, 6)
    }

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
        entry_time = self.env.now()
        intermediate_queue = self.blue_queue if self.assigned_backbone == "blue" else self.red_queue
        self.enter(intermediate_queue)

        # Determine the route based on infeed_id
        if self.infeed_id == 1:
            yield from self._route_west(intermediate_queue)
        elif self.infeed_id == 2:
            yield from self._route_e_hall(intermediate_queue)
        elif self.infeed_id == 3:
            yield from self._route_d_hall(intermediate_queue)
        elif self.infeed_id == 4:
            yield from self._route_t2(intermediate_queue)
        elif self.infeed_id == 5:
            yield from self._route_zuid(intermediate_queue)
        else:
            self.leave(intermediate_queue)
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)
        
        # Calculate time in system and update statistics
        time_in_system = self.env.now() - entry_time
        self._update_stats(time_in_system)
        print(f"{self.name}: Infeed ID: {self.infeed_id}, Sink ID: {self.sink_id}, Time in System: {time_in_system:.2f}")

    def _update_stats(self, time_in_system):
        stats = Baggage.route_stats[self.infeed_id][self.sink_id]
        stats["count"] += 1
        stats["total_time"] += time_in_system

    def _route_west(self, intermediate_queue):
        if self.assigned_backbone == "blue":
            yield from self._move_through_link(link_10040_resource, link_10040_queue[0], hold_time=5)
        else:
            yield from self._move_through_link(link_10040_resource, link_10040_queue[0], hold_time=5)
        
        self.enter(blue_queues[3])  # Move to intermediate queue for T2
        yield from self._route_t2(blue_queues[3])

    def _route_e_hall(self, intermediate_queue):
        if self.assigned_backbone == "blue":
            yield from self._move_through_link(link_10034_resource, link_10034_queue[0], hold_time=5)
        else:
            yield from self._move_through_link(link_10035_resource, link_10035_queue[0], hold_time=5)
           
        yield from self._route_ef()
        
        #Route to West not via BB loop
        if self.sink_id == 1:
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
        
        #Route to D-Hall and Zuid via Backbone loop
        elif self.sink_id in [3, 5]:
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10611_1_resource, link_10611_1_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10621_1_resource, link_10621_1_queue[0], hold_time=5)
            
            yield from self._route_backbone()
        
            if self.sink_id == 3:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10635_resource, link_10635_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10645_resource, link_10645_queue[0], hold_time=5)
                           
        self.enter(self.assigned_sink)
        self.leave(self.assigned_sink)
      
            

    def _route_d_hall(self, intermediate_queue):
        if self.assigned_backbone == "blue":
            yield from self._move_through_link(link_10009_resource, link_10008_queue[0], hold_time=5)
        else:
            yield from self._move_through_link(link_10008_resource, link_10008_queue[0], hold_time=5)

        
        # Route to West and E-Hall via Backbone loop and EF Buffer 
        if self.sink_id in [1, 2]:
            yield from self._route_backbone()
            
            # Move through the appropriate link after the backbone
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=5)
            
            yield from self._route_ef()
            
            if self.sink_id == 1:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                    
            if self.sink_id == 2:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=5)

        # Route to Zuid directly go in sink 
        elif self.sink_id == 5:
            yield from self._route_backbone()
         
        self.enter(self.assigned_sink)
        self.leave(self.assigned_sink)

    def _route_t2(self, intermediate_queue):
        if self.assigned_backbone == "blue":
            yield from self._move_through_link(link_10825_resource, link_10825_queue[0], hold_time=5)
        else:
            yield from self._move_through_link(link_10826_resource, link_10826_queue[0], hold_time=5)
        
        yield from self._route_backbone()
        
        # Route to West and E-Hall via Backbone loop and EF Buffer 
        if self.sink_id in [1, 2]:            
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=5)
            
            yield from self._route_ef()
            
            if self.sink_id == 1:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                    
            if self.sink_id == 2:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=5)
            
        elif self.sink_id == 3:
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10826_resource, link_10826_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10825_resource, link_10825_queue[0], hold_time=5)
         
        self.enter(self.assigned_sink)
        self.leave(self.assigned_sink)

    def _route_zuid(self, intermediate_queue):
        yield from self._route_backbone()

        # Route to West and E-Hall via Backbone loop and EF Buffer 
        if self.sink_id in [1, 2]:            
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=5)
            
            yield from self._route_ef()
            
            if self.sink_id == 1:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                    
            if self.sink_id == 2:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=5)
                else:
                    yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=5)
                    
        if self.sink_id == 3:
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10635_resource, link_10635_queue[0], hold_time=5)
            else:
                yield from self._move_through_link(link_10645_resource, link_10645_queue[0], hold_time=5)
            
        self.enter(self.assigned_sink)
        self.leave(self.assigned_sink)
        
    def _route_backbone(self):
        backbone_resource = backbone_blue_resource if self.assigned_backbone == "blue" else backbone_red_resource
        backbone_queue = backbone_blue_queue if self.assigned_backbone == "blue" else backbone_red_queue
        yield self.request(backbone_resource)
        self.enter(backbone_queue)
        yield self.hold(5)
        self.leave(backbone_queue)
        self.release(backbone_resource)

    def _route_ef(self):
        ef_resource = ef_buffer_blue_resource if self.assigned_backbone == "blue" else ef_buffer_red_resource
        ef_queue = ef_buffer_blue_queue if self.assigned_backbone == "blue" else ef_buffer_red_queue
        yield self.request(ef_resource)
        self.enter(ef_queue)
        yield self.hold(5)
        self.leave(ef_queue)
        self.release(ef_resource)


    def _move_through_link(self, resource, queue, hold_time=5):
        """Helper method to handle movement through a specific link with hold time."""
        yield self.request(resource)
        self.enter(queue)
        yield self.hold(hold_time)
        self.leave(queue)
        self.release(resource)

    @classmethod
    def print_route_statistics(cls):
        print("Detailed Route Statistics (Infeed to Sink):")
        for infeed, sinks in cls.route_stats.items():
            for sink, stats in sinks.items():
                if stats["count"] > 0:
                    avg_time = stats["total_time"] / stats["count"]
                    print(f"Infeed {infeed} to Sink {sink}: Count = {stats['count']}, Avg Time = {avg_time:.2f}")
                else:
                    print(f"Infeed {infeed} to Sink {sink}: Count = {stats['count']}, No baggage processed.")





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

# Resource Buffer and Loops
backbone_blue_resource = sim.Resource('Backbone Blue Loop', capacity=100, monitor=True)
backbone_red_resource = sim.Resource('Backbone Red Loop', capacity=100, monitor=True)
ef_buffer_red_resource = sim.Resource('E/F Buffer Red', capacity=100, monitor=True)
ef_buffer_blue_resource = sim.Resource('E/F Buffer Blue', capacity=100, monitor=True)

# Resource Links
link_10034_resource = sim.Resource('Link 10034 E-Hall to E/F Buffer Blue', capacity=100, monitor=True)
link_10035_resource = sim.Resource('Link 10035 E-Hall to E/F Buffer Red', capacity=100, monitor=True)

link_10009_resource = sim.Resource('Link 10009 D-Hall to BB Loop Blue', capacity=100, monitor=True)
link_10008_resource = sim.Resource('Link 10008 D-Hall to BB Loop Red', capacity=100, monitor=True)

link_10655_resource = sim.Resource('Link 10655 E/F Buffer to West Blue', capacity=100, monitor=True)
link_10665_resource = sim.Resource('Link 10665 E/F Buffer to West Red', capacity=100, monitor=True)

link_10635_resource = sim.Resource('Link 10635 BB Loop to sink D-Hall Blue', capacity=100, monitor=True)
link_10645_resource = sim.Resource('Link 10645 BB Loop to sink D-Hall Red', capacity=100, monitor=True)

link_10825_resource = sim.Resource('Link 10825 T2 to BB Loop Blue', capacity=100, monitor=True)
link_10826_resource = sim.Resource('Link 10826 T2 to BB Loop Red', capacity=100, monitor=True)

link_10040_resource = sim.Resource('Link 10040 West to T2 intermediate queue blue', capacity=100, monitor=True)

link_10041_resource = sim.Resource('Link 10041 E/F Buffer to sink West blue and red', capacity=100, monitor=True)

#link_10826_resource = sim.Resource('Link 10826 T2 to BB Loop Red', capacity=100, monitor=True)

link_Zuid_to_BB_Blue_resource = sim.Resource('Link (no ID) Zuid to BB loop Blue', capacity=100, monitor=True)
link_Zuid_to_BB_Red_resource = sim.Resource('Link (no ID) Zuid to BB loop Red', capacity=100, monitor=True)

link_10611_1_resource = sim.Resource('Link 10611_1 E/F Buffer to BB loop Blue', capacity=100, monitor=True)
link_10621_1_resource = sim.Resource('Link 10621_1 E/F Buffer to BB loop Red', capacity=100, monitor=True)
link_10611_2_resource = sim.Resource('Link 10611_2 E/F Buffer to BB loop Blue', capacity=100, monitor=True)
link_10621_2_resource = sim.Resource('Link 10621_2 E/F Buffer to BB loop Red', capacity=100, monitor=True)


# Queues Buffer and loops
backbone_blue_queue = sim.Queue('Backbone Queue Blue Loop')
backbone_red_queue = sim.Queue('Backbone Queue Red Loop')
ef_buffer_red_queue = sim.Queue('E/F Buffer Red')
ef_buffer_blue_queue = sim.Queue('E/F Buffer Blue')

# Queues Links
link_10034_queue = [sim.Queue('Link 10034 E-Hall to E/F Buffer Blue')]
link_10035_queue = [sim.Queue('Link 10035 E-Hall to E/F Buffer Red')]

link_10009_queue = [sim.Queue('Link 10009 D-Hall to BB Loop Blue')]
link_10008_queue = [sim.Queue('Link 10008 D-Hall to BB Loop Red')]

link_10825_queue = [sim.Queue('Link 10825 T2 to BB Loop Blue')]
link_10826_queue = [sim.Queue('Link 10826 T2 to BB Loop Red')]

link_10655_queue = [sim.Queue('Link 10655 E/F Buffer to West Blue')]
link_10665_queue = [sim.Queue('Link 10665 E/F Buffer to West Red')]

link_10635_queue = [sim.Queue('Link 10635 BB Loop to sink D-Hall Blue')]
link_10645_queue = [sim.Queue('Link 10645 BB Loop to sink D-Hall Red')]

link_10040_queue = [sim.Queue('Link 10040 West to T2 intermediate queue blue')]
link_10041_queue = [sim.Queue('Link 10041 E/F Buffer to sink West blue and red')]
#link_10826_queue = [sim.Queue('Link 10826 T2 to BB Loop Red')]

link_Zuid_to_BB_Blue_queue = [sim.Queue('Link (no ID) Zuid to BB loop Blue')]
link_Zuid_to_BB_Red_queue = [sim.Queue('Link (no ID) Zuid to BB loop Red')]

link_10611_1_queue = [sim.Queue('Link 10611_1 E/F Buffer to BB loop Blue')]
link_10621_1_queue = [sim.Queue('Link 10621_1 E/F Buffer to BB loop Red')]
link_10611_2_queue = [sim.Queue('Link 10611_2 E/F Buffer to BB loop Blue')]
link_10621_2_queue = [sim.Queue('Link 10621_2 E/F Buffer to BB loop Red')]


# Queues Infeed
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
    blue_queues[i].animate(x=blue_intermediate_positions[i][0], y=blue_intermediate_positions[i][1], title=f'Infeed. Q {i + 1} Blue')
    if i > 0:
        red_queues[i].animate(x=red_intermediate_positions[i][0], y=red_intermediate_positions[i][1], title=f'Infeed Q {i + 1} Red')


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
env.run(50)



## Printing results ##
Baggage.print_route_statistics()


