import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Parse environment variables
        self.THRESHOLD_PIXELS = int(os.getenv("THRESHOLD_PIXELS"))
        self.WHITE_THRESHOLD_PERCENTAGE = int(os.getenv("WHITE_THRESHOLD_PERCENTAGE"))
        self.INPUT_DIRECTORY_PATH = os.getenv("INPUT_DIRECTORY_PATH")
        self.OUTPUT_DIRECTORY_PATH = os.getenv("OUTPUT_DIRECTORY_PATH")
