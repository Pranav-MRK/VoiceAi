
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  MessageSquare,
  Phone,
  RefreshCw,
  Server,
  Wifi,
  WifiOff,
} from "lucide-react";

import {
  getDashboardStats,
  getCalls,
  getBackendHealth,
} from "../services/api";

const formatDate = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

const StatCard = ({ title, value, icon: Icon, description, color }) => (
  <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <h3 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
          {value ?? "—"}
        </h3>
      </div>

      <div className={`rounded-lg p-3 ${color}`}>
        <Icon size={21} />
      </div>
    </div>

    <p className="mt-4 text-xs text-slate-500">{description}</p>
  </div>
);

const StatusBadge = ({ status }) => {
  const isActive = status === "active";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
        isActive
          ? "bg-emerald-50 text-emerald-700"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isActive ? "bg-emerald-500" : "bg-slate-400"
        }`}
      />
      {status || "Unknown"}
    </span>
  );
};

export default function Overview() {
  const [stats, setStats] = useState(null);
  const [calls, setCalls] = useState([]);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [statsData, callsData, healthData] = await Promise.allSettled([
        getDashboardStats(),
        getCalls(5, 0),
        getBackendHealth(),
      ]);

      if (statsData.status === "rejected") {
        throw statsData.reason;
      }

      setStats(statsData.value);

      if (callsData.status === "fulfilled") {
        setCalls(callsData.value.calls || []);
      } else {
        setCalls([]);
      }

      setBackendOnline(
        healthData.status === "fulfilled" &&
          healthData.value.status === "healthy"
      );

      setLastUpdated(new Date());
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load dashboard data. Please check your backend."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  return (
    <div className="space-y-7">
      {/* Page heading */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Overview
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Monitor your SamvadAI voice assistant activity.
          </p>
        </div>

        <button
          onClick={loadDashboard}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw
            size={16}
            className={loading ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {/* Backend error */}
      {error && (
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <WifiOff size={19} className="mt-0.5 shrink-0" />
          <div>
            <p className="font-medium">Dashboard data unavailable</p>
            <p className="mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Calls"
          value={loading && !stats ? "..." : stats?.total_calls}
          icon={Phone}
          description="All calls recorded in the database"
          color="bg-blue-50 text-blue-600"
        />

        <StatCard
          title="Active Calls"
          value={loading && !stats ? "..." : stats?.active_calls}
          icon={Activity}
          description="Calls currently marked as active"
          color="bg-emerald-50 text-emerald-600"
        />

        <StatCard
          title="Completed Calls"
          value={loading && !stats ? "..." : stats?.completed_calls}
          icon={CheckCircle2}
          description="Calls successfully marked completed"
          color="bg-violet-50 text-violet-600"
        />

        <StatCard
          title="Total Messages"
          value={loading && !stats ? "..." : stats?.total_messages}
          icon={MessageSquare}
          description="Messages stored across all calls"
          color="bg-amber-50 text-amber-600"
        />
      </div>

      {/* Recent calls and system status */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Recent calls */}
        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm xl:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <div>
              <h2 className="font-semibold text-slate-900">
                Recent Calls
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Latest call records from PostgreSQL
              </p>
            </div>

            <span className="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              Latest 5
            </span>
          </div>

          {loading && calls.length === 0 ? (
            <div className="p-10 text-center text-sm text-slate-500">
              Loading recent calls...
            </div>
          ) : calls.length === 0 ? (
            <div className="p-10 text-center">
              <Phone className="mx-auto text-slate-300" size={30} />
              <p className="mt-3 text-sm font-medium text-slate-700">
                No calls found
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Call records will appear here when available.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Call ID
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Language
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Messages
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Status
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Started
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {calls.map((call) => (
                    <tr
                      key={call.call_id}
                      className="transition hover:bg-slate-50"
                    >
                      <td className="whitespace-nowrap px-5 py-4">
                        <span className="font-mono text-xs text-slate-700">
                          {call.call_id.slice(0, 8)}...
                        </span>
                      </td>

                      <td className="px-5 py-4 text-sm text-slate-600">
                        {call.language?.toUpperCase() || "—"}
                      </td>

                      <td className="px-5 py-4 text-sm text-slate-600">
                        {call.message_count ?? 0}
                      </td>

                      <td className="px-5 py-4">
                        <StatusBadge status={call.status} />
                      </td>

                      <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-500">
                        {formatDate(call.started_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* System status */}
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900">
            System Status
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Current backend availability
          </p>

          <div className="mt-6 flex items-center gap-3 rounded-lg bg-slate-50 p-4">
            {backendOnline ? (
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <Wifi size={20} />
              </div>
            ) : (
              <div className="rounded-lg bg-red-100 p-2 text-red-600">
                <WifiOff size={20} />
              </div>
            )}

            <div>
              <p className="text-sm font-medium text-slate-800">
                FastAPI Backend
              </p>
              <p
                className={`mt-0.5 text-xs font-medium ${
                  backendOnline ? "text-emerald-600" : "text-red-600"
                }`}
              >
                {backendOnline ? "Connected" : "Unavailable"}
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-slate-600">
                <Server size={16} />
                API service
              </span>
              <span className="text-xs font-medium text-slate-500">
                {backendOnline ? "Healthy" : "Unknown"}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-slate-600">
                <Clock3 size={16} />
                Last updated
              </span>
              <span className="text-xs text-slate-500">
                {lastUpdated
                  ? lastUpdated.toLocaleTimeString("en-IN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "—"}
              </span>
            </div>
          </div>

          <div className="mt-6 border-t border-slate-100 pt-4">
            <p className="text-xs leading-relaxed text-slate-500">
              Dashboard data is retrieved from the SamvadAI API and
              PostgreSQL database.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

