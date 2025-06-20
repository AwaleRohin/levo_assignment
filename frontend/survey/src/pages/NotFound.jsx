import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
      <h1 className="text-4xl sm:text-5xl font-bold text-white-800">
        404 | Not Found
      </h1>
      <p className="mt-4 text-white-600 max-w-md m-6">
        Sorry, the page you're looking for doesn't exist or has been moved.
      </p>
      <button
        onClick={() => navigate("/")}
        className="mt-6 text-white-600 hover:underline text-base sm:text-lg"
      >
        Go back to Home
      </button>
    </div>
  );
}