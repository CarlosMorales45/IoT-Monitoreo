import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL;
console.log("API_URL:", API_URL);  // <-- Esto te muestra la URL real usada

export const login = (username, password) =>
  axios.post(`${API_URL}/login`, { username, password });

export const register = (username, password) =>
  axios.post(`${API_URL}/register`, { username, password });

export const listarDispositivos = (username) =>
  axios.get(`${API_URL}/devices`, { params: { username } });

export const registrarDispositivo = (data) =>
  axios.post(`${API_URL}/devices`, data);

export const eliminarDispositivo = (device_id, timestamp, username) =>
  axios.delete(`${API_URL}/devices/${device_id}`, { data: { timestamp, username } });
