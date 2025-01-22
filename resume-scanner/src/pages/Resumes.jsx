import { useState, useEffect } from "react";
import { Table, Modal, Tooltip } from "antd";
import axios from "axios";
import {
  CodeTwoTone,
  EyeTwoTone,
  FilePdfTwoTone,
  RightSquareTwoTone,
} from "@ant-design/icons";
import { JsonView, allExpanded, defaultStyles } from "react-json-view-lite";
import { useNavigate } from "react-router-dom";

const Resumes = () => {
  const [files, setFiles] = useState([]);
  const [json, setJson] = useState("");
  const [error, setError] = useState("");
  const [startRecord, setStartRecord] = useState(null);
  const navigate = useNavigate();

  const handleOk = () => {
    const formData = new FormData();
    formData.append("resume_id", startRecord.id);

    axios
      .post("http://localhost:8000/api/scan-compatibilities/", formData)
      .then(() => {
        setStartRecord(null);
      });
  };

  const handleCancel = () => {
    setJson("");
    setError("");
  };
  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Email",
      dataIndex: "email",
      key: "email",
    },
    {
      title: "Position",
      dataIndex: "position",
      key: "position",
    },
    {
      title: "Resume",
      dataIndex: "file",
      key: "file",
      render: (text) => (
        <Tooltip title="Open File">
          <FilePdfTwoTone
            twoToneColor="red"
            onClick={() =>
              window.open("http://localhost:8000/" + text, "_blank")
            }
            style={{ cursor: "pointer" }}
          />
        </Tooltip>
      ),
    },
    {
      title: "JSON",
      dataIndex: "json",
      key: "json",
      render: (text) => (
        <Tooltip title="View JSON">
          <CodeTwoTone
            style={{ cursor: text ? "pointer" : "initial" }}
            twoToneColor={text ? "blue" : "grey"}
            onClick={() => setJson(text)}
          />
        </Tooltip>
      ),
    },
    {
      title: "Uploaded At",
      dataIndex: "uploaded_at",
      key: "uploaded_at",
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: "Action",
      key: "action",
      render: (record) => (
        <span>
          <span style={{ marginRight: "5px" }}>
            <Tooltip title="Open Detail View">
              <EyeTwoTone
                twoToneColor="blue"
                onClick={() => navigate(record.id)}
              />
            </Tooltip>
          </span>
          <span style={{ marginRight: "5px" }}>
            <Tooltip title="Start Scan">
              <RightSquareTwoTone
                twoToneColor="red"
                onClick={() => setStartRecord(record)}
              />
            </Tooltip>
          </span>
        </span>
      ),
    },
  ];

  useEffect(() => {
    // Fetch files from the server
    axios.get("http://localhost:8000/api/resume/").then((response) => {
      setFiles(response.data);
    });
  }, []);

  return (
    <div style={{ margin: "1rem 0" }}>
      <h1 style={{ margin: "1rem" }}>Resumes</h1>
      <Table columns={columns} dataSource={files} />
      <Modal
        title="JSON"
        open={json}
        onOk={handleCancel}
        onCancel={handleCancel}
      >
        <JsonView
          data={json}
          shouldExpandNode={allExpanded}
          style={defaultStyles}
        />
      </Modal>
      <Modal
        title="Error"
        open={error}
        onOk={handleCancel}
        onCancel={handleCancel}
      >
        <p>{error}</p>
      </Modal>
      <Modal
        title="Are you sure?"
        open={startRecord}
        onOk={handleOk}
        okText="Yes"
        onCancel={() => setStartRecord(null)}
      >
        <p>
          This Action will start searching for relevant jobs for resume{" "}
          {startRecord?.id}.
        </p>
      </Modal>
    </div>
  );
};

export default Resumes;
