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
      setMensaje("Usuario creado. Ahora puedes iniciar sesión.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (e) {
      setMensaje("Error: el usuario ya existe.");
    }
  };

  return (
    <div className="register-container">
      <h2>Registro</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Usuario" value={username} onChange={e => setUsername(e.target.value)} required />
        <input placeholder="Contraseña" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Registrarse</button>
      </form>
      <button onClick={() => navigate("/login")}>Volver al Login</button>
      {mensaje && <div style={{ color: "green", marginTop: 10 }}>{mensaje}</div>}
    </div>
  );
}
