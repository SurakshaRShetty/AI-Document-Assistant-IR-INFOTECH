import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import api from "../api/axios";

export default function Upload() {
  const navigate = useNavigate();

  const uploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("/documents", formData);

      localStorage.setItem("document_id", res.data.document_id || res.data.id);

      navigate("/chat");
    } catch {
      alert("Upload failed");
    }
  };

  return (
    <>
      <Header />

      <div style={styles.page}>
        <div style={styles.card}>
          <h2>Upload Document</h2>
          <p style={styles.text}>
            Upload a PDF file to start chatting with your document
          </p>

          <input type="file" onChange={uploadFile} />
        </div>
      </div>
    </>
  );
}

const styles = {
  page: {
    background: "#f5f7fb",
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    background: "#fff",
    padding: "30px",
    width: "400px",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    textAlign: "center",
  },
  text: {
    color: "#555",
    marginBottom: "20px",
  },
};
