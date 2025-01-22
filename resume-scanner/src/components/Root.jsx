import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import "./Root.css";

function Root() {
  return (
    <div id="template">
      {/* <h2>Resume Checker</h2> */}
      <div className="main">
        <Sidebar />
        <div className="outlet">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default Root;
