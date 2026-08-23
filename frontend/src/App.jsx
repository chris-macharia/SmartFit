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
 * - Provide access to retailer-specific garment
 *   management functionality.
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
import GenerateAvatar from "./pages/GenerateAvatar";
import Avatar from "./pages/Avatar";
import Garments from "./pages/Garments";


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

        {/* =================================================
            MAIN APPLICATION LAYOUT
            ================================================= */}

        <Route element={<MainLayout />}>


          {/* =================================================
              PUBLIC ROUTES
              ================================================= */}

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


          {/* =================================================
              PROTECTED ROUTES
              ================================================= */}

          {/*
           * ProtectedRoute checks whether the user has
           * a valid authenticated session before allowing
           * access to the application pages.
           */}

          <Route element={<ProtectedRoute />}>


            {/* =================================================
                DASHBOARD
                ================================================= */}

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />


            {/* =================================================
                VIDEO UPLOAD
                ================================================= */}

            <Route
              path="/upload-video"
              element={<UploadVideo />}
            />


            {/* =================================================
                AVATAR GENERATION
                ================================================= */}

            <Route
              path="/generate-avatar"
              element={<GenerateAvatar />}
            />


            {/* =================================================
                AVATAR VIEWER
                ================================================= */}

            <Route
              path="/avatar"
              element={<Avatar />}
            />


            {/* =================================================
                RETAILER GARMENTS
                ================================================= */}

            {/*
             * The Garments page is protected by authentication
             * at the routing level.
             *
             * Garments.jsx additionally checks that the
             * authenticated user has the retailer role.
             *
             * The backend also independently enforces retailer
             * authorization using require_retailer.
             */}

            <Route
              path="/garments"
              element={<Garments />}
            />

          </Route>

        </Route>

      </Routes>

    </BrowserRouter>
  );
}


export default App;