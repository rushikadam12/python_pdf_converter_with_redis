import React from "react";
import { BsFiletypePpt } from "react-icons/bs";
import { BsFiletypeXlsx } from "react-icons/bs";
import { BsFiletypeHtml } from "react-icons/bs";
import { BsFiletypeDocx } from "react-icons/bs";
import { MdArrowRightAlt } from "react-icons/md";
import ParticleComponent from "../components/ParticalComponent";
import { useNavigate } from "react-router-dom";
const Home: React.FC = () => {
  const navigate = useNavigate();
  return (
    <>
      <ParticleComponent id="tsparticles" />
      <div className="w-full h-screen flex justify-center items-center gap-5">
        {/*  */}
        <div
          className=" border-2 border-slate-200 w-[18%] h-[25%]  rounded-lg flex flex-col gap-2 
         bg-slate-800 bg-opacity-50 backdrop-blur-sm hover:bg-slate-700 transition 0.8s ease-linear"
        >
          <label className="block py-2 w-full self-start pl-2">
            <BsFiletypePpt size={40} color="#70C4DE" />
          </label>
          <span className="block pl-2 pt-2 font-bold">
            convert your PPTX files to PDF
          </span>
          <button
            className="outline-none border-none flex items-center justify-end self-end "
            onClick={() => {
              navigate(`/fileupload/${`.ppt, .pptx`}`);
            }}
          >
            <MdArrowRightAlt size={35} color="white" />
          </button>
        </div>
        {/*  */}
        <div className=" border-2 border-slate-200 w-[18%] h-[25%]  rounded-lg flex flex-col gap-2   bg-slate-800 bg-opacity-50 backdrop-blur-sm">
          <label className="block py-2 w-full  self-start pl-2">
            <BsFiletypeXlsx size={40} color="#AAFF00" className="" />
          </label>
          <span className="block pl-2 pt-2 font-bold">
            convert your xls or .xlsx files to PDF
          </span>
          <button
            className="outline-none border-none flex items-center justify-end self-end "
            onClick={() => {
              navigate(`/fileupload/${`.xlsx, .xls`}`);
            }}
          >
            <MdArrowRightAlt size={35} color="white" />
          </button>
        </div>
        <div className=" border-2 border-slate-200 w-[18%] h-[25%]  rounded-lg flex flex-col gap-2 bg-slate-800 bg-opacity-50 backdrop-blur-sm">
          <label className="block py-2 w-full  self-start pl-2">
            <BsFiletypeHtml size={40} color=" #FFA500" className="" />
          </label>
          <span className="block pl-2 pt-2 font-bold">
            convert your PPTX files to PDF
          </span>
          <button className="outline-none border-none flex items-center justify-end self-end ">
            <MdArrowRightAlt size={35} color="white" />
          </button>
        </div>
        <div className=" border-2 border-slate-200 w-[18%] h-[25%]  rounded-lg flex flex-col gap-2 bg-slate-800 bg-opacity-50 backdrop-blur-sm">
          <label className="block py-2 w-full  self-start pl-2">
            <BsFiletypeDocx size={40} color="#CB8AD1" className="" />
          </label>
          <span className="block pl-2 pt-2 font-bold">
            convert your PPTX files to PDF
          </span>
          <button className="outline-none border-none flex items-center justify-end self-end ">
            <MdArrowRightAlt size={35} color="white" />
          </button>
        </div>
      </div>
    </>
  );
};

export default Home;
