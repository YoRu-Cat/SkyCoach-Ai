import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ErrorBoundary from "@components/ErrorBoundary";
import "leaflet/dist/leaflet.css";

const rootEl = document.getElementById("root");
if (!rootEl) {
  document.body.innerHTML =
    '<div style="color:#f5f3ff;padding:2rem;font-family:sans-serif">' +
    "<h1>SkyCoach failed to start</h1>" +
    "<p>Could not find the React mount point. Try a hard refresh.</p>" +
    "</div>";
} else {
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  );
}
