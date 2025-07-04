import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
	BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from "recharts";
import { X } from "lucide-react";

import { getSurveyStats } from "../api/index.js";

export default function AllSurveyStats() {
	const navigate = useNavigate();
	const [surveys, setSurveys] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const loadSurveyStats = async () => {
			try {
				setLoading(true);
				const data = await getSurveyStats();
				setSurveys(data);
			} catch (err) {
				console.error("Failed to load survey:", err);
			} finally {
				setLoading(false);
			}
		};

		loadSurveyStats();
	}, []);
	if (loading) {
		return <div>Loading...</div>;
	}
	return (
		<div className="w-[95%] sm:w-[540px] md:w-[640px] lg:w-[768px] xl:w-[1024px] mx-auto mt-10 px-6">
			<div className="flex justify-between items-center mb-6">
				<h2 className="text-2xl font-bold text-white-800 mb-6">Survey Response Overview</h2>
				<button
					onClick={() => navigate("/")}
					className="text-white-600 hover:text-gray-800"
				>
					<X size={24} />
				</button>

			</div>
			{surveys.length === 0 ? (
				<p>No survey data available.</p>
			) : (
				<div className="bg-white border rounded-lg p-4 shadow">
					<ResponsiveContainer width="100%" height={400}>
						<BarChart data={surveys}>
							<XAxis
								dataKey="title"
								angle={-30}
								textAnchor="end"
								interval={0} />
							<YAxis />
							<Tooltip />
							<Bar
								dataKey="total_responses"
								fill="#8884d8"
								cursor="pointer"
								onClick={(data, index) => {
									const surveyId = surveys[index].survey_id;
									navigate(`/surveys/${surveyId}/stats`);
								}}
							/>
						</BarChart>
					</ResponsiveContainer>
				</div>

			)}
		</div>
	);
}
