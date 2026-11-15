
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Phone,
  MessagesSquare,
  ChartNoAxesCombined,
  Bot,
  Settings,
  AudioWaveform,
  X,
} from "lucide-react";

const navigation = [
  { name: "Overview", path: "/", icon: LayoutDashboard },
  { name: "Call History", path: "/calls", icon: Phone },
  { name: "Conversations", path: "/conversations", icon: MessagesSquare },
  { name: "Analytics", path: "/analytics", icon: ChartNoAxesCombined },
  { name: "Agent Settings", path: "/settings", icon: Bot },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-20 items-center justify-between border-b border-slate-100 px-6">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-2 text-white">
              <AudioWaveform size={21} />
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              SamvadAI
            </span>
          </div>

          <button onClick={onClose} className="lg:hidden">
            <X size={21} />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-4 py-6">
          <p className="mb-4 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Workspace
          </p>

          {navigation.map(({ name, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                }`
              }
            >
              <Icon size={19} />
              {name}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-100 p-4">
          <NavLink
            to="/settings"
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-500 hover:bg-slate-50"
          >
            <Settings size={19} />
            Settings
          </NavLink>

          <div className="mt-4 rounded-xl bg-slate-50 p-3">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs font-medium text-slate-700">
                SamvadAI Workspace
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Admission voice assistant
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
