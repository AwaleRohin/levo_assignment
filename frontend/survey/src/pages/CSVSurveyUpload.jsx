import { useState, useRef } from "react";
import { Upload, FileText, X } from "lucide-react";
import { uploadSurveyCSV } from "../api/index.js";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function CSVSurveyUpload() {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [csvFile, setCsvFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef();
    const navigate = useNavigate();

    const handleFile = (file) => {
        console.log(file)
        if (file && file.type === "text/csv") {
            setCsvFile(file);
        } else {
            alert("Only CSV files are allowed.");
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title || !csvFile) {
            alert("Please complete all fields and upload a CSV.");
            return;
        }

        const formData = new FormData();
        formData.append("title", title);
        formData.append("description", description);
        formData.append("csv", csvFile);
        for (let [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }

        try {
            await uploadSurveyCSV(formData);
            toast.success("Survey uploaded successfully!");
            navigate("/");
        } catch (err) {
            console.error("Upload failed", err);
            toast.error("Failed to upload survey.");
        }
    };

    return (
        <div className="w-[95%] sm:w-[540px] md:w-[640px] lg:w-[768px] xl:w-[1024px]  mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white-900">
                    Create New Survey
                </h2>
                <button
                    onClick={() => navigate("/")}
                    className="text-white-600 hover:text-gray-800"
                >
                    <X size={24} />
                </button>
            </div>
            <form
                onSubmit={handleSubmit}
                className="space-y-8 bg-white p-8 rounded-xl shadow-md border border-gray-200"
                onDragEnter={handleDrag}
                onSubmitCapture={(e) => e.preventDefault()}
            >
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Survey Title</label>
                    <input
                        type="text"
                        className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                        className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={3}
                    />
                </div>

                {/* Drag-and-drop CSV upload */}
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDrag}
                    onDragLeave={handleDrag}
                    className={`border-2 border-dashed rounded-lg p-10 text-center transition-all ${dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
                        }`}
                >
                    <div className="flex justify-center mb-4">
                        <div className="bg-gray-100 p-3 rounded-full">
                            <Upload className="w-6 h-6 text-gray-500" />
                        </div>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-800 mb-1">Upload CSV File</h3>
                    <p className="text-sm text-gray-500 mb-4">Drag and drop or choose a file below</p>

                    <label
                        htmlFor="csv"
                        className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700 transition"
                    >
                        <FileText className="w-4 h-4" />
                        Choose CSV File
                    </label>

                    <input
                        ref={fileInputRef}
                        id="csv"
                        type="file"
                        accept=".csv"
                        className="hidden"
                        onChange={(e) => handleFile(e.target.files[0])}
                    />

                    {csvFile && (
                        <div className="mt-3 text-sm text-gray-700">{csvFile.name}</div>
                    )}
                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition"
                    >
                        Upload Survey
                    </button>
                </div>
            </form>
        </div>
    );
}
