import os

from RPA.Excel.Files import Files


class Excel:
    def __init__(self) -> None:
        self.files = Files()

    def create_excel(self, worksheet_data: dict, filepath: str, index) -> None:
        """Creates an Excel file with the given news data.
        """
        try:
            if os.path.exists(filepath):
                self.files.open_workbook(filepath)
                self.files.create_worksheet(
                    name=f"Sheet{index}", content=worksheet_data, header=True)
                self.files.save_workbook(filepath)
            else:
                self.files.create_workbook()
                self.files.create_worksheet(
                    name=f"Sheet{index}", content=worksheet_data, header=True)
                self.files.save_workbook(filepath)

        except Exception as e:
            print(f"Error in creating excel---{e}")

        finally:
            self.files.open_workbook(filepath)
            if self.files.worksheet_exists(name="Sheet"):
                self.files.remove_worksheet(name="Sheet")
            self.files.save_workbook(filepath)
            pass
