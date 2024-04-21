import cv2
import numpy as np

def resize_image(img, target_height, target_width):
    return cv2.resize(img, (target_width, target_height))

def add_text_to_image(img, text, position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 0, 0), thickness=2):
    cv2.putText(img, text, position, font, font_scale, color, thickness)

def stitch_images(image_paths, output_path, text_list=None, target_height=None, target_width=None, final_height=None, final_width=None):
    images = []
    max_height = 0
    total_width = 0

    # Load images and find the maximum height and total width
    for path in image_paths:
        img = cv2.imread(path)
        images.append(img)
        max_height = max(max_height, img.shape[0])
        total_width += img.shape[1]

    # If target height or width is not specified, use the maximum height and width of the input images
    if target_height is None:
        target_height = max_height
    if target_width is None:
        target_width = total_width // len(image_paths)

    # Calculate the number of rows and columns for the grid
    num_images = len(image_paths)
    num_rows = int(np.sqrt(num_images))
    num_cols = (num_images + num_rows - 1) // num_rows  # Calculate number of columns such that each row but the last is filled

    # Resize images to fit into grid cells
    resized_images = []
    for img in images:
        resized_img = resize_image(img, target_height, target_width)
        resized_images.append(resized_img)

    # Create a blank canvas for stitching images
    stitched_height = num_rows * target_height
    stitched_width = num_cols * target_width
    stitched_image = np.zeros((stitched_height, stitched_width, 3), dtype=np.uint8)

    # Paste resized images onto the canvas
    row = 0
    col = 0
    for img, text in zip(resized_images, text_list):
        if col == num_cols:
            col = 0
            row += 1
        y_offset = row * target_height
        x_offset = col * target_width
        stitched_image[y_offset:y_offset + target_height, x_offset:x_offset + target_width] = img
        add_text_to_image(stitched_image, text, position=(x_offset + 10, y_offset + 30))  # Add text to the bottom left corner of each cell
        col += 1

    # Resize the stitched image to the final specified size
    if final_height is not None and final_width is not None:
        stitched_image = resize_image(stitched_image, final_height, final_width)

    # Save the stitched image
    cv2.imwrite(output_path, stitched_image)
    print("Stitched image saved to:", output_path)

# Example usage:
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg", "image7.jpg","image6.jpg","image8.jpg","image9.jpg","image10.jpg","image11.jpg"]  # Replace with your image paths
text_list = ["Name 1", "Name 2", "Name 3", "Name 4", "Name 7","Name 6","Name 8","Name 9","Name 10","Name 11"]  # Replace with your text list
output_path = "stitched_image.jpg"  # Replace with your desired output path
stitch_images(image_paths, output_path, text_list=text_list, target_height=300, target_width=400)  # Replace with desired dimensions
