# import random
# import matplotlib.pyplot as plt
# import numpy as np
from shapely import MultiPoint, Point

# def calculate_slope(point1, point2):
#     """Calculate the slope between two points."""
#     if point2[0] - point1[0] == 0:  # Avoid division by zero for vertical lines
#         return None  # Slope is undefined (vertical line)
#     return (point2[1] - point1[1]) / (point2[0] - point1[0])

# def find_perpendicular_slope(slope):
#     """Find the slope of the perpendicular line."""
#     if slope is None:  # Vertical line, perpendicular is horizontal (slope=0)
#         return 0
#     if slope == 0:  # Horizontal line, perpendicular is vertical (undefined slope)
#         return None
#     return -1 / slope

# def calculate_perpendicular_line(center, surrounding, distance_percent=0.25):
#     """Calculate and plot the perpendicular line through the midpoint."""
#     midpoint = [(center[0] + distance_percent * (surrounding[0] - center[0])),
#                 (center[1] + distance_percent * (surrounding[1] - center[1]))]
    
#     slope = calculate_slope(center, surrounding)
#     perp_slope = find_perpendicular_slope(slope)
    
#     if perp_slope is None:
#         # Perpendicular is a vertical line (x = constant)
#         x_values = np.full(100, midpoint[0])
#         y_values = np.linspace(midpoint[1] - 10, midpoint[1] + 10, 100)
#     else:
#         # Perpendicular line: y - y1 = m(x - x1)
#         x_values = np.linspace(midpoint[0] - 10, midpoint[0] + 10, 100)
#         y_values = perp_slope * (x_values - midpoint[0]) + midpoint[1]
    
#     return midpoint, perp_slope, midpoint[1] - perp_slope * midpoint[0] if perp_slope is not None else midpoint[0]

# def find_intersection(m1, b1, m2, b2):
#     """Find the intersection point of two lines given by their slope and intercept."""
#     if m1 == m2:
#         # If the slopes are equal, the lines are parallel and there is no intersection
#         return None
    
#     if m1 is None:  # Line 1 is vertical (x = constant)
#         x_int = b1  # x coordinate is the constant value
#         y_int = m2 * x_int + b2  # y = m2 * x + b2 for the second line
#     elif m2 is None:  # Line 2 is vertical
#         x_int = b2  # x coordinate is the constant value
#         y_int = m1 * x_int + b1  # y = m1 * x + b1 for the first line
#     else:
#         # Solve for x: m1*x + b1 = m2*x + b2
#         x_int = (b2 - b1) / (m1 - m2)
#         y_int = m1 * x_int + b1  # Substitute x into one of the line equations
    
#     return (x_int, y_int)

# # Example usage
# center = [0, 0]
# surrounding_points = [[random.uniform(-10, 10), random.uniform(-10, 10)] for _ in range(5)]
# perpendicular_lines = []
# intersection_points = []

# # Plotting
# plt.figure(figsize=(8, 8))
# for surrounding in surrounding_points:
#     # Plot the line connecting center and surrounding point
#     plt.plot([center[0], surrounding[0]], [center[1], surrounding[1]], 'b--')

#     # Calculate and plot the perpendicular line
#     midpoint, perp_slope, perp_intercept = calculate_perpendicular_line(center, surrounding)
#     plt.plot(midpoint[0], midpoint[1], 'ro')  # Plot the midpoint
    
#     # Store the line equation (slope and intercept) for later intersection calculation
#     perpendicular_lines.append((perp_slope, perp_intercept))
    
#     # Generate points for the perpendicular line
#     if perp_slope is None:
#         x_perp = np.full(100, perp_intercept)
#         y_perp = np.linspace(midpoint[1] - 10, midpoint[1] + 10, 100)
#     else:
#         x_perp = np.linspace(midpoint[0] - 10, midpoint[0] + 10, 100)
#         y_perp = perp_slope * (x_perp - midpoint[0]) + midpoint[1]
    
#     plt.plot(x_perp, y_perp, 'g')  # Plot the perpendicular line

# # Now calculate and plot intersections between each pair of perpendicular lines
# intersection_counter = 1  # Initialize the counter for numbering intersection points
# for i in range(len(perpendicular_lines)):
#     for j in range(i + 1, len(perpendicular_lines)):
#         m1, b1 = perpendicular_lines[i]
#         m2, b2 = perpendicular_lines[j]
#         intersection = find_intersection(m1, b1, m2, b2)
#         if intersection:
#             plt.plot(intersection[0], intersection[1], 'bo')  # Plot the intersection point
#             plt.text(intersection[0], intersection[1], f'{intersection_counter}', fontsize=10, color='blue')
#             intersection_points.append((intersection_counter, intersection))  # Store the intersection with its ID
#             intersection_counter += 1

# plt.scatter(center[0], center[1], color='black', label="Center Point", zorder=5)
# plt.xlim(-10, 10)
# plt.ylim(-10, 10)
# plt.grid(True)
# plt.axhline(0, color='black',linewidth=0.5)
# plt.axvline(0, color='black',linewidth=0.5)
# plt.legend()
# plt.show

# # Input the IDs of the selected intersections (in real usage, this can be input by the user)
# selected_ids = input("Enter the IDs of the 5 intersections (comma-separated, in desired polygon order): ")
# selected_ids = [int(x.strip()) for x in selected_ids.split(',')]

# # Extract the corresponding coordinates of the selected intersections
# selected_points = [point for idx, point in intersection_points if idx in selected_ids]

# # Check if exactly 5 points are selected
# if len(selected_points) != 5:
#     print("You must select exactly 5 intersection points.")
# else:
#     # Ensure the order of points follows the input order
#     selected_points = np.array([point for idx in selected_ids for id_point, point in intersection_points if id_point == idx])
    
#     # Draw the polygon on top of the existing graph
#     polygon = plt.Polygon(selected_points, fill=None, edgecolor='r', linewidth=2)
#     plt.gca().add_patch(polygon)
    
#     # Redraw the graph with the polygon
#     plt.xlim(-10, 10)
#     plt.ylim(-10, 10)
#     plt.grid(True)
#     plt.axhline(0, color='black',linewidth=0.5)
#     plt.axvline(0, color='black',linewidth=0.5)
#     plt.legend()
#     plt.show()