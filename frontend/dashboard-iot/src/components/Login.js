import React, { useState } from "react";
import { login } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mensaje, setMensaje] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    try {
      await login(username, password);
      setUser(username);
      localStorage.setItem("iot_username", username);
      navigate("/dashboard");
    } catch (e) {
      console.log("Error al logear:", e.response?.data || e.message);  // <-- Esto
      setMensaje("Credenciales inválidas");
    }
  };

  return (
    <div>
      <h2>Iniciar Sesión</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Usuario" value={username} onChange={e => setUsername(e.target.value)} required />
        <input placeholder="Contraseña" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Entrar</button>
      </form>
      <button onClick={() => navigate("/register")}>¿No tienes cuenta? Regístrate</button>
      {mensaje && <div style={{ color: "red", marginTop: 10 }}>{mensaje}</div>}
    </div>
  );
}
