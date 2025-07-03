import React, { useState } from "react";
import { register } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mensaje, setMensaje] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    try {
      await register(username, password);
      setMensaje("Usuario registrado. Ahora puedes iniciar sesión.");
      setTimeout(() => navigate("/login"), 1200);
    } catch (e) {
      console.log("Error al registrar:", e.response?.data || e.message);  // <-- Esto
      setMensaje("Error: El usuario ya existe o hubo un problema.");
    }
  };

  return (
    <div>
      <h2>Registro</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Usuario" value={username} onChange={e => setUsername(e.target.value)} required />
        <input placeholder="Contraseña" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Registrarme</button>
      </form>
      <button onClick={() => navigate("/login")}>Volver a login</button>
      {mensaje && <div style={{ color: "green", marginTop: 10 }}>{mensaje}</div>}
    </div>
  );
}
