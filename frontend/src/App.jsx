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

import MainLayout from "./layouts/MainLayout";


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
          <Route path="/" element={<Home />} />

          {/* User login page. */}
          <Route path="/login" element={<Login />} />

          {/* User registration page. */}
          <Route path="/register" element={<Register />} />

          {/* User dashboard. */}
          <Route path="/dashboard" element={<Dashboard />} />

          <Route path="/upload-video" element={<UploadVideo />}/>

        </Route>

      </Routes>

    </BrowserRouter>
  );
}


export default App;