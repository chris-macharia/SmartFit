/**
 * SmartFit React Application
 *
 * This is the root component of the SmartFit frontend.
 *
 * Responsibilities:
 *
 * - Configure React Router.
 * - Define the application's routes.
 * - Use MainLayout for pages that share the common
 *   SmartFit navigation and footer.
 * - Protect authenticated application pages.
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
import UploadVideo from "./pages/UploadVideo";
import Avatar from "./pages/Avatar";


import MainLayout from "./layouts/MainLayout";

import ProtectedRoute from "./components/ProtectedRoute";


function App() {
  return (
    /*
     * BrowserRouter provides client-side routing for
     * the SmartFit React application.
     */
    <BrowserRouter>

      <Routes>

        {/*
         * MainLayout wraps the pages that share the
         * SmartFit navigation and footer.
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


          {/*
           * Protected SmartFit application pages.
           *
           * ProtectedRoute checks whether the user
           * has a valid authenticated session before
           * rendering these routes.
           */}
          <Route element={<ProtectedRoute />}>

            {/* Authenticated user dashboard. */}
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />


            {/* Authenticated video upload page. */}
            <Route
              path="/upload-video"
              element={<UploadVideo />}
            />


            {/* Authenticated avatar page. */}
            <Route
              path="/avatar"
              element={<Avatar />}
            />

          </Route>

        </Route>

      </Routes>

    </BrowserRouter>
  );
}


export default App;