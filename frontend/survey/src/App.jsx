import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SurveyList from "./pages/SurveyList";
import CreateSurvey from "./pages/CreateSurvey";
import EditSurvey from "./pages/EditSurvey";
import CSVSurveyUpload from "./pages/CSVSurveyUpload";
import TakeSurvey from "./pages/TakeSurvey";

import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SurveyList />} />
        <Route path="/surveys/create" element={<CreateSurvey />} />
        <Route path="/surveys/:id/edit" element={<EditSurvey />} />
        <Route path="/surveys/upload" element={<CSVSurveyUpload />} />
        <Route path="/surveys/:id/take" element={<TakeSurvey />} />
      </Routes>
    </Router>
  );
}

export default App
