import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SurveyList from "./pages/SurveyList";
import CreateSurvey from "./pages/CreateSurvey";
import EditSurvey from "./pages/EditSurvey";
import CSVSurveyUpload from "./pages/CSVSurveyUpload";
import TakeSurvey from "./pages/TakeSurvey";
import AllSurveyStats from "./pages/AllSurveyStats";
import SurveyStats from "./pages/SurveyStats";
import NotFound from "./pages/NotFound";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import './App.css'

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<SurveyList />} />
          <Route path="/surveys/create" element={<CreateSurvey />} />
          <Route path="/surveys/:id/edit" element={<EditSurvey />} />
          <Route path="/surveys/upload" element={<CSVSurveyUpload />} />
          <Route path="/surveys/:id/take" element={<TakeSurvey />} />
          <Route path="/surveys/overview" element={<AllSurveyStats />} />
          <Route path="/surveys/:id/stats" element={<SurveyStats />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
      <ToastContainer
        position="top-right"
        autoClose={3000}       // toast disappears after 3 seconds
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </>
  );
}

export default App
