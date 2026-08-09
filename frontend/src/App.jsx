/**
 * SmartFit Application Router
 *
 * This component defines the application's client-side
 * navigation structure using React Router.
 *
 * The MainLayout is used as the shared parent layout,
 * allowing the Navbar and Footer to remain visible while
 * the page content changes.
 */

import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import MainLayout from "./layouts/MainLayout";


function App() {
  return (
    /*
      BrowserRouter enables client-side routing for the
      React application.

      This allows users to navigate between pages without
      causing a full browser refresh.
    */
    <BrowserRouter>

      <Routes>

        {/*
          MainLayout acts as the shared parent for the
          application's primary routes.

          Any route nested inside this component will
          automatically receive the Navbar and Footer.
        */}
        <Route element={<MainLayout />}>

          {/* SmartFit landing page. */}
          <Route
            path="/"
            element={<Home />}
          />

          {/* User login page. */}
          <Route
            path="/login"
            element={<Login />}
          />

          {/* User registration page. */}
          <Route
            path="/register"
            element={<Register />}
          />

          {/* User dashboard. */}
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

        </Route>

      </Routes>

    </BrowserRouter>
  );
}


export default App;