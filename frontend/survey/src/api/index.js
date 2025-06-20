import axios from "axios";

const apiUrl = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: apiUrl, // your Flask base URL
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;

export const getSurveyById = async (id) => {
  try {
    const response = await api.get(`/surveys/${id}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching survey:", error);
    throw error; // let the calling component catch this
  }
};


export const createSurvey = async (data) => {
  try {
    const response = await api.post("/surveys", data);
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};

export const updateSurvey = async (id, data) => {
  try {
    const response = await api.put(`/surveys/${id}`, data);
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};


export const uploadSurveyCSV = async (formData) => {
  try {
    const response = await axios.post(`${apiUrl}/surveys/upload`, formData, {
      headers: {
        "Content-Type": "multipart/form-data", // optional; axios handles this well even if omitted
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};


export const submitSurvey = async (id, data) => {
  try {
    const response = await api.post(`/surveys/${id}/submit`, data);
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};


export const getSurveyStats = async () => {
  try {
    const response = await api.get(`/surveys/stats`);
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};


export const getSurveyStatById = async (id) => {
  try {
    const response = await api.get(`/surveys/${id}/stats`);
    return response.data;
  } catch (error) {
    console.error("Error creating survey:", error);
    throw error; // let the calling component catch this
  }
};