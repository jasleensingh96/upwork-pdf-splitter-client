class PDFResponse:
    def __init__(
        self,
        border_image_paths_with_page_no,
        pdf_with_color_path,
        pages_with_color_count,
        pdf_without_color_path,
        pages_without_color_count,
    ):
        self.border_image_paths_with_page_no: dict = border_image_paths_with_page_no
        self.pdf_with_color_path: str = pdf_with_color_path
        self.pages_with_color_count: int = pages_with_color_count
        self.pdf_without_color_path: str = pdf_without_color_path
        self.pages_without_color_count: int = pages_without_color_count
