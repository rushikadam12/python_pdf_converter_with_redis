from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    Response,
    make_response,
    send_file,
)
from fpdf import FPDF
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
import zipfile

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
    print(file_bytes)
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

    # check if the file exist in redis
    if redis_client.exists(file_hash):
        hash_values = redis_client.hgetall(file_hash)
        # print(hash_values)
        file_name = hash_values[b"file_name"].decode("utf-8")
        file_bytes = base64.b64encode(hash_values[b"file_bytes"]).decode("utf-8")
        response = make_response(
            {"file_name": file_name, "file_bytes": file_bytes, "message": "cache file"}
        )

        # response.set_cookie("file_id", file_hash, httponly=True, secure=True)
        return response

    file_bytes = User_file.read()  # convert into bytes
    cache_key = cache_file(file_hash, User_file.filename, file_bytes)
    print(cache_key)
    response = make_response({"message": "file new file found"})
    response.set_cookie("file_id", file_hash, httponly=True, secure=True)
    return response


# @main_dp.route("/convert")
# def file_convert():
#     if "id" in session:
#         session_id = session.get("id")
#     print(session_id)
#     file_list = os.listdir("/home/rk/python_pdf_project/app/storage")
#     for file in file_list:
#         if session_id in file:
#             return f"{file}"

#     return ""


@main_dp.route("/convert_xlsx_to_pdf")
def convert_xlsx():
    try:

        file_hash = request.cookies.get("file_id")
        session_id = session.get("userId")
        if file_hash is None:
            return jsonify({"message": "file not found pls check the file"})

        file_data = redis_client.hgetall(file_hash)
        file_name = file_data[b"file_name"].decode("utf-8")
        file_extension = file_name.split(".")
        file_bytes = base64.b64decode(file_data[b"file_bytes"])
        file_like = io.BytesIO(file_bytes)

        # df = pd.read_excel(read_file, engine="openpyxl")
        # print(df)
        # return {"file_name": file_name, "file_bytes": str(file_bytes)}
        # if file_bytes is not None:
        #     return send_file(
        #         file_like,
        #         mimetype="application/pdf",
        #         as_attachment=True,
        #         download_name=f"{file_hash}.pdf",
        #     )

        # return " hey"

        # for old file format '.xls'

        if "xls" == file_extension[1]:
            df = pd.read_excel(
                file_bytes,
                engine="xlrd",
            )
        # for new file format 'xlsx'

        elif "xlsx" == file_extension[1]:
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
        #################################################################
        file_split_name = file_name.split(".")

        # output_pdf_file = os.path.join(file_name[0], f"{session_id}.pdf")

        # save the pdf buffer to memory
        pdf_Buffer = io.BytesIO()
        pdf.output(pdf_Buffer)
        pdf_Buffer.seek(0)  # go to the start of the buffer to read

        pdf_bytes = pdf_Buffer.read()
        if not pdf_bytes:
            return "not able to read pdf bytes"

        # base64_pdf_encoding=base64.b64encode(pdf_bytes).decode("utf-8")
        print("file os converted ")

        redis_client.hset(file_hash, "converted_file", pdf_bytes)

        # cache values
        hash_values = redis_client.hget(file_hash,'converted_file')
        if hash_values:

            # decoded_file = io.BytesIO(hash_values)
            # decoded_file.seek(0)
            # decoded_read_value = decoded_file.read()
            # print(decoded_read_value)

            # with open("debug_file.pdf","wb") as f1 ,open("debug_retrieved.pdf","wb") as f2:
            #     f1.write(pdf_bytes)
            #     f2.write(decoded_file)

            # file_like = io.BytesIO(decoded_file)
            # file_like.seek(0)
            response = Response(hash_values, content_type="application/pdf")
            response.headers["Content-Disposition"] = (
                'attachment;filename="converted_file.pdf"'
            )
            return response
        else:
            return "something went wrong"
        # return send_file(
        #     response_file,
        #     mimetype="application/pdf",
        #     as_attachment=True,
        #     download_name=f"{file_split_name[0]}.pdf",
        # )

    except Exception as e:
        return str(e)
