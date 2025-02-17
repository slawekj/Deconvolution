import click
import numpy as np
from matplotlib import pyplot as plt


@click.command()
@click.option('--long-diameter-file', '-l',
              type=click.Path(exists=True),
              required=True,
              help='Path to the long diameter file')
@click.option('--short-diameter-file', '-s',
              type=click.Path(exists=True),
              required=True,
              help='Path to the short diameter file')
@click.option('--output-file', '-o',
              type=click.Path(exists=False),
              required=True,
              help='Path to the output file')
@click.option('--skip-plotting-results',
              is_flag=True,
              default=False,
              help='Weather to skip plotting the results')
@click.option('--skip-printing-rings',
              is_flag=True,
              default=False,
              help='Weather to skip printing the ring avg z values')
def extrapolate_ellipse(long_diameter_file, short_diameter_file, output_file, skip_plotting_results,
                        skip_printing_rings):
    # Load the tab-separated values files into NumPy arrays
    long_diameter = np.loadtxt(long_diameter_file, delimiter='\t')
    short_diameter = np.loadtxt(short_diameter_file, delimiter='\t')

    min_long_diameter = np.min(long_diameter[:, 0])
    max_long_diameter = np.max(long_diameter[:, 0])

    min_short_diameter = np.min(short_diameter[:, 0])
    max_short_diameter = np.max(short_diameter[:, 0])

    radii_ratio = max_long_diameter / max_short_diameter

    def calculate_ellipse_radii(x, y, ratio):
        # Calculate the long radius (r1) and short radius (r2) from ellipsis condition
        long_radius = np.sqrt(x ** 2 + (ratio ** 2) * y ** 2)
        short_radius = np.sqrt((x ** 2) / (ratio ** 2) + y ** 2)
        return long_radius, short_radius

    def step_function(x_matrix, y_matrix):
        # Calculate r1 and r2 for the ellipsis
        r1, r2 = calculate_ellipse_radii(x_matrix, y_matrix, radii_ratio)

        # Calculate the intersection points with the x and y axes
        x_axis_intersection = np.sign(x_matrix) * r1
        y_axis_intersection = np.sign(y_matrix) * r2

        # Find the closest values in long_diameter and short_diameter
        long_idx = np.argmin(np.abs(long_diameter[:, 0, np.newaxis, np.newaxis] - x_axis_intersection), axis=0)
        short_idx = np.argmin(np.abs(short_diameter[:, 0, np.newaxis, np.newaxis] - y_axis_intersection), axis=0)

        long_value = long_diameter[long_idx, 1]
        short_value = short_diameter[short_idx, 1]

        # Calculate the elliptical distances from the axes
        distance_x = np.sqrt((x_matrix - x_axis_intersection) ** 2 + (y_matrix / radii_ratio) ** 2)
        distance_y = np.sqrt((y_matrix - y_axis_intersection) ** 2 + (x_matrix / radii_ratio) ** 2)
        total_distance = distance_x + distance_y

        # Calculate the weighted average based on the distances
        result = np.where(total_distance == 0, (long_value + short_value) / 2,
                          (long_value * (distance_y / total_distance) + short_value * (distance_x / total_distance)))

        return result

    def compute_sum_and_count_inside_ellipse(grid_z, grid_x, grid_y, short_radius, long_radius):
        # Create a mask for points inside or on the ellipse
        ellipse_mask = (grid_x / long_radius) ** 2 + (grid_y / short_radius) ** 2 <= 1

        # Filter grid_z using the mask
        points_inside_ellipse = grid_z[ellipse_mask]

        # Compute the sum and count of the filtered points
        sum_values = np.sum(points_inside_ellipse)
        count_values = points_inside_ellipse.size

        return sum_values, count_values

    # Generate a grid of points
    grid_x, grid_y = np.mgrid[min_long_diameter:max_long_diameter:500j, min_short_diameter:max_short_diameter:500j]

    # Apply the step function to the distances to get the z-values
    grid_z = step_function(grid_x, grid_y)

    if not skip_printing_rings:
        print_avg_z_rings(compute_sum_and_count_inside_ellipse, grid_x, grid_y, grid_z, long_diameter,
                          long_diameter_file,
                          radii_ratio, short_diameter_file)

    # Create a 2D matrix to store the data
    matrix = np.zeros((grid_y.shape[0] + 1, grid_x.shape[1] + 1))

    # Fill the first row with X values and the first column with Y values
    matrix[0, 1:] = grid_x[:, 0]
    matrix[1:, 0] = grid_y[0, :]

    # Fill the remaining cells with Z values
    matrix[1:, 1:] = grid_z

    # Save the matrix to a .dpt file
    np.savetxt(output_file, matrix, delimiter='\t')

    # Plot the 2D contour plot
    if not skip_plotting_results:
        plt.contourf(grid_x, grid_y, grid_z, cmap='viridis')
        plt.colorbar(label='Z')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Visualization based on cross-section data')
        plt.show()


def print_avg_z_rings(compute_sum_and_count_inside_ellipse,
                      grid_x,
                      grid_y,
                      grid_z,
                      long_diameter,
                      long_diameter_file,
                      radii_ratio,
                      short_diameter_file):
    print(f"{long_diameter_file} {short_diameter_file}")
    print("")
    rows = [row for row in long_diameter if row[0] > 0 and row[1] > 0]

    # Initialize dynamic programming table
    sums = [0] * len(rows)
    counts = [0] * len(rows)

    for i in range(len(rows)):
        row = rows[i]
        r1 = row[0]
        r2 = r1 / radii_ratio
        sums[i], counts[i] = compute_sum_and_count_inside_ellipse(grid_z, grid_x, grid_y, r1, r2)

    for i in range(len(rows)):
        row = rows[i]
        r1 = row[0]
        r2 = r1 / radii_ratio
        if i == 0:
            sum_z = sums[i]
            count_z = counts[i]
            print(f"Ellipse r1={r1:.2f} r2={r2:.2f}: avg z: {sum_z / count_z:.2f}")
        else:
            sum_z = sums[i] - sums[i - 1]
            count_z = counts[i] - counts[i - 1]
            print(f"Ring r1={r1:.2f} r2={r2:.2f}: avg z: {sum_z / count_z:.2f}")


if __name__ == '__main__':
    extrapolate_ellipse()
