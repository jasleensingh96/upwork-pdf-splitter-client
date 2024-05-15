import os

from config import Config
from dto import PDFResponse
from service import (
    get_pdf_files,
    create_folder_with_timestamp,
    extract_page_as_image_with_border_check,
    get_pdf_with_max_pages,
)

config = Config()


def main():
    try:
        pdf_files = get_pdf_files(config.INPUT_DIRECTORY_PATH)
    except FileNotFoundError:
        os.makedirs(config.INPUT_DIRECTORY_PATH, exist_ok=True)
        print(f"ERROR: Place file in the '{config.INPUT_DIRECTORY_PATH}' folder first.")
        return

    output_folder = create_folder_with_timestamp(config)

    card_file_path = get_pdf_with_max_pages(pdf_files)
    print(f"Card File: {card_file_path}\n\n")

    for pdf_file in pdf_files:
        print(f"Processing file: {pdf_file}...")

        file_name_without_extension = os.path.basename(pdf_file)[:-4]
        is_card_file = True if card_file_path == pdf_file else False

        pdf_response: PDFResponse = extract_page_as_image_with_border_check(
            pdf_file, file_name_without_extension, output_folder, config, is_card_file
        )
        print(f"White Page Count: {pdf_response.pages_without_color_count}")
        print(f"Colored Page Count: {pdf_response.pages_with_color_count}\n\n")

    print(f"Check the final pdfs: {output_folder}")


main()
