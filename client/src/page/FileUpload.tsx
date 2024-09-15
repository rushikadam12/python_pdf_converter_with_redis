import React, { useEffect, useState } from "react";
import { RiUploadCloud2Line } from "react-icons/ri";
import { useParams } from "react-router-dom";
import axios from "axios";
const FileUpload: React.FC = () => {
  const { id } = useParams();
  const [UploadFile, setUploadFile] = useState<any>([]);
  const [isLoading, setIsLoading] = useState<Boolean>(false);

  useEffect(() => {
    if (UploadFile.length > 0) {
      setIsLoading(true);
      const file = UploadFile[0];
      const Upload = async () => {
        try {
          const formData = new FormData();
          formData.append("file", file);

          const resp = await axios.post(
            "http://127.0.0.1:5000/fileupload",
            formData,
            {
              
              withCredentials: true,
            }
          );
          console.log(resp.data);
        } catch (error) {
          console.error(error);
          setUploadFile([]);
        } finally {
          setIsLoading(false);
        }
      };
      Upload();
    }
  }, [UploadFile]);
  return (
    <>
      {isLoading && <h1>Loading...</h1>}
      <div className="w-full h-screen flex justify-center items-center flex-col">
        <label className="font-semibold text-[2.5rem] p-5">
          Upload the file for conversion
        </label>
        <input
          type="file"
          id="uploadfile"
          hidden
          accept={id}
          onChange={(e) => {
            setUploadFile(e.target.files);
          }}
        />
        <label
          htmlFor="uploadfile"
          className="w-[30%] h-[25%] border-2 flex items-center justify-center rounded-lg flex-col bg-slate-800 bg-opacity-50 backdrop-blur-md"
        >
          <RiUploadCloud2Line size={100} />
          <span className="block font-medium ">Click to select the file</span>
        </label>
      </div>
    </>
  );
};

export default FileUpload;
