import { useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("document_id");

    navigate("/", { replace: true });
  };

  return (
    <div style={styles.header}>
      <h3>RAG Chatbot</h3>
      <button style={styles.logout} onClick={logout}>
        Logout
      </button>
    </div>
  );
}

const styles = {
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 24px",
    background: "#fff",
    borderBottom: "1px solid #e5e7eb",
  },
  logout: {
    background: "#ef4444",
    color: "#fff",
    border: "none",
    padding: "8px 14px",
    borderRadius: "6px",
    cursor: "pointer",
  },
};
