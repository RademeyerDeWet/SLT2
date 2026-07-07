import streamlit as st
import numpy as np

def bending_moment(supports, support_reactions, support_moments, point_loads, distributed_loads, external_moments, beam_length, resolution):
    bending_moment = [0.0] * (int(beam_length * resolution) + 1)
    x_coords = np.linspace(0, beam_length, len(bending_moment))

    #fixed support postion
    for support_types, position in supports:
        if support_types == "Fixed":
            fixed_support_pos = position

    # add support reaction moment to bending moment
    if support_reactions:
        for position, magnitude in support_reactions:
            for i, x in enumerate(x_coords):
                if x >= position:
                    bending_moment[i] += magnitude * (x-position)

    # add support moments to bending moment
    if support_moments:
        for position, magnitude in support_moments:
            for i, x in enumerate(x_coords):
                if x >= position:
                    if fixed_support_pos == 0:
                        bending_moment[i] += magnitude
                    else:
                        bending_moment[i] -= magnitude
    
    # add point load to the bending moment
    for position, magnitude in point_loads:
        for i, x in enumerate(x_coords):
            if x>=position:
                bending_moment[i] += magnitude * (x-position)
    
    # add distributed loads to the bending monet
    for start_pos, end_pos, start_mag, end_mag in distributed_loads:
        for i, x in enumerate(x_coords):
            if start_pos <= x <= end_pos:
                # Calculate the load at position x using linear interpolation
                load = start_mag + (end_mag - start_mag) * ((x - start_pos) / (end_pos - start_pos))

                # Incremental load based on the segment size
                increment = load * (x_coords[1] - x_coords[0])

                # Update bending moment for all positions y >= x (similar to shear force approach)
                for j, y in enumerate(x_coords):
                    if y >= x:
                        bending_moment[j] += (y - x) * increment
    
    # add external moments
    for position, magnitude in external_moments:
        for i, x in enumerate(x_coords):
            if x >= position:
                bending_moment[i] += magnitude

    return x_coords, bending_moment