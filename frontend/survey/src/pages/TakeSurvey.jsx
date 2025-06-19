import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { getSurveyById, submitSurvey } from "../api/index.js";
import { useNavigate } from "react-router-dom";

export default function TakeSurvey() {
	const { id } = useParams();
	const navigate = useNavigate();

	const [survey, setSurvey] = useState(null);
	const [responses, setResponses] = useState([]);
	const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
	const [chat, setChat] = useState([]);
	const [inputValue, setInputValue] = useState("");
	const [loading, setLoading] = useState(true);
	const [completed, setCompleted] = useState(false);
	const [typing, setTyping] = useState(false);
	const scrollRef = useRef(null);

	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [chat, typing]);

	useEffect(() => {
		const loadSurvey = async () => {
			if (!id) return setLoading(false);
			try {
				setLoading(true);
				const data = await getSurveyById(id);
				setSurvey(data);
				setChat([{ sender: "bot", text: `👋 ${data.questions[0].text}` }]);
			} catch (err) {
				console.error("Failed to load survey:", err);
			} finally {
				setLoading(false);
			}
		};
		loadSurvey();
	}, [id]);

	const handleAnswer = async (answer) => {
		const currentQ = survey.questions[currentQuestionIndex];
		const updatedResponses = [...responses, { question: currentQ.text, answer }];
		setResponses(updatedResponses);

		const newChat = [
			...chat,
			{ sender: "user", text: Array.isArray(answer) ? answer.join(", ") : answer },
		];

		const nextIndex = currentQuestionIndex + 1;

		if (nextIndex < survey.questions.length) {
			setTyping(true);
			setChat(newChat);
			setTimeout(() => {
				setCurrentQuestionIndex(nextIndex);
				newChat.push({
					sender: "bot",
					text: `🗨️ ${survey.questions[nextIndex].text}`,
				});
				setChat([...newChat]);
				setTyping(false);
			}, 500);
		} else {
			try {
				await submitSurvey(id, { survey_id: id, answers: updatedResponses });
				newChat.push({
					sender: "bot",
					text: "🎉 Thank you! Your response has been submitted!",
				});
			} catch (err) {
				newChat.push({
					sender: "bot",
					text: "Oops! Submission failed. Please try again.",
				});
				console.log(err)
			}
			setChat(newChat);
			setCompleted(true);
		}
		setInputValue("");
	};

	const handleCheckboxChange = (option) => {
		const currentQ = survey.questions[currentQuestionIndex];
		const existing = responses.find((r) => r.question === currentQ.text)?.answer || [];
		let updated = existing.includes(option)
			? existing.filter((o) => o !== option)
			: [...existing, option];
		const otherResponses = responses.filter((r) => r.question !== currentQ.text);
		setResponses([...otherResponses, { question: currentQ.text, answer: updated }]);
	};

	const submitCheckboxAnswer = () => {
		const currentQ = survey.questions[currentQuestionIndex];
		const answer = responses.find((r) => r.question === currentQ.text)?.answer || [];
		if (answer.length > 0) handleAnswer(answer);
	};

	if (loading)
		return (
			<div className="text-center text-lg text-gray-600 mt-10">Loading survey...</div>
		);

	if (!survey)
		return (
			<div className="text-center text-red-600 text-lg mt-10">Survey not found</div>
		);

	if (!survey.published)
		return (
			<div className="text-center text-yellow-400 text-lg mt-10">Survey is not published yet.</div>
		);

	const currentQ = survey.questions[currentQuestionIndex];

	return (
		<>
			<div className="mb-4">
				<button
					onClick={() => navigate("/")}
					className="text-white-600 hover:text-gray-800 flex items-center gap-1"
				>
					Back to Home
				</button>
			</div>
			<div className="max-w-4xl min-w-xl mx-auto mt-10 p-6 bg-gradient-to-br from-blue-50 to-purple-100 rounded-xl shadow-xl h-[600px] flex flex-col">
				<h2 className="text-2xl font-bold text-purple-800 mb-4">{survey.title}</h2>

				<div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 mb-4 px-2">
					{chat.map((msg, idx) => (
						<div
							key={idx}
							className={`flex ${msg.sender === "bot" ? "justify-start" : "justify-end"
								}`}
						>
							<div
								className={`max-w-[85%] px-4 py-2 rounded-2xl transition ${msg.sender === "bot"
									? "bg-purple-100 text-purple-800"
									: "bg-blue-400 text-white"
									}`}
							>
								{msg.text}
							</div>
						</div>
					))}
					{typing && (
						<div className="text-sm text-gray-400 ml-2 animate-pulse">Bot is typing...</div>
					)}
				</div>

				{!completed && (
					<div className="pt-2 border-t mt-4">
						{currentQ?.type === "text" && (
							<div className="flex gap-2">
								<input
									type="text"
									value={inputValue}
									onChange={(e) => setInputValue(e.target.value)}
									onKeyDown={(e) => e.key === "Enter" && handleAnswer(inputValue)}
									className="flex-1 px-4 py-2 text-gray-700 ounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-400"
									placeholder="Type your answer..."
								/>
								<button
									onClick={() => handleAnswer(inputValue)}
									className="bg-purple-600 text-white px-4 py-2 rounded-full hover:bg-purple-700 transition"
								>
									Send
								</button>
							</div>
						)}

						{currentQ?.type === "multiple-choice" && (
							<div className="grid grid-cols-1 gap-2 mt-2">
								{currentQ.options.map((opt) => (
									<button
										key={opt}
										onClick={() => handleAnswer(opt)}
										className="bg-white border-2 border-purple-400 hover:bg-purple-100 text-purple-900 px-4 py-2 rounded-full text-left"
									>
										{opt}
									</button>
								))}
							</div>
						)}

						{currentQ?.type === "checkbox" && (
							<div className="mt-2">
								{currentQ.options.map((opt) => (
									<label key={opt} className="flex items-center gap-2 mb-2">
										<input
											type="checkbox"
											checked={
												responses.find((r) => r.question === currentQ.text)?.answer?.includes(opt) ||
												false
											}
											onChange={() => handleCheckboxChange(opt)}
											className="form-checkbox h-4 w-4 text-purple-600"
										/>
										<span className="text-purple-800">{opt}</span>
									</label>
								))}
								<button
									onClick={submitCheckboxAnswer}
									className="mt-3 bg-purple-600 text-white px-4 py-2 rounded-full hover:bg-purple-700"
								>
									Next ➡️
								</button>
							</div>
						)}
					</div>
				)}

				{completed && (

					<div className="text-center mt-6">
						<div className="text-center text-green-600 font-semibold text-lg mb-4">
							All done! We appreciate your feedback!
						</div>
						<button
							onClick={() => window.location.reload()}
							className="bg-purple-600 text-white px-5 py-2 rounded-full hover:bg-purple-700 transition"
						>
							Take Another One
						</button>
					</div>
				)}
			</div>
		</>
	);
}
