import os


class DIRECTORIES:
    OUTPUT = os.path.join(os.getcwd(), "output")
    File_Path = os.path.join(OUTPUT, "NewsFromReuters.xlsx")
    IMG_Path = os.path.join(OUTPUT, "images")
    ERROR_SCREENSHOT_PATH = os.path.join(OUTPUT, "error.png")
    ARCH_Path = IMG_Path
