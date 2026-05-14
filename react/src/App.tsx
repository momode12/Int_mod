import { BrowserRouter as Router } from "react-router-dom";
import  AuthProvider  from "./providers/AuthProvider";
import  ChatProvider  from "./providers/ChatProvider";
import  ThemeProvider  from "./providers/ThemeProvider";
import  ToastProvider  from "./providers/ToastProvider";
import AppRoutes from "./routes/AppRoutes"; // ← toute la logique routes ici

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <ChatProvider>
            <Router>
              <AppRoutes />
            </Router>
          </ChatProvider>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;