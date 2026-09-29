import { API_URL, apiFetch } from "../api";
import { useState, useContext, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";


const Login = () => {
  const navigate = useNavigate();
  const { isLoggedIn, setIsLoggedIn } = useContext(AuthContext);
  const { mail_guardado,setMail_guardado} = useContext(AuthContext);
  const url = `${API_URL}/clientes/validarContrasena`;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isLoggedIn) navigate("/");
  }, [isLoggedIn, navigate]);

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const response = await apiFetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuarioIngresado: email.trim(), contraseñaIngresada: password }),
      });
      const valid = await response.json();
      if (valid !== true) throw new Error("Correo o contraseña incorrectos.");
      setMail_guardado(email.trim());
      localStorage.setItem("mail_guardado", JSON.stringify(email.trim()));
      localStorage.setItem("isLoggedIn", "true");
      setIsLoggedIn(true);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // La pantalla de login fue reimaginada como una vista premium de agencia.
  // Se separó la parte visual del formulario para crear un look más atractivo,
  // consistente con el resto del rediseño y la identidad visual de la marca.
  return (
    <div className="auth-shell auth-login-shell">
      <div className="auth-visual">
        <div className="auth-visual-inner">
          <span className="auth-kicker">Tu próximo destino</span>
          <h2>Viajá con claridad, sin atrasos ni complicaciones.</h2>
          <p>Compará opciones, encontrá la mejor salida y reservá tu escape ideal con total confianza.</p>
          <div className="auth-stats">
            <div>
              <strong>120K+</strong>
              <span>reservas</span>
            </div>
            <div>
              <strong>4.9/5</strong>
              <span>valoración</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login auth-card">
        <div className="auth-header">
          <span className="auth-badge">AirTrip Arg</span>
          <h1 className="cont-input-title">Iniciar sesión</h1>
        </div>

        <form onSubmit={handleLogin} className="auth-form">
          <label className="label">Correo electrónico</label>
          <input required type="email" name="correo_electronico" className="input" placeholder="Ingrese tu mail" onChange={(event) => setEmail(event.target.value)} />

          <label className="label">Contraseña</label>
          <input required type="password" name="contraseña" className="input" placeholder="Ingrese su contraseña" onChange={(event) => setPassword(event.target.value)} />

          <p className="linkkk">¿No tenés una cuenta? <Link to={"/sing-up"}>¡Regístrate!</Link></p>
          {error && <p role="alert">{error}</p>}
          <button type="submit" className="auth-submit" disabled={submitting}>{submitting ? "Ingresando…" : "Entrar"}</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
