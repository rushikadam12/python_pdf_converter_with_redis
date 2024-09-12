import subprocess
import os
import uuid
from dotenv import load_dotenv
from io import BytesIO
import subprocess
import shutil


load_dotenv()


def Ppt_To_Pdf(file_path, file_id):
    try:
        command = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            file_path,
            "--outdir",
            os.environ.get("STORAGE_PATH"),
        ]
        subprocess.run(command, check=True)

        # find the the converted pdf file and return it
        list_dir = os.listdir(os.environ.get("STORAGE_PATH"))
        for dir in list_dir:
            _, ext = os.path.splitext(dir)
            if ext == ".pdf":
                print(f"FILE APTH :{dir}")
                return dir

        return "ppt to pdf conversion failed"

    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path} to PDF: {e}")
        return False
    except Exception as e:

        return str(e)
