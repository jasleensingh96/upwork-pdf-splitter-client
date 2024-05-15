import configparser


class Config:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        self.THRESHOLD_PIXELS = int(config["THRESHOLD"]["THRESHOLD_PIXELS"])
        self.WHITE_THRESHOLD_PERCENTAGE = int(config["THRESHOLD"]["WHITE_THRESHOLD_PERCENTAGE"])
        self.INPUT_DIRECTORY_PATH = config["DIRECTORY"]["INPUT_DIRECTORY_PATH"]
        self.OUTPUT_DIRECTORY_PATH = config["DIRECTORY"]["OUTPUT_DIRECTORY_PATH"]

