import React, { useState, useEffect, useCallback } from "react";
import { listarDispositivos, registrarDispositivo, eliminarDispositivo } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Dashboard({ user, setUser }) {
  const [devices, setDevices] = useState([]);
  const [nuevo, setNuevo] = useState({
    device_id: "",
    nombre: "",
    tipo: "",
    ubicacion: "",
    estado: "activo"
  });
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const navigate = useNavigate();

  // Función para cargar dispositivos (memoizada con useCallback)
  const cargarDispositivos = useCallback(async () => {
    setCargando(true);
    try {
      const res = await listarDispositivos(user);
      setDevices(res.data);
    } catch {
      setMensaje("Error al cargar dispositivos");
    }
    setCargando(false);
  }, [user]);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    cargarDispositivos();
  }, [user, cargarDispositivos, navigate]);

  const handleChange = e => {
    setNuevo({ ...nuevo, [e.target.name]: e.target.value });
  };

  const handleRegistrar = async e => {
    e.preventDefault();
    setMensaje("");
    try {
      await registrarDispositivo({ ...nuevo, username: user });
      setMensaje("Dispositivo registrado");
      setNuevo({ device_id: "", nombre: "", tipo: "", ubicacion: "", estado: "activo" });
      cargarDispositivos();
    } catch {
      setMensaje("Error al registrar");
    }
  };

  const handleEliminar = async (device_id, timestamp) => {
    if (!window.confirm("¿Eliminar este dispositivo?")) return;
    try {
      await eliminarDispositivo(device_id, timestamp, user);
      setMensaje("Dispositivo eliminado");
      cargarDispositivos();
    } catch {
      setMensaje("Error al eliminar");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("iot_username");
    setUser(null);
    navigate("/login");
  };

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h2>Dashboard Monitoreo IoT</h2>
      <button onClick={handleLogout} style={{ float: "right" }}>Cerrar sesión</button>
      {mensaje && <div style={{ color: 'green', marginBottom: 8 }}>{mensaje}</div>}

      <form onSubmit={handleRegistrar} style={{ marginBottom: 20, border: "1px solid #ccc", padding: 16 }}>
        <h3>Registrar dispositivo</h3>
        <input name="device_id" value={nuevo.device_id} onChange={handleChange} placeholder="ID único" required />
        <input name="nombre" value={nuevo.nombre} onChange={handleChange} placeholder="Nombre" required />
        <input name="tipo" value={nuevo.tipo} onChange={handleChange} placeholder="Tipo" required />
        <input name="ubicacion" value={nuevo.ubicacion} onChange={handleChange} placeholder="Ubicación" required />
        <select name="estado" value={nuevo.estado} onChange={handleChange}>
          <option value="activo">Activo</option>
          <option value="error">Error</option>
        </select>
        <button type="submit">Registrar</button>
      </form>

      <h3>Dispositivos registrados</h3>
      {cargando ? (
        <div>Cargando...</div>
      ) : (
        <table border={1} cellPadding={8} cellSpacing={0} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th><th>Nombre</th><th>Tipo</th><th>Ubicación</th><th>Estado</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {devices.map(d => (
              <tr key={d.device_id + d.timestamp}>
                <td>{d.device_id}</td>
                <td>{d.nombre}</td>
                <td>{d.tipo}</td>
                <td>{d.ubicacion}</td>
                <td style={{ color: d.estado === "error" ? "red" : "green" }}>{d.estado}</td>
                <td>
                  <button onClick={() => handleEliminar(d.device_id, d.timestamp)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
