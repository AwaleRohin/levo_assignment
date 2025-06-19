import SurveyForm from "../components/SurveyForm";
import { useNavigate } from "react-router-dom";
import { createSurvey } from "../api/index.js"; 

const CreateSurvey = () => {
  const navigate = useNavigate();

  const handleCreate = async (formData) => {
    await createSurvey(formData);
    navigate("/");
  };

  return <SurveyForm onSubmit={handleCreate} />;
};

export default CreateSurvey;