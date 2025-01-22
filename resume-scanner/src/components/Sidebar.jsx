import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, Switch } from "antd";
import {
  DatabaseFilled,
  ForwardFilled,
  PieChartFilled,
  TagFilled,
} from "@ant-design/icons";
import "./Sidebar.css";
import { useRecoilState } from "recoil";
import { modeAtom } from "../atoms";

const LOCATION_KEYS = {
  dashboard: "1",
  uploads: "2",
  resumes: "3",
};

function Sidebar() {
  const [selectedKeys, setSelectedKeys] = useState(["1"]);
  const [mode, setMode] = useRecoilState(modeAtom);

  const location = useLocation();
  const navigate = useNavigate();
  const url = location.pathname.split("/");

  useEffect(() => {
    if (!url[1]) {
      navigate("/dashboard", { replace: true });
      setSelectedKeys(LOCATION_KEYS["dashboard"]);
    } else {
      setSelectedKeys(LOCATION_KEYS[url[1]]);
    }
  }, [url]);

  return (
    <div id="sidebar">
      <Menu
        mode="inline"
        defaultSelectedKeys={["1"]}
        selectedKeys={selectedKeys}
        items={[
          {
            key: "1",
            icon: <PieChartFilled />,
            label: <Link to="/dashboard">Dashboard</Link>,
          },
          {
            key: "2",
            icon: <ForwardFilled />,
            label: <Link to="/queue">Queue</Link>,
          },
          {
            key: "3",
            icon: <DatabaseFilled />,
            label: <Link to="/resumes">Resumes</Link>,
          },
          {
            key: "4",
            icon: <TagFilled />,
            label: <Link to="/jobs">Jobs</Link>,
          },
        ]}
      />
      <Menu
        mode="inline"
        defaultSelectedKeys={["1"]}
        selectedKeys={selectedKeys}
        className="reverse-list"
        items={[
          {
            key: "r1",
            icon: <Switch value={mode.isUploadMode} onChange={()=>setMode((prev)=>({...prev, isUploadMode: !prev.isUploadMode}))} title="Upload" />,
            label: <div>Upload Mode</div>,
          },
          {
            key: "r2",
            icon: <Switch value={mode.isJobMode} onChange={()=>setMode((prev)=>({...prev, isJobMode: !prev.isJobMode}))} title="Job" />,
            label: <div>Job Mode</div>,
          },
        ]}
      />
    </div>
  );
}

export default Sidebar;
