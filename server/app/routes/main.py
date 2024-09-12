from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    Response,
    make_response,
    send_file,
)
from functools import wraps
from fpdf import FPDF
import pdfkit
import uuid
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
from app import redis_client
import json
import base64
import io
import subprocess
import zipfile
from xhtml2pdf import pisa
from weasyprint import HTML
from app.controller.converter import Ppt_To_Pdf

# from app.controller.html_converter import html_converter

main_dp = Blueprint("main_dp", __name__)
load_dotenv()


@main_dp.route("/")
def index():
    return ""


def compute_has_for_file(file_stream):
    hash_algo = hashlib.sha256()

    for chunk in iter(lambda: file_stream.read(4096), b""):
        # to read the file in chunks of 4096=4kb
        hash_algo.update(chunk)
    file_stream.seek(0)  # rest the stream
    return hash_algo.hexdigest()


def cache_file(cache_key, file_name, file_bytes):
    # print(file_bytes)
    redis_client.hset(
        cache_key,
        mapping={
            "file_name": file_name,
            "converted_file": "",
            "file_bytes": base64.b64encode(file_bytes).decode("utf-8"),
        },
    )

    return cache_key


@main_dp.route("/fileupload", methods=["POST"])
def file_upload():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    userId = session["user_id"]
    User_file = request.files["file"]

    file_hash = compute_has_for_file(User_file.stream)
    User_file.seek(0)
    # check if the file exist in redis
    if redis_client.exists(file_hash):
        hash_values = redis_client.hgetall(file_hash)
        # print(hash_values)
        file_name = hash_values[b"file_name"].decode("utf-8")
        try:
            file_bytes = base64.b64decode(hash_values[b"file_bytes"]).decode("utf-8")
        except UnicodeDecodeError:
            file_bytes = base64.b64decode(hash_values[b"file_bytes"])
            if ".html" in file_name:
                file_bytes_string = str(file_bytes)

        response = make_response(
            {
                "file_hash": str(file_hash),
                "file_name": str(file_name),
                "file_bytes": str(file_bytes)[:15],
                "message": "cache file",
            }
        )

        return response

    file_bytes = User_file.read()  # convert into bytes
    cache_key = cache_file(file_hash, User_file.filename, file_bytes)
    print(cache_key)
    response = make_response({"message": "file new file found"})
    response.set_cookie("file_id", file_hash, httponly=True, secure=True)
    return response


@main_dp.route("/convert_xlsx_to_pdf")
def convert_xlsx():
    try:

        file_hash = request.cookies.get("file_id")
        session_id = session.get("userId")

        # check for cache and return
        if file_hash is None:
            return jsonify({"message": "file not found pls check the file"})

        cache_file = redis_client.hget(file_hash, "converted_file")
        # check for cache and return the cache file
        if cache_file:
            cache_response = Response(cache_file, content_type="application/pdf")
            cache_response.headers["Content-Disposition"] = (
                'attachment;filename="converted_file.pdf"'
            )
            return cache_response

        file_data = redis_client.hgetall(file_hash)
        file_name = file_data[b"file_name"].decode("utf-8")
        file_split_name, file_extension = os.path.splitext(file_name)
        file_bytes = base64.b64decode(file_data[b"file_bytes"])
        file_like = io.BytesIO(file_bytes)

        # check for file types
        if ".xls" == file_extension:
            df = pd.read_excel(
                file_bytes,
                engine="xlrd",
            )

        # for new file format 'xlsx'
        elif ".xlsx" == file_extension:
            df = pd.read_excel(file_bytes, engine="openpyxl")
            print("i execute")
        else:
            return {"message": "unsupported file type"}

        pdf = FPDF()

        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        columns_widths = [pdf.get_string_width(str(col)) for col in df.columns]
        columns_widths = [max(width, 40) for width in columns_widths]

        # column headers
        pdf.set_font("Arial", "B", 12)
        for i, col in enumerate(df.columns):
            header_text = str(col)
            pdf.cell(columns_widths[i], 10, txt=header_text, border=1, align="c")
        pdf.ln()

        pdf.set_font("Arial", size=12)
        for _, row in df.iterrows():  # add data rows
            for i, value in enumerate(row):
                row_text = str(value)
                print(f"Writing value: {row_text} (type: {type(value)})")
                pdf.cell(columns_widths[i], 10, txt=row_text, border=1, align="c")
            pdf.ln()

        # save the pdf buffer to memory
        pdf_Buffer = io.BytesIO()
        pdf.output(pdf_Buffer)
        pdf_Buffer.seek(0)  # go to the start of the buffer to read

        # read the buffer
        pdf_bytes = pdf_Buffer.read()
        if not pdf_bytes:
            return "not able to read pdf bytes"

        # base64_pdf_encoding=base64.b64encode(pdf_bytes).decode("utf-8")
        print("file os converted ")

        redis_client.hset(file_hash, "converted_file", pdf_bytes)

        # cache values
        hash_values = redis_client.hget(file_hash, "converted_file")
        if hash_values:

            response = Response(hash_values, content_type="application/pdf")
            response.headers["Content-Disposition"] = (
                'attachment;filename="converted_file.pdf"'
            )
            return response
        else:
            return "something went wrong"

    except Exception as e:
        return str(e)


@main_dp.route("/ppt_to_pdf", methods=["POST"])
def convert_ppt_to_pdf():

    try:
        file_hash = request.cookies.get("file_id")
        cache_file = redis_client.hgetall(file_hash)

        if not cache_file:
            return "file is not uploaded correctly"

        file_name = cache_file[b"file_name"].decode("utf-8")
        file_bytes = base64.b64decode(cache_file[b"file_bytes"])

        # check for cache and return the cache file
        cache_file = redis_client.hget(file_hash, "converted_file")
        if cache_file:
            response = Response(cache_file, content_type="application/pdf")
            response.headers["Content-Disposition"] = (
                'attachment;filename="converted_file.pdf"'
            )
            return response

        file_id = uuid.uuid4()
        saved_file_result = Save_file(
            file_bytes, file_name, file_id
        )  # save the file to the server storage

        result = Ppt_To_Pdf(saved_file_result, file_id)  # PPT TO --> PDF

        cache_result = Save_Cache(result, file_hash)  # save file in cache

        return cache_result
    except Exception as e:
        return str(e)


def Save_file(file_bytes, file_name, id):
    try:
        fName, extension = os.path.splitext(file_name)
        if not file_bytes:
            return "pls check the function params named file_bytes"

        # create the file here
        file_name = str(id) + fName + extension
        file_path = os.path.join(os.environ.get("STORAGE_PATH"), file_name)
        print(file_path)

        # bytes conversion
        file_stream = io.BytesIO(file_bytes)
        file_data = file_stream.read()

        with open(file_path, "wb") as f:
            f.write(file_data)
        return file_path

    except Exception as e:
        return str(e)


def Save_Cache(file_name, file_hash):
    try:
        file_path = os.path.join(os.environ.get("STORAGE_PATH"), file_name)
        with open(file_path, "rb") as f:
            content = f.read()
        if not content:
            return "file not found"
        redis_client.hset(file_hash, "converted_file", content)

        # clean the storage file once complete the conversion
        list_dir = os.listdir(os.environ.get("STORAGE_PATH"))
        for dir in list_dir:
            rm_file = os.path.join(os.environ.get("STORAGE_PATH"), dir)
            try:
                if os.path.isfile(rm_file):
                    os.remove(rm_file)
            except Exception as e:
                print(str(e))
                return str(e)
        response = Response(content, content_type="application/pdf")
        response.headers["Content-Disposition"] = (
            'attachment;filename="converted_file.pdf"'
        )
        return response

    except Exception as e:
        return str(e)


@main_dp.route("/html_to_pdf", methods=["POST"])
def html_to_pdf():
    try:
        file_hash = request.cookies.get("file_id")
        if file_hash is None:
            return "uploaded file not found"

        # redis_cache
        file_data = redis_client.hgetall(file_hash)
        file_name = file_data[b"file_name"].decode("utf-8")
        file_bytes = base64.b64decode(file_data[b"file_bytes"]).decode("utf-8")

        # cache file (pdf file already present so here we will directly return it)
        converted_file = redis_client.hget(file_hash, "converted_file")
        if converted_file:
            response = Response(converted_file, content_type="application/pdf")
            response.headers["Content-Disposition"] = (
                'attachment;filename="converted_file.pdf"'
            )
            return response

        # start conversion
        try:
            result = html_converter(file_bytes)
        except Exception as e:
            return str(e)

        # cache
        redis_client.hset(file_hash, "converted_file", result)

        # create the response here
        response = Response(result, content_type="application/pdf")
        response.headers["Content-Disposition"] = (
            'attachment;filename="converted_file.pdf"'
        )
        return response
        # return result

    except Exception as e:
        return str(e)


def html_converter(file_bytes):
    try:

        file_path = os.path.join(os.environ.get("STORAGE_PATH"), "converted_file.pdf")

        # file_conversion
        HTML(string=str(file_bytes)).write_pdf(file_path)

        # read the binary of the pdf file which saved in directory
        with open(file_path, "rb") as file:
            file_binary = file.read()

        list_dir = os.listdir(os.environ.get("STORAGE_PATH"))
        for dir in list_dir:
            print(dir)
            rm_file = os.path.join(os.environ.get("STORAGE_PATH"), dir)
            try:
                if os.path.isfile(rm_file):
                    os.remove(rm_file)

            except Exception as e:
                return str(e)

        return file_binary

    except Exception as e:
        return str(e)


# decorate to check for cookies
def Cookies_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file_hash = request.cookies.get("file_id")

        if file_hash is None:
            return {"message": "Cookies not Found"}

        return func(file_hash, *args, **kwargs)

    return wrapper


def save_to_storage(file_binary):
    file_path = os.path.join(os.environ.get("STORAGE_PATH"), "Userfile.docx")
    try:
        with open(file_path, "wb") as file:
            file.write(file_binary)

        return file_path

    except Exception as e:
        return str(e)


@main_dp.route("/docx_to_pdf", methods=["POST"])
@Cookies_check
def docx_to_pdf(file_hash):
    try:
        file_data = redis_client.hgetall(file_hash)
        file_name = file_data[b"file_name"].decode("utf-8")
        file_binary = base64.b64decode(file_data[b"file_bytes"])

        cache_file=redis_client.hget(file_hash,"converted_file")
        # print(cache_file)

        if cache_file:
            response = Response(cache_file, content_type="application/pdf")
            response.headers["Content-Disposition"] = (
            'attachment;filename="converted_file.pdf"'
            )
            return response

            user_file = save_to_storage(file_binary)
            output_path = os.environ.get("STORAGE_PATH")
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    user_file,
                    "--outdir",
                    output_path,
                ],
                check=True,
            )

            file_path = os.path.join(os.environ.get("STORAGE_PATH"),"Userfile.pdf")

            result = Save_Cache(file_path,file_hash)

            return result

    except Exception as e:
        return str(e)

