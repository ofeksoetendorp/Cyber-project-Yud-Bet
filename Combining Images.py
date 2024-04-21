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

    # Resize images to have equal height and width
    resized_images = [resize_image(img, target_height, target_width) for img in images]

    # Add text to each image
    if text_list is not None:
        for img, text in zip(resized_images, text_list):
            add_text_to_image(img, text)

    # Create a blank canvas for stitching images
    stitched_image = np.zeros((target_height, total_width, 3), dtype=np.uint8)

    # Paste resized images onto the canvas
    x_offset = 0
    for img in resized_images:
        h, w = img.shape[:2]
        stitched_image[:h, x_offset:x_offset + w] = img
        x_offset += w

    # Resize the stitched image to the final specified size
    if final_height is not None and final_width is not None:
        stitched_image = resize_image(stitched_image, final_height, final_width)

    # Save the stitched image
    cv2.imwrite(output_path, stitched_image)
    print("Stitched image saved to:", output_path)

# Example usage:
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]  # Replace with your image paths
text_list = ["Name 1", "Name 2", "Name 3"]  # Replace with your text list
output_path = "stitched_image.jpg"  # Replace with your desired output path
stitch_images(image_paths, output_path, text_list=text_list, target_height=300, target_width=600, final_height=600, final_width=4000)  # Replace with desired dimensions
