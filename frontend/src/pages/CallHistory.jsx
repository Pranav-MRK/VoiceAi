import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  RefreshCw,
  Phone,
  ChevronLeft,
  ChevronRight,
  CalendarDays,
  MessageSquare,
  X,
} from "lucide-react";

import { getCalls } from "../services/api";

const PAGE_SIZE = 10;

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

function StatusBadge({ status }) {
  const active = status === "active";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
        active
          ? "bg-emerald-50 text-emerald-700"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          active ? "bg-emerald-500" : "bg-slate-400"
        }`}
      />
      {status}
    </span>
  );
}

export default function CallHistory() {
  const navigate = useNavigate();

  const [calls, setCalls] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [refreshKey, setRefreshKey] = useState(0);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [language, setLanguage] = useState("");
  const [sort, setSort] = useState("newest");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  useEffect(() => {
    let cancelled = false;

    const loadCalls = async () => {
      setLoading(true);
      setError("");

      try {
        const data = await getCalls({
          limit: PAGE_SIZE,
          offset: (page - 1) * PAGE_SIZE,
          status,
          language,
          search,
          sort,
        });

        if (!cancelled) {
          setCalls(data.calls || []);
          setTotal(data.total || 0);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              "Unable to load call history. Please try again."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadCalls();

    return () => {
      cancelled = true;
    };
  }, [page, status, language, search, sort, refreshKey]);

  const clearFilters = () => {
    setSearch("");
    setStatus("");
    setLanguage("");
    setSort("newest");
    setPage(1);
  };

  const hasFilters = search || status || language || sort !== "newest";

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Call History
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Search and manage all your SamvadAI conversations.
          </p>
        </div>

        <button
          onClick={() => setRefreshKey((current) => current + 1)}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-60"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Matching calls</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {total}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Current page</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {page}{" "}
            <span className="text-base font-normal text-slate-400">
              / {totalPages}
            </span>
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Records per page</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {PAGE_SIZE}
          </p>
        </div>
      </div>

      {/* Filters */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-slate-900">Filters</h2>
            <p className="mt-1 text-xs text-slate-500">
              Narrow down your call records.
            </p>
          </div>

          {hasFilters && (
            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              <X size={15} />
              Clear filters
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          {/* Search */}
          <div className="relative">
            <Search
              size={17}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="Search Call ID..."
              className="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          {/* Status */}
          <select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>

          {/* Language */}
          <select
            value={language}
            onChange={(event) => {
              setLanguage(event.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          >
            <option value="">All languages</option>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="mr">Marathi</option>
          </select>

          {/* Sorting */}
          <select
            value={sort}
            onChange={(event) => {
              setSort(event.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Calls table */}
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col justify-between gap-2 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-semibold text-slate-900">All Calls</h2>
            <p className="mt-1 text-xs text-slate-500">
              {total} matching records
            </p>
          </div>

          <span className="w-fit rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            PostgreSQL records
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-slate-500">
            Loading call records...
          </div>
        ) : calls.length === 0 ? (
          <div className="p-12 text-center">
            <Phone size={32} className="mx-auto text-slate-300" />
            <p className="mt-3 font-medium text-slate-700">No calls found</p>
            <p className="mt-1 text-sm text-slate-500">
              Try changing your search or filters.
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
                  <th className="px-5 py-3 text-xs font-medium text-slate-500">
                    Ended
                  </th>
                  <th className="px-5 py-3 text-xs font-medium text-slate-500">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {calls.map((call) => (
                  <tr
                    key={call.call_id}
                    onClick={() =>
                      navigate("/conversations", {
                        state: { callId: call.call_id },
                      })
                    }
                    className="cursor-pointer transition hover:bg-blue-50/50"
                  >
                    <td className="whitespace-nowrap px-5 py-4 font-mono text-xs text-slate-700">
                      {call.call_id.slice(0, 8)}...
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-600">
                      {call.language?.toUpperCase() || "—"}
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-600">
                      <span className="inline-flex items-center gap-1.5">
                        <MessageSquare size={14} className="text-slate-400" />
                        {call.message_count ?? 0}
                      </span>
                    </td>

                    <td className="px-5 py-4">
                      <StatusBadge status={call.status} />
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1.5">
                        <CalendarDays size={14} />
                        {formatDate(call.started_at)}
                      </span>
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-500">
                      {formatDate(call.ended_at)}
                    </td>

                    <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-blue-600">
                      View details →
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        <div className="flex flex-col justify-between gap-3 border-t border-slate-100 px-5 py-4 sm:flex-row sm:items-center">
          <p className="text-xs text-slate-500">
            {total === 0
              ? "Showing 0 records"
              : `Showing ${(page - 1) * PAGE_SIZE + 1}–${Math.min(
                  page * PAGE_SIZE,
                  total
                )} of ${total} records`}
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page <= 1 || loading}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft size={16} />
              Previous
            </button>

            <span className="px-2 text-sm text-slate-600">
              {page} / {totalPages}
            </span>

            <button
              onClick={() =>
                setPage((current) => Math.min(totalPages, current + 1))
              }
              disabled={page >= totalPages || loading}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}