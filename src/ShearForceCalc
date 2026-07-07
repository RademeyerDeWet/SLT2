import streamlit as st
import numpy as np

def shear_force(support_reactions, point_loads, distributed_loads, beam_length, resolution):
    shear = [0.0] * (int(beam_length * resolution) + 1) #define list for shear
    x_coords = np.linspace(0, beam_length, len(shear))

    # add support reactions to shear force
    # st.write(type(support_reactions))
    if support_reactions:
        for position, magnitude in support_reactions:
            for i, x in enumerate(x_coords):
                if x >= position:
                    shear[i] +=magnitude
    # add point load to the shear force
    for position, magnitude in point_loads:
        for i, x in enumerate(x_coords):
            if x>= position:
                shear[i] += magnitude
    for start_pos, end_pos, start_mag, end_mag in distributed_loads:
        for i, x in enumerate(x_coords):
            if start_pos <= x <= end_pos:
                # Calculate the load at position x
                load = start_mag + (end_mag - start_mag) * ((x - start_pos) / (end_pos - start_pos))
                # Incremental load based on segment size
                increment = load * (x_coords[1] - x_coords[0])
                # Update shear for all positions y >= x
                for j, y in enumerate(x_coords):
                    if y >= x:
                        shear[j] += increment  #  load increment  # Apply and accumulate the load
                        # st.write(f"x: {x}, Load: {load:.2f}, Increment: {increment:.2f}, Updated Shear: {shear[i]:.2f}")
    return x_coords, shear