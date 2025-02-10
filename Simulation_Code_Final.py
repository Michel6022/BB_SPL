# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 11:03:20 2025

@author: miche
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 08:48:17 2024

@author: miche
"""

# -*- coding: utf-8 -*-
"""
Updated Simulation Script for Baggage Flow
@author: miche
"""
import salabim as sim
import matplotlib.pyplot as plt
import random
import numpy as np
import time  

import numpy as np
import time

imbalance_log = []  # Stores (time, imbalance percentage)

G = 1 # Growthfactor
def run_simulation(seed):
    rng = np.random.default_rng(seed)  # Initialize RNG with the provided seed
   
    sim.yieldless(False)
    claimers_blue = []
    claimers_red = []

    backbone_blue_times = []
    backbone_red_times = []
    ef_blue_times = []
    ef_red_times = []
    # Define time ranges and loads
    time_ranges = {
        "morning01": (0, 2 * 3600),  # 0–2 hours
        "morning02": (2 * 3600, 4 * 3600),  # 2–4 hours
        "midday": (4 * 3600, 8 * 3600),  # 4–8 hours
        "evening": (8 * 3600, 12 * 3600),  # 8–12 hours
        "night": (12 * 3600, 16 * 3600),  # 12–16 hours
    }
    
    infeed_loads = {i: 0 for i in range(1, 6)}  # Infeed stations are numbered 1–5
    # Define scale factor
    time_scale = 576  # Scale 4 hours (14400 seconds) to 100 seconds
    
    cumulative_process_times_per_sink = {sink_id: 0 for sink_id in range(1, 6)}
    route_process_times = {  # Global dictionary to store process times per route
        (infeed, sink): [] for infeed in range(1, 6) for sink in range(1, 6)
    }
    current_system_capacity = {
    "blue": 100,  # Capacity for Blue Backbone
    "red": 100    # Capacity for Red Backbone
    }

    class Baggage(sim.Component):
        global current_system_capacity
        # Class-level dictionary to store route statistics
        all_baggage = []
        route_stats = {
            infeed: {
                sink: {
                    time_period: {"count": 0, "total_time": 0} for time_period in time_ranges
                }
                for sink in range(1, 6)
            }
            for infeed in range(1, 6)
        }
        
        hourly_loads = {  # Dictionary to track passage times for each route
            "Backbone Blue": [],
            "Backbone Red": [],
            "E/F Buffer Blue": [],
            "E/F Buffer Red": [],
            # Add other routes as necessary
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
            self.entry_time = None  # Track entry time into the system
            self.time_in_system = None  # Time spent in the system
            # Add this instance to the class-level list
            Baggage.all_baggage.append(self)
    
        def process(self):
            self.entry_time = self.env.now()
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
            #elf.time_in_system = self.env.now() - self.entry_time
            #print(f"{self.name}: Infeed ID: {self.infeed_id}, Sink ID: {self.sink_id}, Time in System: {time_in_system:.2f}")
            self.exit_time = self.env.now()
            self.time_in_system = self.exit_time - self.entry_time
    
            # Print the time in system for this baggage
            # print(f"{self.name}: Infeed ID {self.infeed_id}, Sink ID {self.sink_id}, "
                  #f"Time in System {self.time_in_system:.2f}")
       
        def _update_stats(self, time_in_system):
            # Determine the current time range
            current_time = self.env.now() * time_scale  # Convert to real-world seconds
            time_period = None
            for period, (start, end) in time_ranges.items():
                if start <= current_time < end:
                    time_period = period
                    break
        
            # Update statistics for the route within the current time period
            stats = Baggage.route_stats[self.infeed_id][self.sink_id][time_period]
            stats["count"] += 1
            stats["total_time"] += time_in_system
            stats["assigned_backbone"] = self.assigned_backbone
        
            # Store the process time in the route_process_times dictionary
            route_key = (self.infeed_id, self.sink_id)
            if route_key not in route_process_times:
                route_process_times[route_key] = []
                route_process_times[route_key].append(time_in_system)
         
            
            
        def _route_west(self, intermediate_queue):
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10040_resource, link_10040_queue[0], hold_time=0.001)
            else:
                yield from self._move_through_link(link_10040_resource, link_10040_queue[0], hold_time=5)
            
            self.enter(blue_queues[3])  # Move to intermediate queue for T2
            yield from self._route_t2(blue_queues[3])
    
        def _route_e_hall(self, intermediate_queue):
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10034_resource, link_10034_queue[0], hold_time=(np.random.uniform(26.45, 26.86) / time_scale))
            else:
                yield from self._move_through_link(link_10035_resource, link_10035_queue[0], hold_time=(np.random.uniform(64.36, 99.69) / time_scale))
               
            yield from self._route_ef()
            
            #Route to West not via BB loop
            if self.sink_id == 1:
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
                else:
                    yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
            
            #Route to D-Hall and Zuid via Backbone loop
            elif self.sink_id in [3, 5]:
                # if self.assigned_backbone == "blue":
                #     yield from self._move_through_link(link_10611_1_resource, link_10611_1_queue[0], hold_time=0.001 /time_scale)
                # else:
                #     yield from self._move_through_link(link_10621_1_resource, link_10621_1_queue[0], hold_time=0.001)
                
                yield from self._route_backbone()
            
                if self.sink_id == 3:
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10635_resource, link_10635_queue[0], hold_time=0.001)
                    else:
                        yield from self._move_through_link(link_10645_resource, link_10645_queue[0], hold_time=0.001)
                               
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)
          
                
    
        def _route_d_hall(self, intermediate_queue):
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10009_resource, link_10009_queue[0], hold_time= (np.random.uniform(106.79, 130.09) / time_scale))
            else:
                yield from self._move_through_link(link_10008_resource, link_10008_queue[0], hold_time= (np.random.uniform(84.82, 93.92) / time_scale))
    
            
            # Route to West and E-Hall via Backbone loop and EF Buffer 
            if self.sink_id in [1, 2]:
                yield from self._route_backbone()
                
                # Move through the appropriate link after the backbone
                if self.assigned_backbone == "blue":
                    yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=0.001)
                else:
                    yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=0.001)
                
                yield from self._route_ef()
                
                if self.sink_id == 1:
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
                    else:
                        yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
                        
                if self.sink_id == 2:
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=0.001)
                    else:
                        yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=0.001)
    
            # Route to Zuid directly go in sink 
            elif self.sink_id == 5:
                yield from self._route_backbone()
             
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)
    
        def _route_t2(self, intermediate_queue):
            if self.assigned_backbone == "blue":
                yield from self._move_through_link(link_10825_resource, link_10825_queue[0], hold_time= (np.random.uniform(87.78, 89.43) / time_scale))
            else:    
                yield from self._move_through_link(link_10826_resource, link_10826_queue[0], hold_time= (np.random.uniform(122.49, 125.17) / time_scale))
            
            yield from self._route_backbone()
            
            
            
            
            # # Route to West and E-Hall via Backbone loop and EF Buffer
            # if self.sink_id in [1, 2]:            
            #     if self.assigned_backbone == "blue":
            #         yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=0.001)
            #     else:
            #         yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=0.001)
                
            #     yield from self._route_ef()
                
            #     if self.sink_id == 1:
            #         if self.assigned_backbone == "blue":
            #             yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
            #         else:
            #             yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=0.001)
                        
            #     if self.sink_id == 2:
            #         if self.assigned_backbone == "blue":
            #             yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=0.001)
            #         else:
            #             yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=0.001)
                
            # elif self.sink_id == 3:
            #     if self.assigned_backbone == "blue":
            #         yield from self._move_through_link(link_10826_resource, link_10826_queue[0], hold_time=0.001)
            #     else:
            #         yield from self._move_through_link(link_10825_resource, link_10825_queue[0], hold_time=0.001)
             
            self.enter(self.assigned_sink)
            self.leave(self.assigned_sink)
    
        def _route_zuid(self, intermediate_queue):
                yield from self._route_backbone()
    
            # Route to West and E-Hall via Backbone loop and EF Buffer 
            # if self.sink_id in [1, 2]:            
            #     if self.assigned_backbone == "blue":
            #         yield from self._move_through_link(link_10611_2_resource, link_10611_2_queue[0], hold_time=5)
            #     else:
            #         yield from self._move_through_link(link_10621_2_resource, link_10621_2_queue[0], hold_time=5)
                
                
                if self.sink_id == 1:             
                    yield from self._route_ef()
                    
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                    else:
                        yield from self._move_through_link(link_10041_resource, link_10041_queue[0], hold_time=5)
                        
                if self.sink_id == 2:
                    yield from self._route_ef()
                   
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10655_resource, link_10655_queue[0], hold_time=(np.random.uniform(93.41, 93.95) / time_scale))
                    else:
                        yield from self._move_through_link(link_10665_resource, link_10665_queue[0], hold_time=(np.random.uniform(93.72, 94.05) / time_scale))
                        
                if self.sink_id == 3:
                    if self.assigned_backbone == "blue":
                        yield from self._move_through_link(link_10635_resource, link_10635_queue[0], hold_time=(np.random.uniform(26.07, 27.02) / time_scale))
                    else:
                        yield from self._move_through_link(link_10645_resource, link_10645_queue[0], hold_time=(np.random.uniform(22.30, 23.45) / time_scale))
                    
                self.enter(self.assigned_sink)
                self.leave(self.assigned_sink)
            
        
                  
        
       
    
        def _route_backbone(self):
            
            if self.assigned_backbone == "blue":
                current_time = self.env.now() * time_scale
                Baggage.hourly_loads["Backbone Blue"].append(current_time)
                
            
                # Request access to the blue backbone resource
                yield self.request(backbone_blue_resource)
                self.enter(backbone_blue_queue)
    
                # Determine hold time based on infeed and outfeed
                if self.infeed_id == 4 and self.sink_id == 5:
                    hold_time = np.random.uniform(66.18, 95.74)  # Example: Blue-specific hold time for infeed 3, outfeed 5
                elif self.infeed_id == 3 and self.sink_id == 5:
                    hold_time = np.random.uniform(67.27, 84.15) # Example: Blue-specific hold time for infeed 1, outfeed 4
                elif self.infeed_id == 2 and self.sink_id == 5:
                    hold_time = np.random.uniform(114.27, 117.53) # Example: Blue-specific hold time for infeed 1, outfeed 4
                elif self.infeed_id == 5 and self.sink_id == 3:
                    hold_time = np.random.uniform(163.13, 165.75) # Example: Blue-specific hold time for infeed 1, outfeed 4
                elif self.infeed_id == 5 and self.sink_id == 2:
                   hold_time = np.random.uniform(145.09, 146.14) # Example: Blue-specific hold time for infeed 1, outfeed 4
                else:
                    hold_time = 100.0  # Default hold time for Blue backbone
    
                # Simulate hold time for blue backbone
                yield self.hold(hold_time / time_scale)
    
                self.leave(backbone_blue_queue)
                self.release(backbone_blue_resource)
    
            elif self.assigned_backbone == "red":
                current_time = self.env.now() * time_scale
                Baggage.hourly_loads["Backbone Red"].append(current_time)
               
                # 
                
               # Red Backbone logic
                backbone_resource = backbone_red_resource
                backbone_queue = backbone_red_queue
    
                # Request access to the red backbone resource
                yield self.request(backbone_resource)
                self.enter(backbone_queue)
    
                # Determine hold time based on infeed and outfeed
                if self.infeed_id == 4 and self.sink_id == 5:
                    hold_time =  np.random.uniform(66.49, 70.39)   # Example: Red-specific hold time for infeed 3, outfeed 5
                elif self.infeed_id == 3 and self.sink_id == 5:
                    hold_time = np.random.uniform(68.27, 69.15)  # Example: Red-specific hold time for infeed 1, outfeed 4
                elif self.infeed_id == 2 and self.sink_id == 5:
                    hold_time = np.random.uniform(116.53, 121.29)  # Example: Red-specific hold time for infeed 1, outfeed 4
                elif self.infeed_id == 5 and self.sink_id == 3:
                    hold_time = np.random.uniform(164.20, 185.40)  # Example: Red-specific hold time for infeed 1, outfeed 4    
                elif self.infeed_id == 5 and self.sink_id == 2:
                    hold_time = np.random.uniform(350.77, 356.41)  # Example: Red-specific hold time for infeed 1, outfeed 4 
                else:
                    hold_time = 110.0  # Default hold time for Red backbone
    
                # Simulate hold time for red backbone
                yield self.hold(hold_time / time_scale)
    
                self.leave(backbone_queue)
                self.release(backbone_resource)
         
            
            
        def _route_ef(self):
            if self.assigned_backbone == "blue":
                Baggage.hourly_loads["E/F Buffer Blue"].append(self.env.now())
                # Blue E/F Buffer logic
                ef_resource = ef_buffer_blue_resource
                ef_queue = ef_buffer_blue_queue
    
                # Request access to the blue E/F buffer resource
                yield self.request(ef_resource)
                self.enter(ef_queue)
    
                # Determine hold time based on infeed and outfeed
                if self.infeed_id == 2 and self.sink_id == 5:
                    hold_time = (np.random.uniform(116.50, 117.21)) # Example: Blue-specific hold time for infeed 3, outfeed 5
                elif self.infeed_id == 5 and self.sink_id == 2:
                    hold_time = (np.random.uniform(36.25, 37.06)) # Example: Blue-specific hold time for infeed 3, outfeed 5
                else:
                    hold_time = 100.0  # Default hold time for Blue backbone
    
                # Simulate hold time for blue buffer
                yield self.hold(hold_time / time_scale)
    
                self.leave(ef_queue)
                self.release(ef_resource)
    
            elif self.assigned_backbone == "red":
                Baggage.hourly_loads["E/F Buffer Red"].append(self.env.now())
                # Red E/F Buffer logic
                ef_resource = ef_buffer_red_resource
                ef_queue = ef_buffer_red_queue
    
                # Request access to the red E/F buffer resource
                yield self.request(ef_resource)
                self.enter(ef_queue)
    
                # Determine hold time based on infeed and outfeed
                if self.infeed_id == 2 and self.sink_id == 5:
                    hold_time = (np.random.uniform(117.77, 124.32))   # Example: Red-specific hold time for infeed 3, outfeed 5
                elif self.infeed_id == 5 and self.sink_id == 2:
                    hold_time = (np.random.uniform(35.83, 38.63))   # Example: Red-specific hold time for infeed 3, outfeed 5
                else:
                    hold_time = 110.0  # Default hold time for Red backbone
    
                # Simulate hold time for red buffer
                yield self.hold(hold_time / time_scale)
    
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
            print("\n### Detailed Route Statistics ###")
            
            # Initialize a dictionary to store total counts per time period
            total_bags_per_period = {time_period: 0 for time_period in time_ranges}
            
            # # Iterate through route statistics
            # for infeed, sinks in cls.route_stats.items():
            #     print(f"\nInfeed {infeed}:")
            #     for sink, time_periods in sinks.items():
            #         print(f"  → Sink {sink}:")
            #         for time_period, stats in time_periods.items():
            #             if stats["count"] > 0:
            #                 avg_time = stats["total_time"] / stats["count"]
            #                 print(f"    {time_period.capitalize()}: Count = {stats['count']}, "
            #                       f"Total Time = {stats['total_time']:.2f}, "
            #                       f"Avg Time = {avg_time:.2f}")
            #             else:
            #                 print(f"    {time_period.capitalize()}: Count = {stats['count']}, No baggage processed.")
                        
            #             # Aggregate the counts for the time period
            #             total_bags_per_period[time_period] += stats["count"]
            
            # # Print the total bags per time period
            # print("\n### Total Baggage Processed Per Time Period ###")
            # for time_period, total_count in total_bags_per_period.items():
            #     print(f"  {time_period.capitalize()}: {total_count} bags")
    
    
    
    
    # Lists to store simulation data
    sim_time = []
    queue_lengths_blue = []
    queue_lengths_red = []
    process_times = []
    ef_buffer_blue_lengths = []
    ef_buffer_red_lengths = []
    


    
    class MonitorOccupancy(sim.Component):
        def process(self):
            while True:
                sim_time.append(env.now())
                queue_lengths_blue.append(backbone_blue_queue.length())
                queue_lengths_red.append(backbone_red_queue.length())
                yield self.hold(10 / time_scale)  # Monitor every scaled second
    
    
    backbone_distributions = {
        (2, 5): (0.5, 0.5),   # E-hall → ZUID
        (3, 5): (0.5, 0.5),   # D-Hall → ZUID
        (4, 5): (0.5, 0.5),   # T2 → ZUID
        (5, 3): (0.5, 0.5),  # ZUID → D-Hall
        (5, 2): (0.5, 0.5)  # ZUID → E-Hall
        # Add other routes as needed
    }
    
    class LoadMonitor(sim.Component):
        """Monitor the load of each infeed station."""
        def process(self):
            while True:
                print(f"Current load at {env.now():.2f} simulated seconds:")
                for infeed_id, load in infeed_loads.items():
                    print(f"  Infeed {infeed_id}: {load} items")
                yield self.hold(3600 / time_scale)  # Print load every real-world hour
    
    
    class DirectionGenerator(sim.Component):
        debug_printed = set()  # Class-level set to track printed messages
        def __init__(self, sink, infeed_queue, blue_queue, red_queue, interval_lookup, infeed_id, sink_id, *args, **kwargs):
            # Initialize the base class
            super().__init__(*args, **kwargs)
            
            # Store custom arguments as attributes
            self.sink = sink
            self.infeed_queue = infeed_queue
            self.blue_queue = blue_queue
            self.red_queue = red_queue
            self.interval_lookup = interval_lookup
            self.infeed_id = infeed_id
            self.sink_id = sink_id
            self.baggage_count = 0  # Initialize baggage count
    
        def process(self):
            initial_distribution = (0.4, 0.6)  # Initial distribution: Red, Blue
            dynamic_start_time = 0 * 3600 / time_scale  # 2 hours in scaled time
            dynamic_stop_time = 4 * 3600 / time_scale  # 2 hours in scaled time
    
            while True:
                current_time = self.env.now()
    
                # Determine the time range for the interval
                for time_period, (start, end) in time_ranges.items():
                    if start <= current_time * time_scale < end:
                        total_interval = self.interval_lookup.get((self.infeed_id, self.sink_id, time_period), 0.1)
                        break
                else:
                    total_interval = 0.1
    
                # Choose distribution based on time
                if dynamic_start_time < current_time < dynamic_stop_time:
                    distribution = initial_distribution  # Use the initial fixed distribution
                else:
                    # Calculate dynamic probabilities
                    total_load = len(backbone_blue_resource.claimers()) + len(backbone_red_resource.claimers())
                    if total_load > 0:
                        blue_probability = 1 - (len(backbone_blue_resource.claimers()) / total_load)
                        red_probability = 1 - (len(backbone_red_resource.claimers()) / total_load)
                        distribution = (red_probability, blue_probability)
                    else:
                        distribution = (0.5, 0.5)  # Equal distribution if no load
    
                # Split interval between red and blue
                blue_interval = total_interval / distribution[1] if distribution[1] > 0 else float("inf")
                red_interval = total_interval / distribution[0] if distribution[0] > 0 else float("inf")
    
                # Determine which backbone the baggage will take
                assigned_backbone = random.choices(["red", "blue"], weights=distribution, k=1)[0]
                interval = red_interval if assigned_backbone == "red" else blue_interval
    
                self.baggage_count += 1
                baggage = Baggage(
                    assigned_sink=self.sink,
                    blue_queue=self.blue_queue,
                    red_queue=self.red_queue,
                    number=self.baggage_count,
                    assigned_backbone=assigned_backbone,
                    infeed_id=self.infeed_id,
                    sink_id=self.sink_id,
                )
                baggage.enter(self.infeed_queue)
                yield self.hold(0.01 / time_scale)  # Scaled delay
                baggage.leave(self.infeed_queue)
                yield self.hold(interval)
            
# def process(self):
#             while True:
#                 # Determine the current time range
#                 current_time = self.env.now() * time_scale  # Scale simulation time back to real-time seconds
#                 for time_period, (start, end) in time_ranges.items():
#                     if start <= current_time < end:
#                         total_interval = interval_lookup.get((self.infeed_id, self.sink_id, time_period), 0.1)
#                         break
#                 else:
#                     total_interval = 0.1  # Default interval if none found
        
#                 #Split interval for red and blue based on distribution
#                 #if 2 * 3600 <= current_time < 3 * 3600:  # From 08:00 to 10:00 (scaled time)
#                  #   distribution = (0.99999, 0.011111)  # 100% red, 0% blue
#                 #else:
#                 distribution = backbone_distributions.get((self.infeed_id, self.sink_id), (0.5, 0.5))  # Default distribution
                
#                 blue_interval = total_interval / distribution[1] if distribution[1] > 0 else float("inf")
#                 red_interval = total_interval / distribution[0] if distribution[0] > 0 else float("inf")
        
#                 # debug_key = (self.infeed_id, self.sink_id, time_period)
#                 # if debug_key not in DirectionGenerator.debug_printed:
#                 #    # print(
#                 #         f"[DEBUG] Infeed: {self.infeed_id}, Sink: {self.sink_id}, "
#                 #         f"Time: {current_time:.2f}s, Period: {time_period}, "
#                 #         f"Total Interval: {total_interval:.4f}s, "
#                 #         f"Blue Interval: {blue_interval:.4f}s, Red Interval: {red_interval:.4f}s"
#                 #     )
#                 #     DirectionGenerator.debug_printed.add(debug_key)
        
#                 # Determine which backbone the baggage will take
#                 assigned_backbone = random.choices(["red", "blue"], weights=distribution, k=1)[0]
#                 interval = red_interval if assigned_backbone == "red" else blue_interval
                
                
#                 # if self.infeed_id == 4 and self.sink_id == 5:
#                 #     print(
#                 #     f"[DEBUG] Generated baggage for Route 4 → 5: "
#                 #     f"Backbone {assigned_backbone}, Total Interval: {total_interval:.4f}, "
#                 #     f"Assigned Interval: {interval:.4f}"
#                 # )
                
#                 self.baggage_count += 1
        
#                 # Create baggage and assign it to the appropriate backbone
#                 baggage = Baggage(
#                     assigned_sink=self.sink,
#                     blue_queue=self.blue_queue,
#                     red_queue=self.red_queue,
#                     number=self.baggage_count,
#                     assigned_backbone=assigned_backbone,
#                     infeed_id=self.infeed_id,
#                     sink_id=self.sink_id,
#                 )
#                 baggage.enter(self.infeed_queue)
#                 infeed_loads[self.infeed_id] += 1
#                 yield self.hold(0.01 / time_scale)  # Scaled delay
#                 baggage.leave(self.infeed_queue)
        
#                 # Hold for the dynamically calculated interval
#                 yield self.hold(interval)


    
    
    class InfeedStation(sim.Component):
        def __init__(self, sink, sink_id, infeed_queue, blue_queue, red_queue, interval_lookup, infeed_id, *args, **kwargs):
            # Initialize the base class
            super().__init__(*args, **kwargs)
    
            # Store custom arguments as attributes
            self.sink = sink
            self.sink_id = sink_id
            self.infeed_queue = infeed_queue
            self.blue_queue = blue_queue
            self.red_queue = red_queue
            self.interval_lookup = interval_lookup
            self.infeed_id = infeed_id
    
            # Initialize DirectionGenerator for each sink
            for (infeed_id, sink_id, time_period), interval in interval_lookup.items():
                if infeed_id == self.infeed_id:
                    DirectionGenerator(
                        sink=self.sink,
                        infeed_queue=self.infeed_queue,
                        blue_queue=self.blue_queue,
                        red_queue=self.red_queue,
                        interval_lookup=self.interval_lookup,
                        infeed_id=self.infeed_id,
                        sink_id=sink_id
                    )
    
    class MonitorBackboneQueues(sim.Component):
        def process(self):
            while True:
                # Append the current queue lengths to lists
                queue_lengths_blue.append(backbone_blue_queue.length())
                queue_lengths_red.append(backbone_red_queue.length())
                sim_time.append(env.now())
                
                # Wait for the next monitoring interval
                yield self.hold(10 / time_scale)  # Adjust the interval as needed
    
    
    class BackboneMonitor(sim.Component):
        def process(self):
            while True:
                # Record simulation time
                current_time = self.env.now() * time_scale  # Convert to real-world seconds
                
                # Record queue lengths
                queue_lengths_blue.append(backbone_blue_queue.length())
                queue_lengths_red.append(backbone_red_queue.length())
                
                # Record the number of claimers actively using the backbone
                blue_load = len(backbone_blue_resource.claimers())
                red_load = len(backbone_red_resource.claimers())
                claimers_blue.append(blue_load)
                claimers_red.append(red_load)
                
                # Calculate total load and imbalance KPI
                total_load = blue_load + red_load
                if total_load > 0:
                    imbalance_percentage = abs(blue_load - red_load) / total_load * 100
                else:
                    imbalance_percentage = 0.0  # No imbalance if total load is zero
                
                # Log imbalance data
                imbalance_log.append((current_time, imbalance_percentage))
                
                # Print for debugging (optional)
                print(f"Time: {current_time / 3600:.2f} hours")
                print(f"Blue Load: {blue_load}, Red Load: {red_load}")
                print(f"Load Imbalance: {imbalance_percentage:.2f}%")
                
                # Wait for the next monitoring interval
                yield self.hold(5 / time_scale)  # Monitor every scaled 10 seconds



    

    class BackboneClaimersMonitor(sim.Component):
        def process(self):
            half_hour_real_time = 30 * 60 / time_scale  # 30 minutes in scaled time
            while True:
                current_time = self.env.now() * time_scale  # Convert to real-world seconds
                print(f"Time: {current_time / 3600:.2f} hours")
                print(f"Blue Backbone: {len(backbone_blue_resource.claimers())} claimers (Capacity: {backbone_blue_resource.capacity()})")
                print(f"Red Backbone: {len(backbone_red_resource.claimers())} claimers (Capacity: {backbone_red_resource.capacity()})")
                yield self.hold(half_hour_real_time)  # Wait for 30 minutes real-time


    
    # Create a new random generator instance
    rng = np.random.default_rng()
    
    # # Load boundaries for all routes
    # route_bounds = {
    #     (2, 5): (390+261,752+740),   # E-hall - ZUID
    #     (3, 5): (152+270, 366+758),  # D-Hall - ZUID   
    #     (4, 5): (91, 350),           # T2 - ZUID
    #     (5, 3): (616, 997),          # ZUID - D-Hall
    #     (5, 2): (605, 1237)          # ZUID - E-Hall
    
    #         # Add more routes as needed
    # }
    
    route_bounds_by_interval = {
        "morning01": {
            (2, 5): (562/4 * G , 930/4 * G),   # E-hall → ZUID
            (3, 5): (649/4* G, 1193/4* G),   # D-Hall → ZUID
            (4, 5): (69/4* G, 322/4* G),   # T2 → ZUID
            (5, 3): (553/4* G, 858/4* G),  # ZUID → D-Hall
            (5, 2): (4/4* G, 93/4* G),  # ZUID → E-Hall
        },
        "morning02": {
            (2, 5): (562/4  * G, 930/4  * G),   # E-hall → ZUID
            (3, 5): (649/4  * G, 1193/4 * G),   # D-Hall → ZUID
            (4, 5): (69/4   * G, 322/4*  G),   # T2 → ZUID
            (5, 3): (553/4 * G, 858/4*  G),  # ZUID → D-Hall
            (5, 2): (4/4* G, 93/4*  G),  # ZUID → E-Hall
        },
        "midday": {
            (2, 5): (786/4* G, 962/4* G),   # E-hall → ZUID
            (3, 5): (560/4* G, 745/4* G),   # D-Hall → ZUID
            (4, 5): (716/4* G, 946/4* G),   # T2 → ZUID
            (5, 3): (816/4 * G, 1197/4* G),   # ZUID → D-Hall
            (5, 2): (1005/4* G, 1437/4* G),  # ZUID → E-Hall
        },
        "evening": {
            (2, 5): (350/4* G, 611/4* G),   # E-hall → ZUID
            (3, 5): (47/4* G, 302/4* G),   # D-Hall → ZUID
            (4, 5): (233/4* G, 494/4* G),   # T2 → ZUID
            (5, 3): (1291/4* G, 1779/4* G),   # ZUID → D-Hall
            (5, 2): (729/4* G, 1192/4* G),  # ZUID → E-Hall
        },
        "night": {
            (2, 5): (330/4* G, 714/4* G),   # E-hall → ZUID
            (3, 5): (24/4* G, 191/4* G),   # D-Hall → ZUID
            (4, 5): (99/4* G, 160/4* G),    # T2 → ZUID
            (5, 3): (866/4* G, 1242/4* G),   # ZUID → D-Hall
            (5, 2): (153/4* G, 795/4* G),  # ZUID → E-Hall
        },
    
    }
    
    # Generate load and calculate intervals for all routes
    total_time_scaled = (4 * 3600) / time_scale  # 4 hours scaled down
    
    interval_lookup = {}  # To store intervals for each route and time period
    print("Chosen loads and intervals for each route:")
    
    for time_period, route_bounds in route_bounds_by_interval.items():
        for (infeed_id, sink_id), (lower_bound, upper_bound) in route_bounds.items():
            # Sample load from the defined range for the specific time period
            load_per_hour = np.random.uniform(lower_bound, upper_bound)
            
            # Calculate total load over the scaled 4-hour period
            total_load = load_per_hour 
            
            # Calculate interval for this route and time period in scaled time
            scaled_interval = total_time_scaled / total_load
            
            # Store the interval in the lookup table with a composite key
            interval_lookup[(infeed_id, sink_id, time_period)] = scaled_interval
            
            # Print the chosen load and calculated interval
            print(f"Route {infeed_id} → {sink_id} ({time_period}): Load (per hour) = {load_per_hour}, Total Load (4 hours) = {total_load}, Interval = {scaled_interval:.4f} seconds")
            
    # Dictionary to store total baggage count for each route and time period
    total_bags_per_route_period = {time_period: {} for time_period in route_bounds_by_interval}
    
    # Simulation results processing
    for baggage in Baggage.all_baggage:
        current_time = baggage.entry_time * time_scale  # Convert to real-world seconds
        for time_period, (start, end) in time_ranges.items():
            if start <= current_time < end:
                route = (baggage.infeed_id, baggage.sink_id)
                if route not in total_bags_per_route_period[time_period]:
                    total_bags_per_route_period[time_period][route] = 0
                total_bags_per_route_period[time_period][route] += 1
                break
    
    
            
    
    env = sim.Environment()
    #env.time = 21600  # Set the environment's current time to 6:00 AM
    
    # Resource Buffer and Loops
    backbone_blue_resource = sim.Resource('Backbone Blue Loop', capacity=150, monitor=True)
    backbone_red_resource = sim.Resource('Backbone Red Loop', capacity=150, monitor=True)
    ef_buffer_red_resource = sim.Resource('E/F Buffer Red', capacity=3000/ 2 /3600 *time_scale, monitor=True)
    ef_buffer_blue_resource = sim.Resource('E/F Buffer Blue', capacity=3000/ 2 /3600 *time_scale, monitor=True)
    
    # Resource Links
    link_10034_resource = sim.Resource('Link 10034 E-Hall to E/F Buffer Blue', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    link_10035_resource = sim.Resource('Link 10035 E-Hall to E/F Buffer Red', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    
    link_10009_resource = sim.Resource('Link 10009 D-Hall to BB Loop Blue', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    link_10008_resource = sim.Resource('Link 10008 D-Hall to BB Loop Red', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    
    link_10655_resource = sim.Resource('Link 10655 E/F Buffer to West Blue', capacity=1500/ 2 /3600 *time_scale, monitor=True)
    link_10665_resource = sim.Resource('Link 10665 E/F Buffer to West Red', capacity=1500/ 2 /3600 *time_scale, monitor=True)
    
    link_10635_resource = sim.Resource('Link 10635 BB Loop to sink D-Hall Blue', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    link_10645_resource = sim.Resource('Link 10645 BB Loop to sink D-Hall Red', capacity=1350/ 2 /3600 *time_scale, monitor=True)
    
    link_10825_resource = sim.Resource('Link 10825 T2 to BB Loop Blue', capacity=1200/ 2 /3600 *time_scale, monitor=True)
    link_10826_resource = sim.Resource('Link 10826 T2 to BB Loop Red', capacity=1200 / 2 /3600, monitor=True)
    
    link_10040_resource = sim.Resource('Link 10040 West to T2 intermediate queue blue', capacity=1000 / 2 /3600, monitor=True)
    
    link_10041_resource = sim.Resource('Link 10041 E/F Buffer to sink West blue and red', capacity=1350/ 2 /3600, monitor=True)
    
    #link_10826_resource = sim.Resource('Link 10826 T2 to BB Loop Red', capacity=100, monitor=True)
    
    link_Zuid_to_BB_Blue_resource = sim.Resource('Link (no ID) Zuid to BB loop Blue', capacity=1800/ 2 /3600, monitor=True)
    link_Zuid_to_BB_Red_resource = sim.Resource('Link (no ID) Zuid to BB loop Red', capacity=1800/ 2 /3600, monitor=True)
    
    link_10611_1_resource = sim.Resource('Link 10611_1 E/F Buffer to BB loop Blue', capacity=1800/ 2 /3600, monitor=True)
    link_10621_1_resource = sim.Resource('Link 10621_1 E/F Buffer to BB loop Red', capacity=1800/ 2 /3600, monitor=True)
    link_10611_2_resource = sim.Resource('Link 10611_2 E/F Buffer to BB loop Blue', capacity=1800/ 2 /3600, monitor=True)
    link_10621_2_resource = sim.Resource('Link 10621_2 E/F Buffer to BB loop Red', capacity=1800/ 2 /3600, monitor=True)
    
    
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
    
    # interval_lookup = {
    #     (3, 2): 4, 
    # }
    
    # Set positions for visual elements
    infeed_positions = [(100, 100), (100, 600), (400, 600), (700, 400), (700, 100)]
    sink_positions = [(200, 100), (200, 600), (500, 600), (800, 400), (800, 100)]
    blue_intermediate_positions = [(100, 175), (100, 525), (400, 525), (700, 325), (700, 175)]
    red_intermediate_positions = [(200, 175), (200, 525), (500, 525), (800, 325), (800, 175)]
    
    # # Animate infeed stations, sinks, and intermediate queues
    # for i in range(5):
    #     #infeed_queues[i].animate(x=infeed_positions[i][0], y=infeed_positions[i][1], title=f'Infeed Station {i + 1}')
    #     #sinks[i].animate(x=sink_positions[i][0], y=sink_positions[i][1], title=f'Sink {i + 1}')
    #     blue_queues[i].animate(x=blue_intermediate_positions[i][0], y=blue_intermediate_positions[i][1], title=f'Infeed. Q {i + 1} Blue')
    #     if i > 0:
    #         red_queues[i].animate(x=red_intermediate_positions[i][0], y=red_intermediate_positions[i][1], title=f'Infeed Q {i + 1} Red')
    
    
    # Animate the first infeed and sink as Infeed West and Outfeed West
    sim.AnimateQueue(infeed_queues[0], x=infeed_positions[0][0], y=infeed_positions[0][1], title='Infeed West', direction='e', max_length=4, id='infeed_west')
    sim.AnimateQueue(sinks[0], x=sink_positions[0][0], y=sink_positions[0][1], title='Outfeed West', direction='e', max_length=4, id='outfeed_west')
    
    # Animate the second infeed and sink as Infeed E-Hall and Outfeed E-Hall (top side)
    sim.AnimateQueue(infeed_queues[1], x=infeed_positions[1][0], y=infeed_positions[1][1], title='Infeed E-Hall', direction='e', max_length=4, id='infeed_e_hall')
    sim.AnimateQueue(sinks[1], x=sink_positions[1][0], y=sink_positions[1][1], title='Outfeed E-Hall', direction='e', max_length=4, id='outfeed_e_hall')
    
    # Animate the third infeed and sink as Infeed D-Hall and Outfeed D-Hall (right middle)
    sim.AnimateQueue(infeed_queues[2], x=infeed_positions[2][0], y=infeed_positions[2][1], title='Infeed D-Hall', direction='e', max_length=4, id='infeed_d_hall')
    sim.AnimateQueue(sinks[2], x=sink_positions[2][0], y=sink_positions[2][1], title='Outfeed D-Hall', direction='e', max_length=4, id='outfeed_d_hall')
    
    # Animate the fourth infeed and sink as Infeed T2 and Outfeed T2
    sim.AnimateQueue(infeed_queues[3], x=infeed_positions[3][0], y=infeed_positions[3][1], title='Infeed T2', direction='e', max_length=4, id='infeed_t2')
    sim.AnimateQueue(sinks[3], x=sink_positions[3][0], y=sink_positions[3][1], title='Outfeed T2', direction='e', max_length=4, id='outfeed_t2')
    
    # Animate the fifth infeed and sink as Infeed Zuid and Outfeed Zuid
    sim.AnimateQueue(infeed_queues[4], x=infeed_positions[4][0], y=infeed_positions[4][1], title='Infeed Zuid', direction='e', max_length=6, id='infeed_zuid')
    sim.AnimateQueue(sinks[4], x=sink_positions[4][0], y=sink_positions[4][1], title='Outfeed Zuid', direction='e', max_length=4, id='outfeed_zuid')
    
    # Additional buffer and backbone queues
    sim.AnimateQueue(ef_buffer_red_queue, x=200, y=300, title='E/F Buffer Red', direction='e', max_length=4, id='ef_buffer_red')
    sim.AnimateQueue(ef_buffer_blue_queue, x=200, y=400, title='E/F Buffer Blue', direction='e', max_length=4, id='ef_buffer_blue')
    sim.AnimateQueue(backbone_red_queue, x=425, y=300, title='Backbone Queue Red', direction='e', max_length=4, id='backbone_red')
    sim.AnimateQueue(backbone_blue_queue, x=425, y=400, title='Backbone Queue Blue', direction='e', max_length=4, id='backbone_blue')
    
    
    
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
    
    
    
    
    
    env.animate(False)
    monitor = MonitorOccupancy()
    monitor_backbone = MonitorBackboneQueues()
    load_monitor = LoadMonitor()
    monitor_backbone_claimers = BackboneClaimersMonitor()
    backbone_monitor = BackboneMonitor()

    
    #QueueUtilizationUpdater()
    # Run the simulation
    env.run(16 * 3600 / time_scale)  # Correct
    
    print("\n### Backbone Usage Statistics ###")
    print(f"Max Queue Length (Blue): {max(queue_lengths_blue)}")
    print(f"Max Claimers (Blue): {max(claimers_blue)}")
    print(f"Average Queue Length (Blue): {np.mean(queue_lengths_blue):.2f}")
    print(f"Average Claimers (Blue): {np.mean(claimers_blue):.2f}")
    
    print(f"Max Queue Length (Red): {max(queue_lengths_red)}")
    print(f"Max Claimers (Red): {max(claimers_red)}")
    print(f"Average Queue Length (Red): {np.mean(queue_lengths_red):.2f}")
    print(f"Average Claimers (Red): {np.mean(claimers_red):.2f}")

    
    bin_size = 3600  # 1 hour
    # At the end of the simulation
    bin_edges = np.arange(0, 16 * 3600 + bin_size, bin_size)
    hourly_loads_blue = np.histogram(Baggage.hourly_loads["Backbone Blue"], bins=bin_edges)[0]
    hourly_loads_red = np.histogram(Baggage.hourly_loads["Backbone Red"], bins=bin_edges)[0]
        
    ###=======================Printing results===================================###
    # Route totals
    route_totals = {
        f"Route {i} → {j}": {"Blue": 0, "Red": 0, "Total": 0}
        for i in range(1, 6) for j in range(1, 6)
    }
    
    # Iterate through all baggage instances
    for baggage in Baggage.all_baggage:
        # Determine the route label
        route_label = f"Route {baggage.infeed_id} → {baggage.sink_id}"
    
        # Increment counts based on the assigned backbone
        if baggage.assigned_backbone == "blue":
            route_totals[route_label]["Blue"] += 1
        elif baggage.assigned_backbone == "red":
            route_totals[route_label]["Red"] += 1
    
        # Update the total count
        route_totals[route_label]["Total"] += 1
    
    # Print the route totals
    for route_label, totals in route_totals.items():
        print(f"\n{route_label}:") 
        print(f"  Total Baggage via Blue Backbone: {totals['Blue']}")
        print(f"  Total Baggage via Red Backbone: {totals['Red']}")
        print(f"  Total Baggage for the Route: {totals['Total']}")
        
        
    
    total_blue_backbone_load = sum(route["Blue"] for route in route_totals.values())
    total_red_backbone_load = sum(route["Red"] for route in route_totals.values())
    # Reset route totals
    route_totals = {
        f"Route {i} → {j}": {"Blue": 0, "Red": 0, "Total": 0}
        for i in range(1, 6) for j in range(1, 6)
    }
    
    # Iterate through all baggage instances
    for baggage in Baggage.all_baggage:
        # Determine the route label
        route_label = f"Route {baggage.infeed_id} → {baggage.sink_id}"
    
        # Increment counts based on the assigned backbone
        if baggage.assigned_backbone == "blue":
            route_totals[route_label]["Blue"] += 1
        elif baggage.assigned_backbone == "red":
            route_totals[route_label]["Red"] += 1
    
        # Update the total count
        route_totals[route_label]["Total"] += 1

    return hourly_loads_blue, hourly_loads_red,  Baggage.all_baggage


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter


# %%


hourly_loads_blue = []
hourly_loads_red = []
all_baggage_data = []

# Define the number of seeds
num_seeds = 10

# Run the simulation for multiple seeds
for seed in range(1, num_seeds + 1):
    print(f"Running simulation for seed {seed}...")
    hourly_blue, hourly_red, baggage_data = run_simulation(seed=seed)
    hourly_loads_blue.append(hourly_blue)
    hourly_loads_red.append(hourly_red)
    all_baggage_data.extend(baggage_data)  # Collect baggage data from all seeds
    
    
print(hourly_blue)
print(hourly_red)
total_hourly_load_blue = sum(hourly_blue)
total_hourly_load_red = sum(hourly_red)
print(f"Total baggage through blue backbone: {total_hourly_load_blue}")
print(f"Total baggage through red backbone: {total_hourly_load_red}")


# Convert the lists to numpy arrays for easier manipulation
hourly_loads_blue = np.array(hourly_loads_blue)
hourly_loads_red = np.array(hourly_loads_red)

# Calculate the averages across the 10 seeds
average_hourly_loads_blue = np.mean(hourly_loads_blue, axis=0)
average_hourly_loads_red = np.mean(hourly_loads_red, axis=0)

# Generate time bins (scaled time in hours), shifted to start from 06:00 AM
time_bins = np.arange(6, 6 + len(average_hourly_loads_blue))  # Start from 6 hours (6:00 AM)

# Define a function to format the x-axis as HH:MM (06:00, 07:00, etc.)
def time_formatter(x, pos):
    hours = int(x)
    minutes = int((x - hours) * 60)  # Convert the fractional part to minutes
    return f"{hours:02d}:{minutes:02d}"

# Ensure the correct dimensions and plotting
if hourly_loads_blue.shape[1] == len(time_bins) and hourly_loads_red.shape[1] == len(time_bins):
    plt.figure(figsize=(12, 8))

    # Add boxplots for spread and overlay line plots for averages
    plt.boxplot(
        hourly_loads_blue,
        positions=time_bins - 0.15,
        widths=0.3,
        patch_artist=True,
        boxprops=dict(facecolor='lightblue', alpha=0.7),
        showfliers=False, 
    )
    plt.boxplot(
        hourly_loads_red,
        positions=time_bins + 0.15,
        widths=0.3,
        patch_artist=True,
        boxprops=dict(facecolor='lightcoral', alpha=0.7),
        showfliers=False,
    )

    # Overlay line plots on the boxplots
    plt.plot(time_bins, average_hourly_loads_blue, marker="o", label="Blue Backbone Average", color="blue", linestyle="-")
    plt.plot(time_bins, average_hourly_loads_red, marker="s", label="Red Backbone Average", color="red", linestyle="--")

    # Add labels, title, and legend with the number of seeds in the title
    plt.title(f"Average Hourly Load per Backbone with Spread Across {num_seeds} Seeds with dynamic load balancing", fontsize=14)
    plt.xlabel("Time (hours)", fontsize=12)
    plt.ylabel("Load (bags per hour)", fontsize=12)
    
    # Apply the time formatter to the x-axis
    plt.gca().xaxis.set_major_formatter(FuncFormatter(time_formatter))
    
    # Set xticks to show whole hours from 06:00 onwards
    plt.xticks(time_bins)

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=12)
    plt.tight_layout()

    # Show the plot
    plt.show()
else:
    print("Mismatch detected between data dimensions and positions. Check your inputs.")

# Convert imbalance_log to a NumPy array for easier manipulation
imbalance_log = np.array(imbalance_log)
time_stamps = imbalance_log[:, 0]  # Extract timestamps
imbalance_percentages = imbalance_log[:, 1]  # Extract imbalance percentages

# Define hourly bins and calculate averages
bin_size = 3600  # 1 hour
hourly_bins = np.arange(0, 16 * 3600 + bin_size, bin_size)  # Hourly bin edges
hourly_averages = []

for i in range(len(hourly_bins) - 1):
    start, end = hourly_bins[i], hourly_bins[i + 1]
    hourly_data = imbalance_percentages[(time_stamps >= start) & (time_stamps < end)]
    hourly_avg = np.mean(hourly_data) if len(hourly_data) > 0 else 0
    hourly_averages.append(hourly_avg)

# Convert bin edges to hours for x-axis labels
hourly_labels = hourly_bins[:-1] / 3600 + 6  # Convert to hours, starting from 6:00 AM

# Plot hourly imbalance averages
plt.figure(figsize=(10, 6))
plt.plot(hourly_labels, hourly_averages, marker='o', color='purple', linestyle='-')
plt.title("Hourly Imbalance Percentage Between Blue and Red Backbones", fontsize=14)
plt.xlabel("Time (hours)", fontsize=12)
plt.ylabel("Imbalance Percentage (%)", fontsize=12)
plt.xticks(hourly_labels, labels=[f"{int(h)}:00" for h in hourly_labels], rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from math import ceil

time_scale = 576  # Scale 4 hours (14400 seconds) to 100 seconds

# Define route descriptions and norm times (could be moved to an external configuration)
route_descriptions = {
    "Route 2 → 5": "E-hall - ZUID",
    "Route 3 → 5": "D-Hall - ZUID",
    "Route 4 → 5": "T2 - ZUID",
    "Route 5 → 3": "ZUID - D-Hall",
    "Route 5 → 2": "ZUID - E-Hall",
}

norm_times = {
    "Route 4 → 5": {"Blue": 255, "Red": 255},
    "Route 3 → 5": {"Blue": 275, "Red": 350},
    "Route 2 → 5": {"Blue": 460, "Red": 500},
    "Route 5 → 3": {"Blue": 300, "Red": 315},
    "Route 5 → 2": {"Blue": 680, "Red": 680},
}


# Process baggage data into a DataFrame
route_data = pd.DataFrame(columns=["Route", "Backbone", "Time_in_System", "Exceeded_Norm", "Seed"])

for baggage in all_baggage_data:
    if baggage.time_in_system is None:
        continue

    # Extract route and norm time
    route_label = f"Route {baggage.infeed_id} → {baggage.sink_id}"
    norm_time = norm_times.get(route_label, {}).get(baggage.assigned_backbone.capitalize(), float("inf"))
    exceeded_norm = baggage.time_in_system * time_scale > norm_time

    # Append data to the DataFrame
    route_data = pd.concat(
        [
            route_data,
            pd.DataFrame.from_records(
                [{
                    "Route": route_label,
                    "Backbone": baggage.assigned_backbone.capitalize(),
                    "Time_in_System": baggage.time_in_system * time_scale,
                    "Exceeded_Norm": exceeded_norm,
                    "Seed": num_seeds,
                }]
            )
        ],
        ignore_index=True
    )
# Define route descriptions for mapping
route_descriptions = {
    "Route 2 → 5": "E-hall - ZUID",
    "Route 3 → 5": "D-Hall - ZUID",
    "Route 4 → 5": "T2 - ZUID",
    "Route 5 → 3": "ZUID - D-Hall",
    "Route 5 → 2": "ZUID - E-Hall",
}

seed_grouped = route_data.groupby(["Route", "Backbone", "Seed"]).agg(
    Avg_Time_Per_Seed=("Time_in_System", "mean"),  # Average Time_in_System for each seed
    Bagage_Count=("Time_in_System", "count"),  # Count of baggage items for each seed
    Exceeded_Norm_Count=("Exceeded_Norm", "sum"),  # Count of items exceeding norm time per seed
).reset_index()
print(seed_grouped)

# Group by Route and Backbone to calculate overall averages across seeds
seed_averaged_data = seed_grouped.groupby(["Route", "Backbone"]).agg(
    Avg_Time=("Avg_Time_Per_Seed", "mean"),  # Average time across seeds
    Std_Time=("Avg_Time_Per_Seed", "std"),  # Standard deviation across seeds
    Avg_Bagage_Count=("Bagage_Count", "mean"),  # Average baggage count across seeds
    Avg_Exceeded_Norm_Count=("Exceeded_Norm_Count", "mean"),  # Average exceeding norm count across seeds
    Total_Seeds=("Seed", "count"),  # Total number of seeds
).reset_index()

# Add 1 to Total_Seeds to adjust for the new requirement
seed_averaged_data["Total_Seeds"] = num_seeds

# Merge norm times into the aggregated DataFrame
seed_averaged_data["Norm_Time"] = seed_averaged_data.apply(
    lambda row: norm_times[row["Route"]][row["Backbone"]], axis=1
)

# Calculate Delta Norm Avg (difference between Avg_Time and Norm_Time)
seed_averaged_data["Delta_Norm_Avg"] = seed_averaged_data["Avg_Time"] - seed_averaged_data["Norm_Time"]

# Incorporate route names using route_descriptions
seed_averaged_data["Route_Name"] = seed_averaged_data["Route"].map(route_descriptions)

# Reorder columns to include the route names and exceed norm count
seed_averaged_data = seed_averaged_data[[
    "Route_Name", "Backbone", "Avg_Time", "Std_Time",
    "Avg_Bagage_Count", "Avg_Exceeded_Norm_Count",  # Added Avg_Exceeded_Norm_Count
    "Total_Seeds", "Norm_Time", "Delta_Norm_Avg"
]]


# Print the seed-averaged statistics including route names
print("\n### Seed-Averaged Statistics by Route Name and Backbone ###")
print(seed_averaged_data)

# Save the LaTeX table to a .tex file
with open('seed_averaged_data.tex', 'w') as file:
    file.write(seed_averaged_data.to_latex(index=False, float_format="%.2f"))




# #Plot histograms
# unique_routes = route_data["Route"].unique()
# cols = 3
# rows = 2

# fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5), constrained_layout=True)
# axes = axes.flatten()

# # Prepare legend handles for hatching
# hatch_legend = Patch(facecolor='none', edgecolor='black', hatch='//', label='Exceeds Norm Time')

# for i, route in enumerate(unique_routes):
#     ax = axes[i]
#     route_df = route_data[route_data["Route"] == route]
#     route_name = route_descriptions.get(route, route)

#     # Initialize exceed counts
#     blue_exceed_count = 0
#     red_exceed_count = 0

#     for backbone, color, label in zip(["Blue", "Red"], ["blue", "red"], ["Blue Backbone", "Red Backbone"]):
#         times = route_df[route_df["Backbone"] == backbone]["Time_in_System"] 
#         norm_time = norm_times.get(route, {}).get(backbone, float("inf"))
    
#         # Calculate exceeding counts and total items
#         if not times.empty:
#             exceed_count = (times > norm_time).sum()
#             total_items = len(times)  # Calculate total items for the current backbone
    
#             if backbone == "Blue":
#                 blue_exceed_count = exceed_count / num_seeds
#             elif backbone == "Red":
#                 red_exceed_count = exceed_count / num_seeds
    
#             # Plot histogram with hatching
#             bin_counts, bin_edges = np.histogram(times, bins=20)
#             for idx in range(len(bin_edges) - 1):
#                 hatch = "//" if bin_edges[idx] > norm_time else None
#                 ax.bar(
#                     bin_edges[idx],
#                     bin_counts[idx],
#                     width=bin_edges[idx + 1] - bin_edges[idx],
#                     color=color,
#                     edgecolor="black",
#                     alpha=0.6,
#                     hatch=hatch,
#                     label=f'{label}' if idx == 0 else ""  # Add dynamic label
#                 )


#     # Update subplot title with exceeding counts
#     ax.set_title(
#         f'Process Time: {route_name} Exceeding Norm (av.): Blue={blue_exceed_count}, Red={red_exceed_count}',
#         fontsize=10,
#     )
#     ax.set_xlabel("Process Time (seconds)")
#     ax.set_ylabel("Frequency")
#     ax.legend(loc="upper right")
#     ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    