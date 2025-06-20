import { useEffect, useState } from "react";
import { useParams,useNavigate } from "react-router-dom";
import { getSurveyStatById } from "../api/index.js";
import { X } from "lucide-react";

export default function SurveyStats() {
	const { id } = useParams();
	const navigate = useNavigate();
	const [stats, setStats] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const loadSurveyStats = async () => {
			try {
				setLoading(true);
				const data = await getSurveyStatById(id);
				setStats(data);
			} catch (err) {
				console.error("Failed to load survey:", err);
			} finally {
				setLoading(false);
			}
		};

		loadSurveyStats();
	}, [id]);

	if (loading) return <p className="text-center mt-10">Loading...</p>;
	if (!stats) return <p className="text-center text-red-600 mt-10">Failed to load stats.</p>;

	return (
		<div className="w-[95%] sm:w-[540px] md:w-[640px] lg:w-[768px] xl:w-[1024px] mt-10 space-y-6 px-6">
			<div className="flex justify-between items-center mb-6">
				<h2 className="text-2xl font-bold text-white-800">
					Survey Stats: {stats.title}
				</h2>
				<button
					onClick={() => navigate("/surveys/overview")}
					className="text-white-600 hover:text-gray-800"
				>
					<X size={24} />
				</button>
			</div>
			<div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
				<StatCard title="Responses" value={stats.total_responses} />
				<StatCard title="Questions" value={stats.total_questions} />
				<StatCard
					title="Created"
					value={new Date(stats.created_at).toLocaleDateString()}
				/>
			</div>

			<div className="bg-white border p-6 rounded shadow text-gray-700">
				{stats.total_responses === 0 ? (
					<p className="text-center text-gray-500">No responses yet. Showing dummy preview below.</p>
				) : (
					<p className="text-center text-green-600 font-semibold">
						{stats.total_responses} response{stats.total_responses > 1 ? "s" : ""} collected.
					</p>
				)}
			</div>
		</div>
	);
}

function StatCard({ title, value }) {
	return (
		<div className="bg-white border p-4 rounded shadow text-center">
			<p className="text-sm text-gray-500">{title}</p>
			<p className="text-2xl font-bold text-gray-800">{value}</p>
		</div>
	);
}
