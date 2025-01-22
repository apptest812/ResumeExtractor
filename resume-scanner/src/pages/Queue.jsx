import { useState, useEffect } from "react";
import { Table, Modal, Tooltip } from "antd";
import axios from "axios";
import {
  CloseCircleTwoTone,
  CodeTwoTone,
  DeleteTwoTone,
  FilePdfTwoTone,
  HourglassTwoTone,
  LoadingOutlined,
  RetweetOutlined,
} from "@ant-design/icons";
import { JsonView, allExpanded, defaultStyles } from "react-json-view-lite";
import { modeAtom } from "../atoms";
import { useRecoilValue } from "recoil";

const Queue = () => {
  const mode = useRecoilValue(modeAtom);
  const [files, setFiles] = useState([]);
  const [json, setJson] = useState("");
  const [error, setError] = useState("");
  const [deleteRecord, setDeleteRecord] = useState(null);

  const handleCancel = () => {
    setJson("");
    setError("");
  };

  const handleRetry = (record) => {
    if (record.is_error) {
      const formData = new FormData();
      formData.append("id", record.id);
      formData.append("is_retry", true);

      axios.post("http://localhost:8000/api/queue/", formData);
    }
  };

  const handleDelete = () => {
    if (deleteRecord.is_error || !deleteRecord.in_progress) {
      axios
        .delete("http://localhost:8000/api/queue/?id=" + deleteRecord.id)
        .then(() => {
          setDeleteRecord(null);
          setFiles((prev) => prev.filter((x) => x.id !== deleteRecord.id));
        });
    }
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: mode.isJobMode ? "Job" : "Resume",
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
      title: "Status",
      dataIndex: "in_progress",
      key: "in_progress",
      render: (in_progress, data) =>
        in_progress ? (
          <Tooltip title="In Progress">
            <LoadingOutlined style={{ color: "blue" }} />
          </Tooltip>
        ) : data.is_error ? (
          <Tooltip title="Error">
            <CloseCircleTwoTone
              style={{ cursor: "pointer" }}
              onClick={() => setError(data?.error)}
              twoToneColor="red"
            />
          </Tooltip>
        ) : (
          <Tooltip title="Pending">
            <HourglassTwoTone twoToneColor="orange" />
          </Tooltip>
        ),
    },
    {
      title: "JSON",
      dataIndex: "json",
      key: "json",
      render: (text) => (
        <Tooltip title={text ? "View JSON" : "JSON not generated"}>
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
            <Tooltip title="Retry">
              <RetweetOutlined
                onClick={() => handleRetry(record)}
                disabled={record.is_error}
              />
            </Tooltip>
          </span>
          <span style={{ marginRight: "5px" }}>
            <Tooltip title="Delete">
              <DeleteTwoTone
                onClick={() => setDeleteRecord(record)}
                disabled={record.is_error}
              />
            </Tooltip>
          </span>
        </span>
      ),
    },
  ];

  useEffect(() => {
    // Fetch files from the server
    axios
      .get(`http://localhost:8000/api/upload/`, {
        params: {
          is_resume: !mode.isJobMode,
          is_job_description: mode.isJobMode,
        },
      })
      .then((response) => {
        setFiles(response.data);
      });
  }, [mode.isJobMode]);

  return (
    <div style={{ margin: "1rem 0" }}>
      <h1 style={{ margin: "1rem" }}>Queue</h1>
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
        open={deleteRecord}
        onOk={handleDelete}
        okText="Yes"
        onCancel={() => setDeleteRecord(null)}
      >
        <p>
          This Action will delete the{" "}
          {deleteRecord?.is_resume ? "resume" : "job"} {deleteRecord?.id} from
          queue.
        </p>
      </Modal>
    </div>
  );
};

export default Queue;
