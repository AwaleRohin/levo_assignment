import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, ChevronDown, FileText, Edit3 } from "lucide-react";

export default function SurveyDropDownOption() {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setOpen(!open)}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
      >
        <Plus size={20} />
        Create Survey
        <ChevronDown size={18} />
      </button>

      {open && (
        <div className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg border border-gray-200">
          <div className="py-1">
            <Link
              to="/surveys/upload"
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setOpen(false)}
            >
              <FileText size={16} className="mr-2" />
              Upload CSV
            </Link>
            <Link
              to="/surveys/create"
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={() => setOpen(false)}
            >
              <Edit3 size={16} className="mr-2" />
              Add Questions Manually
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
