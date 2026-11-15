
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";

import Overview from "./pages/Overview";
import CallHistory from "./pages/CallHistory";
import Conversations from "./pages/Conversations";
import Analytics from "./pages/Analytics";
import AgentSettings from "./pages/AgentSettings";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/calls" element={<CallHistory />} />
          <Route path="/conversations" element={<Conversations />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<AgentSettings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

