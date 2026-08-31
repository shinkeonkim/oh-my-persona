import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AdminPage } from "./pages/AdminPage";
import { ChatPage } from "./pages/ChatPage";
import "./styles/base.css";

const page = window.location.pathname.startsWith("/admin") ? <AdminPage /> : <ChatPage />;

createRoot(document.getElementById("root")!).render(<StrictMode>{page}</StrictMode>);
