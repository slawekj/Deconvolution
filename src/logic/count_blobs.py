import click
from skimage import feature, color, io
import matplotlib.pyplot as plt


@click.command()
@click.option("--input-path", type=click.Path(exists=True), required=True, help="Path to the input image")
@click.option("--output-path", type=click.Path(), help="Path to the output image")
@click.option("--box-min-x", type=int, default=0, help="Minimum x-coordinate of the box")
@click.option("--box-max-x", type=int, default=-1, help="Maximum x-coordinate of the box")
@click.option("--box-min-y", type=int, default=0, help="Minimum y-coordinate of the box")
@click.option("--box-max-y", type=int, default=-1, help="Maximum y-coordinate of the box")
@click.option("--log-min-sigma", type=float, default=1, help="Laplacian of Gaussian minimum sigma")
@click.option("--log-max-sigma", type=float, default=2, help="Laplacian of Gaussian maximum sigma")
@click.option("--log-threshold", type=float, default=0.01, help="Laplacian of Gaussian threshold")
@click.option('--skip-plotting-results',
              is_flag=True,
              default=False,
              help='Weather to skip plotting the results')
@click.option('--skip-saving-results',
              is_flag=True,
              default=False,
              help='Weather to skip saving the results')
def count_blobs(input_path,
                output_path,
                box_min_x,
                box_max_x,
                box_min_y,
                box_max_y,
                log_min_sigma,
                log_max_sigma,
                log_threshold,
                skip_plotting_results,
                skip_saving_results):
    image = color.rgb2gray(io.imread(input_path))

    box_max_x = image.shape[0] if box_max_x == -1 else box_max_x
    box_max_y = image.shape[1] if box_max_y == -1 else box_max_x

    blobs_log = feature.blob_log(
        image,
        min_sigma=log_min_sigma,
        max_sigma=log_max_sigma,
        threshold=log_threshold
    )

    # Compute radii
    blobs_log[:, 2] = blobs_log[:, 2] * (2 ** 0.5)

    # Filter blobs inside the box
    blobs_in_box = [
        (y, x, r)
        for y, x, r in blobs_log
        if box_min_x <= x <= box_max_x and box_min_y <= y <= box_max_y
    ]

    # Display
    fig, ax = plt.subplots()
    ax.imshow(image, cmap='gray')

    # Draw the box
    rect = plt.Rectangle(
        (box_min_x, box_min_y),
        box_max_x - box_min_x,
        box_max_y - box_min_y,
        linewidth=1.5,
        edgecolor='blue',
        facecolor='none'
    )
    ax.add_patch(rect)

    # Draw blobs inside the box
    for y, x, r in blobs_in_box:
        c = plt.Circle((x, y), r, color='red', linewidth=0.5, fill=False)
        ax.add_patch(c)

    if not skip_plotting_results:
        plt.show()
    if not skip_saving_results:
        plt.savefig(output_path)

    print(f"Total blobs found in box: {len(blobs_in_box)}")


if __name__ == '__main__':
    count_blobs()
