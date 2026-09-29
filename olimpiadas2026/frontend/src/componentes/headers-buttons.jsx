import { NavLink } from "react-router-dom";

export default function Header_buttons() {
  return <nav className="buttons" aria-label="Navegación principal">
    {[["/", "Inicio"], ["/paquetes", "Paquetes"], ["/vuelos", "Vuelos"], ["/micros", "Micros"]].map(([to, label]) =>
      <NavLink key={to} to={to} end className={({ isActive }) => `link${isActive ? " active" : ""}`}>{label}</NavLink>
    )}
  </nav>;
}
