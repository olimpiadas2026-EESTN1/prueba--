import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";

export default function CategoryHeading({ title, description }) {
  const heading = useRef(null);
  useEffect(() => {
    document.title = `${title} | AirTrip Arg`;
    heading.current?.focus({ preventScroll: true });
    window.scrollTo(0, 0);
    return () => { document.title = "AirTrip Arg"; };
  }, [title]);
  return <header className="category-heading">
    <Link to="/">← Volver al inicio</Link>
    <h1 ref={heading} tabIndex={-1}>{title}</h1>
    <p>{description}</p>
  </header>;
}
