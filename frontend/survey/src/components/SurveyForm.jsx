import { useState, useEffect } from "react";
import { Save, Trash2, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const defaultQuestion = () => ({
  id: `temp-${Date.now()}-${Math.random()}`,
  text: "",
  type: "text",
  required: false,
  options: [],
});

export default function SurveyForm({ onSubmit, initialData = {} }) {
  const navigate = useNavigate();
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const [form, setForm] = useState({
    title: initialData.title || "",
    description: initialData.description || "",
    questions: [defaultQuestion()],
  });
  const [scheduledTime, setScheduledTime] = useState("");

  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      setForm({
        title: initialData.title || "",
        description: initialData.description || "",
        questions: initialData.questions?.length
          ? initialData.questions
          : [defaultQuestion()],
      });
      setScheduledTime(initialData.scheduled_time || "")
    }
  }, [initialData]);


  const updateQuestion = (id, key, value) => {
    setForm(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === id ? { ...q, [key]: value } : q
      ),
    }));
  };

  const addQuestion = () => {
    setForm(prev => ({
      ...prev,
      questions: [...prev.questions, defaultQuestion()],
    }));
  };

  const removeQuestion = id => {
    setForm(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== id),
    }));
  };

  const addOption = qid => {
    setForm(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === qid ? { ...q, options: [...q.options, ""] } : q
      ),
    }));
  };

  const updateOption = (qid, index, value) => {
    setForm(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === qid
          ? {
            ...q,
            options: q.options.map((opt, i) => (i === index ? value : opt)),
          }
          : q
      ),
    }));
  };

  const handleSubmit = (data, message) => {
    onSubmit(data);
    toast.success(message);
  };

  return (
    <div className="w-[95%] sm:w-[540px] md:w-[640px] lg:w-[768px] xl:w-[1024px] mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white-900">
          {initialData.id ? "Edit Survey" : "Create New Survey"}
        </h2>
        <button
          onClick={() => navigate("/")}
          className="text-white-600 hover:text-gray-800"
        >
          <X size={24} />
        </button>
      </div>

      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg border">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Survey Title
              </label>
              <input
                type="text"
                value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })}
                className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })}
                className="w-full px-3 py-2 border text-gray-700 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              />
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Schedule Publish Time (optional)
          </label>
          <input
            type="datetime-local"
            value={scheduledTime}
            onChange={e => setScheduledTime(e.target.value)}
            className="w-full px-3 py-2 border text-gray-700 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>


        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Questions</h3>
            <button
              type="button"
              onClick={addQuestion}
              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
            >
              Add Question
            </button>
          </div>

          {form.questions.map((q, index) => (
            <div key={q.id} className="bg-white p-6 rounded-lg border">
              <div className="flex justify-between items-start mb-4">
                <h4 className="text-md font-medium text-gray-800">
                  Question {index + 1}
                </h4>
                {form.questions.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeQuestion(q.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Question Text
                  </label>
                  <input
                    type="text"
                    value={q.text}
                    onChange={e => updateQuestion(q.id, "text", e.target.value)}
                    className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Question Type
                  </label>
                  <select
                    value={q.type}
                    onChange={e => updateQuestion(q.id, "type", e.target.value)}
                    className="w-full px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="text">Text</option>
                    <option value="multiple-choice">Multiple Choice/Radio</option>
                    <option value="checkbox">Checkbox</option>
                  </select>
                </div>

                {(q.type === "multiple-choice" || q.type === "checkbox") && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Options
                    </label>
                    {q.options.map((opt, i) => (
                      <div key={i} className="flex gap-2 mb-2">
                        <input
                          type="text"
                          value={opt}
                          onChange={e => updateOption(q.id, i, e.target.value)}
                          className="flex-1 px-3 py-2 text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Option ${i + 1}`}
                        />
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => addOption(q.id)}
                      className="text-white-600 hover:text-blue-800 text-sm"
                    >
                      + Add Option
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() =>
              handleSubmit(
                {
                  ...form,
                  published: true,
                  scheduled_time: null,
                },
                initialData.id ? "Survey updated & published!" : "Survey created & published!"
              )
            }
            className="bg-blue-600 text-white px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
          >
            <Save size={20} />
            {initialData.id ? "Update & Publish" : "Create & Publish"}
          </button>

          <button
            type="button"
            onClick={() =>
              handleSubmit(
                {
                  ...form,
                  published: false,
                  scheduled_time: null,
                },
                initialData.id ? "Survey updated as draft!" : "Survey created as draft!"
              )
            }
            className="bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600"
          >
            {initialData.id ? "Update as Draft" : "Save as Draft"}

          </button>

          <button
            type="button"
            disabled={!scheduledTime}
            onClick={() =>
              handleSubmit(
                {
                  ...form,
                  published: false,
                  scheduled_time: scheduledTime,
                  timezone: timeZone
                },
                initialData.id ? "Survey updated & schduled for publish!" : "Survey created & schduled for publish!!"
              )
            }
            className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            Schedule Publish
          </button>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="hidden md:inline-block bg-gray-300 text-white-700 px-6 py-2 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
