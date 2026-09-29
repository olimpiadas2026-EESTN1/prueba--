import { useState } from "react";

const CustomAlert = () => {
  const [visible, setVisible] = useState(true);

  return (
    <>
      
    
      {visible && (
        <div style={styles.alert}>
          <p>Iniciaste sesión correctamente!</p>
          <button onClick={() => setVisible(false)} style={styles.closeButton}>
            Cerrar
          </button>
        </div>
      )}
    </>
  );
};

const styles = {
  alert: {
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    background: " rgb(58, 147, 255)",
    color: "white",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.3)",
    textAlign: "center",
  },
  button: {
    padding: "10px 20px",
    background: "rgb(58, 147, 255)",
    color: "white",
    border: "none",
    cursor: "pointer",
    borderRadius: "5px",
  },
  closeButton: {
    marginTop: "10px 30px",
    textAlign:"center",
    background: "white",
    color: " rgb(58, 147, 255)",
    border: "none",
   
    cursor: "pointer",
  },
};

export default CustomAlert;
