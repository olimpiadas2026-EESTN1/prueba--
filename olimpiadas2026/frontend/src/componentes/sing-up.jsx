import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Outlet , Link} from "react-router-dom"
const SingUp = () => {
  const [mail, setMail] = useState("");
  const [password, setPassword] = useState("");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [dict, setDict] = useState(null);
  const navigate = useNavigate();
  
  // Manejo del formulario
  const handleLogin = (event) => {
    event.preventDefault();
    
    const diccionario = {
      nombre:nombre,
      apellido:apellido,
      contraseña: password,
      correo_electronico: mail,
    };
    
    setDict(diccionario);
    navigate("/login")
  };

  // Enviar datos cuando dict cambie
  useEffect(() => {
    fetch("https://backend-carrito-filb.vercel.app/clientes/ingresar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dict),
    })
      .then(async (res) => {
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Server error: ${res.status} ${errorText}`);
        }
        return res.json();
      })
      .then((res) => console.log("Cliente registrado"))
      .catch(console.error);
  }, [dict]);

  // El registro comparte la misma línea visual que el login para mantener
  // coherencia entre todas las pantallas de acceso. El objetivo es que la
  // autenticación no parezca una vista aislada sino parte del ecosistema visual.
  return (
    <div className="auth-shell auth-signup-shell">
      <div className="auth-visual">
        <div className="auth-visual-inner">
          <span className="auth-kicker">Creá tu cuenta</span>
          <h2>Guardá tus destinos favoritos y reservá con una sola cuenta.</h2>
          <p>Personalizá tu experiencia de viaje, guardá tus búsquedas y volá con más facilidad.</p>
          <div className="auth-stats">
            <div>
              <strong>+30</strong>
              <span>destinos</span>
            </div>
            <div>
              <strong>24/7</strong>
              <span>soporte</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login auth-card">
        <div className="auth-header">
          <span className="auth-badge">AirTrip Arg</span>
          <h1 className="cont-input-title">Crear cuenta</h1>
        </div>

        <form id="formularioIngresarCliente" onSubmit={handleLogin} className="auth-form">
          <label className="label">Nombre</label>
          <input required className="input" type="text" name="nombre" placeholder="Ingrese tu nombre" onChange={(event) => setNombre(event.target.value)} />

          <label className="label">Apellido</label>
          <input required className="input" type="text" name="apellido" placeholder="Ingrese tu apellido" onChange={(event) => setApellido(event.target.value)} />

          <label className="label">Correo electrónico</label>
          <input required className="input" type="email" name="correo_electronico" placeholder="Ingrese tu mail" onChange={(event) => setMail(event.target.value)} />

          <label className="label">Contraseña</label>
          <input required className="input" type="password" name="contraseña" placeholder="Ingrese su contraseña" onChange={(event) => setPassword(event.target.value)} />

          <p className="linkkk">¿Ya tenés una cuenta? <Link to={"/login"}>Ingresá ahora</Link></p>
          <button type="submit" className="auth-submit">Registrarme</button>
        </form>
      </div>
    </div>
  );
};

export default SingUp;
