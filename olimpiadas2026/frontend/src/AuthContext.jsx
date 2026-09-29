// AuthContext.js
import { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [data, setData] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [listaCarrito, setListaCarrito] = useState(() => {
    const guardado = localStorage.getItem("carrito");
    return guardado ? JSON.parse(guardado) : [];
  });
  const [mail_guardado,setMail_guardado]= useState(()=>{
    const mail = localStorage.getItem("mail_guardado");
  
    return mail ? JSON.parse(mail):null;
  })
    const[ autos,setAutos]=useState([]);
    const[ datos,setDatos]=useState([]);
    const[dataPaquetes,setDataPaquetes]=useState([])
    const[ excursiones,setExcursiones]= useState([])
    const [eleccionMoneda, setEleccionMoneda] =useState("ARS")
        const[ precio,setPrecio]= useState(0)
    localStorage.getItem("mail_guardado");
  return (
    <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn, listaCarrito, setListaCarrito,mail_guardado,setMail_guardado,data, setData, autos,setAutos,excursiones,setExcursiones,dataPaquetes,setDataPaquetes,datos,setDatos,eleccionMoneda, setEleccionMoneda,precio,setPrecio }}>
      {children}
    </AuthContext.Provider>
  );
};