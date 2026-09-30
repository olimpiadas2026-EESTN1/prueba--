import { useContext } from "react";
import { AuthContext } from "../AuthContext"; 
import { Link} from "react-router-dom"
const Login_buttons = () => {
  const { isLoggedIn } = useContext(AuthContext); 

  return (
    <>
      {!isLoggedIn && ( // Mostrar solo si el usuario NO ha iniciado sesión
        <div className="buttons-login">
          <Link className="link" to={"/login"}>Logeate</Link>
          <Link className="link" to={"/sing-up"}>Regístrate</Link>
        </div>
      )}
      <Link className="admin-entry admin-entry-header" to="/admin">Entrar como administrador</Link>
    </>
  );
};

export default Login_buttons;
