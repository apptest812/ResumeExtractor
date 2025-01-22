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

const JobDescription = () => {
  const { id } = useParams();
  const [jobDescription, setJobDescription] = useState(null);
  const [compatibilities, setCompatibilities] = useState([]);
  const [error, setError] = useState("");
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const navigate = useNavigate();

  const handleRetry = (record) => {
    if (record.status === "is_error") {
      const formData = new FormData();
      formData.append("job_description_id", id);
      formData.append("resume_id", record.resume__id);

      axios.post("http://localhost:8000/api/compatibility/", formData);
    }
  };

  const handleStartScan = () => {
    const formData = new FormData();
    formData.append("job_description_id", id);

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
      dataIndex: "resume__id",
      key: "resume__id",
    },
    {
      title: "Resume",
      dataIndex: "resume__name",
      key: "resume__name",
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
      dataIndex: "resume_compatibility",
      key: "resume_compatibility",
    },
    {
      title: "Resume",
      dataIndex: "resume__file",
      key: "resume__file",
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
                onClick={() => navigate("/resumes/" + record.resume__id)}
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
      axios.get("http://localhost:8000/api/job/?id=" + id).then((response) => {
        setJobDescription(response.data);
      });
      axios
        .get(
          "http://localhost:8000/api/compatibility/?job_description_id=" + id
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
  return jobDescription ? (
    <div style={{ padding: "20px" }}>
      <Card title="Job Details" bordered={false}>
        <Title level={4}>{jobDescription.title}</Title>
        <Descriptions bordered column={1}>
          <Descriptions.Item label="ID">{jobDescription.id}</Descriptions.Item>
          <Descriptions.Item label="Company">
            {jobDescription.company}
          </Descriptions.Item>
          <Descriptions.Item label="Position">
            {jobDescription.position || "-"}
          </Descriptions.Item>
          <Descriptions.Item label="Salary">
            {jobDescription.salary}
          </Descriptions.Item>
          <Descriptions.Item label="Is For Fresher">
            {jobDescription.is_applicable_for_freshers ? "Yes" : "No"}
          </Descriptions.Item>
          <Descriptions.Item label="City">
            {jobDescription.city}
          </Descriptions.Item>
          <Descriptions.Item label="Email">
            {jobDescription.email}
          </Descriptions.Item>
          <Descriptions.Item label="Job File">
            <Tooltip title="Open File">
              <FilePdfTwoTone
                twoToneColor="red"
                onClick={() =>
                  window.open(
                    "http://localhost:8000/" + jobDescription.file,
                    "_blank"
                  )
                }
                style={{ cursor: "pointer" }}
              />
            </Tooltip>
          </Descriptions.Item>
          <Descriptions.Item label="Uploaded At">
            {jobDescription.uploaded_at}
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
            This Action will start searching for relevant resumes for job {id}.
          </p>
        </Modal>
      </div>
    </div>
  ) : (
    "Loading..."
  );
};

export default JobDescription;
