import { useState, useEffect } from "react";
import { Modal, Table, Tooltip } from "antd";
import axios from "axios";
import {
  CheckSquareTwoTone,
  EyeTwoTone,
  FilePdfTwoTone,
  RightSquareTwoTone,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const Jobs = () => {
  const [files, setFiles] = useState([]);
  const [startRecord, setStartRecord] = useState(null);
  const navigate = useNavigate();

  const handleOk = () => {
    const formData = new FormData();
    formData.append("job_description_id", startRecord.id);

    axios
      .post("http://localhost:8000/api/scan-compatibilities/", formData)
      .then(() => {
        setStartRecord(null);
      });
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: "Company",
      dataIndex: "company",
      key: "company",
    },
    {
      title: "Title",
      dataIndex: "title",
      key: "title",
    },
    {
      title: "Position",
      dataIndex: "position",
      key: "position",
    },
    {
      title: "Salary",
      dataIndex: "salary",
      key: "salary",
    },
    {
      title: "is For Fresher",
      dataIndex: "is_applicable_for_freshers",
      key: "is_applicable_for_freshers",
      render: (text) => (
        <Tooltip title={text ? "Fresher can apply" : "Fresher cannot apply"}>
          <CheckSquareTwoTone
            twoToneColor={text ? "green" : "gray"}
            style={{ cursor: "pointer" }}
          />
        </Tooltip>
      ),
    },
    {
      title: "City",
      dataIndex: "city",
      key: "city",
    },
    {
      title: "Email",
      dataIndex: "email",
      key: "email",
    },
    {
      title: "Job",
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
    axios.get("http://localhost:8000/api/job/").then((response) => {
      setFiles(response.data);
    });
  }, []);

  return (
    <div style={{ margin: "1rem 0" }}>
      <h1 style={{ margin: "1rem" }}>Jobs</h1>
      <Table columns={columns} dataSource={files} />
      <Modal
        title="Are you sure?"
        open={startRecord}
        onOk={handleOk}
        okText="Yes"
        onCancel={() => setStartRecord(null)}
      >
        <p>
          This Action will start searching for relevant resumes for job{" "}
          {startRecord?.id}.
        </p>
      </Modal>
    </div>
  );
};

export default Jobs;
