import { useContext } from "react";
import { AuthContext } from "../AuthContext"; 
import { Outlet , Link} from "react-router-dom"
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
    </>
  );
};

export default Login_buttons;
