import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def calculate_reactions(supports, point_loads, distributed_loads, moments, beam_length):
    num_supports = len(supports)
    if num_supports == 1:
        for support_types, position in supports:
            if support_types == "Fixed":
                sum_point_loads = 0
                sum_dist_loads = 0
                sum_point_loads_moments = 0
                sum_dist_loads_moments = 0
                sum_external_moments = 0

                fixed_support_pos = position

                for position, magnitude in point_loads:
                    sum_point_loads += magnitude
                    sum_point_loads_moments += magnitude * abs(position - fixed_support_pos)

                for start_pos, end_pos, start_mag, end_mag in distributed_loads:
                    sum_dist_loads += 0.5 * (start_mag + end_mag) * (abs(end_pos-start_pos))
                    if end_mag+start_mag != 0 :
                        centroid_left = ((abs(end_pos-start_pos))/3) * ((2*end_mag+start_mag)/(end_mag+start_mag))
                        centroid_right = abs(start_pos - end_pos) - centroid_left
                        distance_left = min(start_pos, end_pos)
                        distance_right = beam_length - max(start_pos, end_pos)
                        if fixed_support_pos == 0:
                            sum_dist_loads_moments += 0.5 * (start_mag + end_mag) * (abs(end_pos-start_pos)) * (centroid_left+distance_left)
                        else:
                            sum_dist_loads_moments += 0.5 * (start_mag + end_mag) * (abs(end_pos-start_pos)) * (centroid_right+distance_right)
                    # else:
                    #     return False

                for position, magnitude in moments:
                    sum_external_moments += magnitude

                reaction_1 = -sum_point_loads - sum_dist_loads
                moment_1 = sum_point_loads_moments +sum_dist_loads_moments -sum_external_moments

                reaction_moment = [reaction_1, moment_1]
                reaction_moment_pos = []
                for support_types, position in supports:
                    reaction_moment_pos.append(position)
                reactions = []
                for i in reaction_moment:
                    reactions.append((reaction_moment_pos[0],i))

                # st.write(reactions)
                reaction_direction ="🡻" if reactions[0][1] <0 else "🢁"
                st.write('Reaction at Fixed Support: ', abs(round(reactions[0][1],2)), " kN ", reaction_direction)
                moment_direction = "Clockwise" if reactions[1][1] >0 else "Anticlockwise"
                st.write('Moment at Fixed Support: ', abs(round(reactions[1][1],2)), ' kNm (', moment_direction, ' )')
                return reactions
            else:
                return st.write("Unable to Solve")



    elif num_supports == 2:
        if any(support_type == "Fixed" for support_type, position in supports):
            return False
        else:
            sum_point_loads = 0
            sum_dist_loads = 0
            sum_point_loads_moments = 0
            sum_dist_loads_moments = 0
            sum_external_moments = 0

            for position, magnitude in point_loads:
                sum_point_loads += magnitude
                sum_point_loads_moments += magnitude*(position)
            for start_pos, end_pos, start_mag, end_mag in distributed_loads:
                sum_dist_loads += 0.5 * (start_mag + end_mag) * (abs(end_pos-start_pos))
                if end_mag+start_mag != 0 :
                    centroid_left = ((abs(end_pos-start_pos))/3) * ((2*end_mag+start_mag)/(end_mag+start_mag))
                    distance_left = min(start_pos, end_pos)
                    sum_dist_loads_moments += 0.5 * (start_mag + end_mag) * (abs(end_pos-start_pos)) * (centroid_left+distance_left)
                else:
                    st.write("")

            for position, magnitude in moments:
                sum_external_moments += magnitude
            
            # [(1,1), (support_1_pos, support_2_pos)]*[(r1, r2)] = [(sum_point_load+sum_dist_load), (sum_point_moment+sum_dist_moment+sum_external_moment)]
            # format: Ax = B
            # formula: x = np.linalg.solve(A, B) 

            reaction_coefficient_mat = [(1,1)]
            support_position = []
            for support_type, position in supports:
                support_position.append(position)
            reaction_coefficient_mat.append(support_position)
            # st.write(reaction_coefficient_mat)

            constant_mat = [(sum_point_loads + sum_dist_loads), (sum_point_loads_moments + sum_dist_loads_moments - sum_external_moments)]
            # st.write(constant_mat)

            try:
                r = np.linalg.solve(reaction_coefficient_mat, constant_mat)
                r1, r2 = -r
            except np.linalg.LinAlgError:
                r1 = 0
                r2 = 0

        reaction_mag = [r1, r2]
        reaction_pos = []
        for support_types, position in supports:
            reaction_pos.append(position)
        reactions = []
        for a, b in zip(reaction_pos, reaction_mag):
            reactions.append((a,b))

        reactions = sorted(reactions, key=lambda x: x[0])
        # st.write(reactions)
        reaction_direction_A ="🡻" if reactions[0][1] <0 else "🢁"
        st.write('Reaction at Support A: ', abs(round(reactions[0][1],2)), " kN ", " ", reaction_direction_A)
        reaction_direction_B ="🡻" if reactions[1][1] <0 else "🢁"
        st.write('Reaction at Support B: ', abs(round(reactions[1][1],2)), ' kN ', reaction_direction_B)
        
        return reactions
    else:
        return False