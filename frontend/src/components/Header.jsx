
import { Menu, Search, Bell } from "lucide-react";
import { useLocation } from "react-router-dom";

const pageTitles = {
  "/": "Overview",
  "/calls": "Call History",
  "/conversations": "Conversations",
  "/analytics": "Analytics",
  "/settings": "Agent Settings",
};

export default function Header({ onMenuClick }) {
  const location = useLocation();
  const title = pageTitles[location.pathname] || "SamvadAI";

  return (
    <header className="flex h-20 items-center justify-between border-b border-slate-200 bg-white px-5 sm:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
        >
          <Menu size={21} />
        </button>

        <div>
          <h1 className="text-lg font-semibold text-slate-900">
            {title}
          </h1>
          <p className="hidden text-xs text-slate-400 sm:block">
            Monitor and manage your AI voice assistant
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="hidden rounded-lg border border-slate-200 p-2 text-slate-500 hover:bg-slate-50 sm:block">
          <Search size={19} />
        </button>

        <button className="relative rounded-lg border border-slate-200 p-2 text-slate-500 hover:bg-slate-50">
          <Bell size={19} />
        </button>

        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
          SA
        </div>
      </div>
    </header>
  );
}
