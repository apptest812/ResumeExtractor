import { InboxOutlined } from "@ant-design/icons";
import { Button, message, Upload } from "antd";
import "./Dashboard.css";
import { modeAtom } from "../atoms";
import { useRecoilValue } from "recoil";
import { useState } from "react";
import TextArea from "antd/es/input/TextArea";
import axios from "axios";

const { Dragger } = Upload;

const Dashboard = () => {
  const mode = useRecoilValue(modeAtom);
  const [description, setDescription] = useState("");

  const dropProps = {
    name: "file",
    multiple: true,
    action: "http://localhost:8000/api/upload/",
    data: mode.isJobMode ? { is_job_description: true } : { is_resume: true },
    onChange(info) {
      const { status } = info.file;
      if (status !== "uploading") {
        console.log(info.file, info.fileList);
      }
      if (status === "done") {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === "error") {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
    onDrop(e) {
      console.log("Dropped files", e.dataTransfer.files);
    },
  };

  const onSubmit = () => {
    let data = new FormData();
    data.append("description", description);
    data.append(mode.isJobMode ? "is_job_description" : "is_resume", true);
    axios.post("http://localhost:8000/api/description/", data);
  };

  return (
    <div id="dashboard">
      <h2>
        {mode.isUploadMode ? "Upload" : "Add"}{" "}
        {mode.isJobMode ? "job description" : "your resume"} here
      </h2>
      <div className="container">
        {mode.isUploadMode ? (
          <div className="dragdrop">
            <Dragger {...dropProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">
                Click or drag file to this area to upload
              </p>
              <p className="ant-upload-hint">
                Support for a single or bulk upload. Strictly prohibited from
                uploading company data or other banned files.
              </p>
            </Dragger>
          </div>
        ) : (
          <>
            <TextArea
              showCount
              onChange={(e) => setDescription(e.target.value)}
              value={description}
              className="description"
            />
            <Button
              onClick={onSubmit}
              className="description-button"
              type="primary"
              size="large"
            >
              Submit
            </Button>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
