import { useState } from "react";
import { Share2, X } from 'lucide-react';
import api from "../api";

export default function ShareSurveyDialog({ isOpen, onClose, surveyId }) {
  const [email, setEmail] = useState("");
  const [shareLoading, setShareLoading] = useState(false);
  const [shareSuccess, setShareSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleClose = () => {
    setEmail("");
    setShareSuccess(false);
    onClose();
  };
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  const onEmailChange = (e) => {
    setEmail(e.target.value);
    setError("");
  };

  const shareSurvey = async () => {
    if (!email.trim()) {
      alert("Please enter at least one email address.");
      return;
    }
    if (!validateEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setShareLoading(true);
    try {
      await api.post(`/surveys/${surveyId}/share`, {
        emails: email,
        survey_link: `${window.location.href}surveys/${surveyId}/take`
      });
      setShareSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 2000);
    } catch (err) {
        console.log(err)
      alert("Failed to share survey. Please try again.");
    } finally {
      setShareLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-auto max-h-[90vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Share Survey</h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {shareSuccess ? (
          <div className="text-center py-4">
            <div className="text-green-600 text-lg font-medium mb-2">
              Survey shared successfully!
            </div>
            <p className="text-gray-600">
              Invitation has been sent to the specified email address.
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <label
                htmlFor="email-input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Email Address
              </label>
              <input
                id="email-input"
                type="email"
                value={email}
                onChange={onEmailChange}
                placeholder="Enter email address"
                className={`w-full p-3 text-gray-700 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  error ? "border-red-500" : "border-gray-300"
                }`}
                disabled={shareLoading}
                aria-invalid={!!error}
                aria-describedby={error ? "email-error" : undefined}
              />
              {error && (
                <p
                  id="email-error"
                  className="mt-1 text-sm text-red-600"
                  role="alert"
                >
                  {error}
                </p>
              )}
            </div>

            <div className="flex gap-3 justify-end flex-wrap">
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
                disabled={shareLoading}
              >
                Cancel
              </button>
              <button
                onClick={shareSurvey}
                disabled={shareLoading || !validateEmail(email)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                {shareLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Sharing...
                  </>
                ) : (
                  <>
                    <Share2 size={16} />
                    Share Survey
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}