import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

function App() {
  const [devices, setDevices] = useState([]);
  const [newDevice, setNewDevice] = useState({
    device_id: '',
    nombre: '',
    tipo: '',
    ubicacion: '',
    estado: 'activo'
  });
  const [mensaje, setMensaje] = useState('');
  const [cargando, setCargando] = useState(false);

  // Cargar dispositivos al iniciar
  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    setCargando(true);
    try {
      const res = await axios.get(`${API_URL}/devices`);
      setDevices(res.data);
    } catch (e) {
      setMensaje('Error cargando dispositivos');
    }
    setCargando(false);
  };

  const handleChange = e => {
    setNewDevice({ ...newDevice, [e.target.name]: e.target.value });
  };

  const handleRegistrar = async e => {
    e.preventDefault();
    setMensaje('');
    try {
      await axios.post(`${API_URL}/devices`, newDevice);
      setMensaje('Dispositivo registrado');
      setNewDevice({ device_id: '', nombre: '', tipo: '', ubicacion: '', estado: 'activo' });
      fetchDevices();
    } catch (e) {
      setMensaje('Error al registrar');
    }
  };

  const handleEliminar = async (device_id, timestamp) => {
    if (!window.confirm("¿Eliminar este dispositivo?")) return;
    try {
      await axios.delete(`${API_URL}/devices/${device_id}`, { data: { timestamp } });
      setMensaje('Dispositivo eliminado');
      fetchDevices();
    } catch {
      setMensaje('Error al eliminar');
    }
  };

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h2>Dashboard Monitoreo IoT</h2>
      {mensaje && <div style={{ color: 'green', marginBottom: 8 }}>{mensaje}</div>}

      <form onSubmit={handleRegistrar} style={{ marginBottom: 20, border: "1px solid #ccc", padding: 16 }}>
        <h3>Registrar dispositivo</h3>
        <input name="device_id" value={newDevice.device_id} onChange={handleChange} placeholder="ID único" required />
        <input name="nombre" value={newDevice.nombre} onChange={handleChange} placeholder="Nombre" required />
        <input name="tipo" value={newDevice.tipo} onChange={handleChange} placeholder="Tipo" required />
        <input name="ubicacion" value={newDevice.ubicacion} onChange={handleChange} placeholder="Ubicación" required />
        <select name="estado" value={newDevice.estado} onChange={handleChange}>
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

export default App;
