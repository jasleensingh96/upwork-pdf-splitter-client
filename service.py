import os
from datetime import datetime

import cv2
import fitz
import numpy as np

from dto import PDFResponse


def has_color_in_border(image_array, white_threshold_percentage, border_width):
    # Get the dimensions of the image
    height, width, _ = image_array.shape

    # Get the border regions of the image
    top_border_right_half = image_array[:border_width, width // 2 :, :]
    bottom_border_right_half = image_array[height - border_width :, width // 2 :, :]
    right_border = image_array[:, width - border_width :, :]

    # Calculate the number of white pixels in the right half of top and bottom borders
    num_pixels_top_right_half = np.sum(np.all(top_border_right_half == [255, 255, 255], axis=-1))
    num_pixels_bottom_right_half = np.sum(np.all(bottom_border_right_half == [255, 255, 255], axis=-1))
    num_pixels_right_border = np.sum(np.all(right_border == [255, 255, 255], axis=-1))

    # Calculate the percentage of white pixels
    percentage_white_top_right_half = (num_pixels_top_right_half / (border_width * (width // 2))) * 100
    percentage_white_bottom_right_half = (num_pixels_bottom_right_half / (border_width * (width // 2))) * 100
    percentage_white_right_border = (num_pixels_right_border / (height * border_width)) * 100

    # If the percentage of white pixels in both borders is below the threshold, return False
    return (
        percentage_white_top_right_half < white_threshold_percentage
        or percentage_white_bottom_right_half < white_threshold_percentage
        or percentage_white_right_border < white_threshold_percentage
    )


def draw_border_on_image(image_array, height, width, border_width, has_color):
    image_with_border = image_array.copy()

    # Draw lines to mark the border region on top, bottom, and right
    cv2.line(image_with_border, (width // 2, border_width), (width - 1, border_width), (0, 255, 0), 2)  # Top
    cv2.line(
        image_with_border, (width // 2, height - border_width), (width - 1, height - border_width), (0, 255, 0), 2
    )  # Bottom
    cv2.line(image_with_border, (width - border_width, 0), (width - border_width, height - 1), (0, 255, 0), 2)  # Right

    # Add text on the top right based on has_color value
    image_text = "White"
    if has_color:
        image_text = "Color"
    cv2.putText(image_with_border, image_text, (width - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return image_with_border


def extract_page_as_image_with_border_check(
    pdf_path, file_name_without_extension, output_folder, config, is_card_file=False
):
    # Open the PDF
    output_border_image_path_with_page_no_dict = {}
    pdf_with_color_path = os.path.join(output_folder, f"{file_name_without_extension}-color.pdf")
    pdf_without_color_path = os.path.join(output_folder, f"{file_name_without_extension}-white.pdf")

    pdf_document = fitz.open(pdf_path)
    pdf_with_color = fitz.open()
    pdf_without_color = fitz.open()

    if is_card_file and len(pdf_document) % 2 != 0:
        return -1

    dpi = 300

    temp_image_folder = os.path.join(output_folder, "temp_images", file_name_without_extension)
    os.makedirs(temp_image_folder, exist_ok=True)

    page_jump = 2 if is_card_file else 1
    for page_index in range(0, len(pdf_document), page_jump):
        output_border_image_path = os.path.join(temp_image_folder, f"{page_index + 1}.jpg")

        page = pdf_document.load_page(page_index)
        zoom_level = dpi / 72

        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))

        image_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
        height, width, _ = image_array.shape

        has_color = has_color_in_border(image_array, config.WHITE_THRESHOLD_PERCENTAGE, config.THRESHOLD_PIXELS)
        image_array_with_border = draw_border_on_image(image_array, height, width, config.THRESHOLD_PIXELS, has_color)

        cv2.imwrite(output_border_image_path, image_array_with_border)
        output_border_image_path_with_page_no_dict[page_index + 1] = output_border_image_path

        to_page = page_index + 1 if is_card_file else page_index
        if has_color:
            pdf_with_color.insert_pdf(pdf_document, from_page=page_index, to_page=to_page)
        else:
            pdf_without_color.insert_pdf(pdf_document, from_page=page_index, to_page=to_page)

    pdf_with_color_len = len(pdf_with_color)
    pdf_without_color_len = len(pdf_without_color)

    if pdf_with_color_len:
        pdf_with_color.save(pdf_with_color_path)
    if pdf_without_color_len:
        pdf_without_color.save(pdf_without_color_path)

    pdf_document.close()
    pdf_with_color.close()
    pdf_without_color.close()

    return PDFResponse(
        border_image_paths_with_page_no=output_border_image_path_with_page_no_dict,
        pdf_with_color_path=pdf_with_color_path,
        pages_with_color_count=pdf_with_color_len,
        pdf_without_color_path=pdf_without_color_path,
        pages_without_color_count=pdf_without_color_len,
    )


# Function to create a folder with the current timestamp
def create_folder_with_timestamp(config):
    current_datetime = datetime.now()
    folder_name = os.path.join(config.OUTPUT_DIRECTORY_PATH, current_datetime.strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(folder_name)
    return folder_name


def get_pdf_files(directory):
    pdf_files = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith(".pdf"):
                pdf_files.append(entry.path)
    return pdf_files


def get_pdf_page_count(file_path):
    with fitz.open(file_path) as pdf:
        return pdf.page_count


def get_pdf_with_max_pages(pdf_files):
    max_pdf_path = ""
    max_pdf_pages = 0

    for file_path in pdf_files:
        current_pdf_pages = get_pdf_page_count(file_path)
        if current_pdf_pages > max_pdf_pages:
            max_pdf_path = file_path

    return max_pdf_path
