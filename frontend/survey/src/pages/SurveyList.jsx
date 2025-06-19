import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { Plus, Edit, Trash2, ListCheck, BarChart3, Share2 } from 'lucide-react';

export default function SurveyList() {
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSurveys = async () => {
    try {
      const res = await api.get("/surveys");
      setSurveys(res.data);
    } catch (err) {
      setError("Failed to load surveys.");
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteSurvey = async (id) => {
    if (!window.confirm("Are you sure you want to delete this survey?")) return;
    try {
      await api.delete(`/surveys/${id}`);
      setSurveys(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      setError("Failed to delete survey.");
      console.log(err);
    }
  };

  useEffect(() => {
    fetchSurveys();
  }, []);

  return (
    <div className="max-w-4xl min-w-2xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white-900">Surveys</h1>
        <Link
          to="/surveys/create"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus size={20} />
          Create Survey
        </Link>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">Loading surveys...</div>
      ) : (
        <div className="grid gap-4">
          {surveys.map(survey => (
            <div key={survey.id} className="bg-white border rounded-lg p-6 shadow-sm">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900">{survey.title}</h3>
                  <p className="text-gray-600 mt-1">{survey.description}</p>
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                    <span>{survey.questions?.length || 0} questions</span>
                    <span>Created: {new Date(survey.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/surveys/${survey.id}/edit`}
                    className="p-2 text-gray-600 hover:text-green-600"
                    title="Edit Survey"
                  >
                    <Edit size={18} />
                  </Link>
                  <button
                    onClick={() => deleteSurvey(survey.id)}
                    className="p-2 text-white-600 hover:text-red-600"
                    title="Delete Survey"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}