// frontend/src/App.tsx
import React from "react";
import AppRouter from "./router/AppRouter";

const App: React.FC = () => {
  return (
    <React.StrictMode>
      <AppRouter />
    </React.StrictMode>
  );
};

export default App;
