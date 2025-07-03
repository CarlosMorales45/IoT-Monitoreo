import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL;

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Funciones útiles
export const login = (username, password) =>
  api.post("/login", { username, password });

export const register = (username, password) =>
  api.post("/register", { username, password });

export const getDevices = (username) =>
  api.get(`/devices?username=${username}`);

export const addDevice = (device) =>
  api.post("/devices", device);

export const updateDevice = (device_id, payload) =>
  api.put(`/devices/${device_id}`, payload);

export const deleteDevice = (device_id, payload) =>
  api.delete(`/devices/${device_id}`, { data: payload });
