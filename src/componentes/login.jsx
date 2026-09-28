import "./Login.css";

function Login() {
  return (
    <div className="login-page">

      <div className="background"></div>

      <div className="login-card">

        <div className="logo">
          ✈
        </div>

        <h2>Bienvenido de nuevo</h2>

        <p className="subtitle">
          Ingresá para continuar tu viaje
        </p>

        <input
          type="email"
          placeholder="Correo electrónico"
        />

        <input
          type="password"
          placeholder="Contraseña"
        />

        <div className="actions">
          <button>Ingresar</button>

          <a href="#">
            ¿Olvidaste tu contraseña?
          </a>
        </div>

        <p className="register">
          ¿No tenés una cuenta?
          <a href="#"> Registrate</a>
        </p>

      </div>

      <div className="content">

        <div className="menu">
          <button className="active">Ingresar</button>
          <button>Registrarse</button>
        </div>

        <div className="text">

          <p>DESCUBRÍ EL MUNDO</p>

          <h1>
            Tu próximo viaje
            <br />
            comienza acá
          </h1>

          <div className="offer">
            <span>✈</span>

            <div>
              <strong>Paquetes turísticos</strong>
              <small>
                Vuelos + hoteles + experiencias
              </small>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Login;