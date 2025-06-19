import { useParams, useNavigate } from "react-router-dom";
import SurveyForm from "../components/SurveyForm";
import { useEffect, useState } from "react";
import { getSurveyById, updateSurvey } from "../api/index.js";

const EditSurvey = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [survey, setSurvey] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSurvey = async () => {
      if (!id) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const data = await getSurveyById(id);
        setSurvey(data);
      } catch (err) {
        console.error("Failed to load survey:", err);
      } finally {
        setLoading(false);
      }
    };

    loadSurvey();
  }, [id]);


  const handleUpdate = async (formData) => {
    await updateSurvey(id, formData);
    navigate("/");
  };
	  if (loading) {
    return <div>Loading...</div>;
  }

  if (!survey) {
    return <div>Survey not found</div>;
  }

  return <SurveyForm initialData={survey} onSubmit={handleUpdate} />
};

export default EditSurvey;