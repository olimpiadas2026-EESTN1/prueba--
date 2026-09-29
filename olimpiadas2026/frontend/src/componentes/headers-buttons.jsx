import { Outlet , Link} from "react-router-dom"
const Header_buttons = ()=>{
      return <div className="buttons">
        <Link className="link" to={"/"}>Home</Link>   
        <Link className="link" to={"/paquetes"}>Paquetes</Link>   
        <Link className="link" to={"/vuelos"}>Vuelos</Link>   
        <Link className="link" to={"/micros"}>Micros</Link>   
        </div>
}
export default Header_buttons
