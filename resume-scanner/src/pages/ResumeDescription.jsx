import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, Descriptions, Tooltip, Typography } from "antd";
import { Table, Modal } from "antd";
import {
  CheckSquareTwoTone,
  CloseCircleTwoTone,
  EyeTwoTone,
  FilePdfTwoTone,
  HourglassTwoTone,
  LoadingOutlined,
  RetweetOutlined,
  RightSquareTwoTone,
} from "@ant-design/icons";

const { Title } = Typography;

const ResumeDescription = () => {
  const { id } = useParams();
  const [resumeDescription, setResumeDescription] = useState(null);
  const [compatibilities, setCompatibilities] = useState([]);
  const [error, setError] = useState("");
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const navigate = useNavigate();

  const handleRetry = (record) => {
    if (record.status === "is_error") {
      const formData = new FormData();
      formData.append("job_description_id", record.job_description__id);
      formData.append("resume_id", id);

      axios.post("http://localhost:8000/api/compatibility/", formData);
    }
  };

  const handleStartScan = () => {
    const formData = new FormData();
    formData.append("resume_id", id);

    axios
      .post("http://localhost:8000/api/scan-compatibilities/", formData)
      .then(() => {
        setIsConfirmModalOpen(false);
      });
  };

  const handleCancel = () => {
    setError("");
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "job_description__id",
      key: "job_description__id",
    },
    {
      title: "Job",
      dataIndex: "job_description__title",
      key: "job_description__title",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (text, data) => {
        switch (text) {
          case "in_progress":
            return (
              <Tooltip title="In Progress">
                <LoadingOutlined style={{ color: "blue" }} />
              </Tooltip>
            );
          case "is_error":
            return (
              <Tooltip title="Error">
                <CloseCircleTwoTone
                  style={{ cursor: "pointer" }}
                  onClick={() => setError(data?.error)}
                  twoToneColor="red"
                />
              </Tooltip>
            );
          case "completed":
            return (
              <Tooltip title="Completed">
                <CheckSquareTwoTone
                  twoToneColor={text ? "green" : "gray"}
                  style={{ cursor: "pointer" }}
                />
              </Tooltip>
            );
          default:
            return (
              <Tooltip title="Pending">
                <HourglassTwoTone twoToneColor="orange" />
              </Tooltip>
            );
        }
      },
    },
    {
      title: "Score",
      dataIndex: "job_compatibility",
      key: "job_compatibility",
    },
    {
      title: "Job",
      dataIndex: "job_description__file",
      key: "job_description__file",
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
      title: "Action",
      key: "action",
      render: (record) => (
        <span>
          <span style={{ marginRight: "5px" }}>
            <Tooltip title="Retry">
              <RetweetOutlined
                onClick={() => handleRetry(record)}
                disabled={record.status === "is_error"}
              />
            </Tooltip>
          </span>
          <span style={{ marginRight: "5px" }}>
            <Tooltip title="Open Detail View">
              <EyeTwoTone
                twoToneColor="blue"
                onClick={() => navigate("/jobs/" + record.job_description__id)}
              />
            </Tooltip>
          </span>
        </span>
      ),
    },
  ];
  useEffect(() => {
    // Fetch files from the server
    if (id) {
      axios.get("http://localhost:8000/api/resume/?id=" + id).then((response) => {
        setResumeDescription(response.data);
      });
      axios
        .get(
          "http://localhost:8000/api/compatibility/?resume_id=" + id
        )
        .then((response) => {
          setCompatibilities(
            response.data.sort(
              (a, b) => b.resume_compatibility - a.resume_compatibility
            )
          );
        });
    }
  }, [id]);
  return resumeDescription ? (
    <div style={{ padding: "20px" }}>
      <Card title="Resume Details" bordered={false}>
        <Title level={4}>{resumeDescription.title}</Title>
        <Descriptions bordered column={1}>
          <Descriptions.Item label="ID">{resumeDescription.id}</Descriptions.Item>
          <Descriptions.Item label="Name">
            {resumeDescription.name}
          </Descriptions.Item>
          <Descriptions.Item label="Position">
            {resumeDescription.position || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="Email">
            {resumeDescription.email}
          </Descriptions.Item>
          <Descriptions.Item label="Phone">
            {resumeDescription.phone}
          </Descriptions.Item>
          <Descriptions.Item label="Nationalities">
            {resumeDescription.nationalities || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="Skills">
            {resumeDescription.skills}
          </Descriptions.Item>
          <Descriptions.Item label="Resume File">
            <Tooltip title="Open File">
              <FilePdfTwoTone
                twoToneColor="red"
                onClick={() =>
                  window.open(
                    "http://localhost:8000/" + resumeDescription.file,
                    "_blank"
                  )
                }
                style={{ cursor: "pointer" }}
              />
            </Tooltip>
          </Descriptions.Item>
          <Descriptions.Item label="Uploaded At">
            {resumeDescription.uploaded_at}
          </Descriptions.Item>
          <Descriptions.Item label="Action">
            <Tooltip title="Start Scan">
              <RightSquareTwoTone
                twoToneColor="red"
                onClick={() => setIsConfirmModalOpen(true)}
              />
            </Tooltip>
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <div style={{ margin: "1rem 0" }}>
        <h1 style={{ margin: "1rem" }}>Scan Result</h1>
        <Table columns={columns} dataSource={compatibilities} />
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
          open={isConfirmModalOpen}
          onOk={handleStartScan}
          okText="Yes"
          onCancel={() => setIsConfirmModalOpen(false)}
        >
          <p>
            This Action will start searching for relevant jobs for resume {id}.
          </p>
        </Modal>
      </div>
    </div>
  ) : (
    "Loading..."
  );
};

export default ResumeDescription;
