
import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  Search,
  RefreshCw,
  MessageSquare,
  User,
  Bot,
  Phone,
  Clock3,
  Languages,
  CalendarDays,
  CheckCircle2,
  AlertCircle,
  MessagesSquare,
} from "lucide-react";

import { getCalls, getCallHistory } from "../services/api";

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

const formatDuration = (startedAt, endedAt) => {
  if (!startedAt || !endedAt) return "In progress";

  const start = new Date(startedAt).getTime();
  const end = new Date(endedAt).getTime();

  if (Number.isNaN(start) || Number.isNaN(end) || end < start) {
    return "—";
  }

  const seconds = Math.floor((end - start) / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes === 0) return `${remainingSeconds}s`;

  return `${minutes}m ${remainingSeconds}s`;
};

const StatusBadge = ({ status }) => {
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
      {status || "Unknown"}
    </span>
  );
};

export default function Conversations() {
  const location = useLocation();

  const [calls, setCalls] = useState([]);
  const [selectedCallId, setSelectedCallId] = useState(
    location.state?.callId || ""
  );
  const [search, setSearch] = useState("");

  const [conversation, setConversation] = useState(null);
  const [loadingCalls, setLoadingCalls] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const selectedCall = useMemo(
    () => calls.find((call) => call.call_id === selectedCallId),
    [calls, selectedCallId]
  );

  const filteredCalls = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return calls;

    return calls.filter(
      (call) =>
        call.call_id.toLowerCase().includes(query) ||
        call.language?.toLowerCase().includes(query) ||
        call.status?.toLowerCase().includes(query)
    );
  }, [calls, search]);

  // Load call list
  useEffect(() => {
    let cancelled = false;

    const loadCalls = async () => {
      setLoadingCalls(true);
      setError("");

      try {
        const data = await getCalls({
          limit: 100,
          offset: 0,
          sort: "newest",
        });

        if (cancelled) return;

        const records = data.calls || [];
        setCalls(records);

        const requestedCallId = location.state?.callId;

        setSelectedCallId((current) => {
          if (
            requestedCallId &&
            records.some((call) => call.call_id === requestedCallId)
          ) {
            return requestedCallId;
          }

          if (current && records.some((call) => call.call_id === current)) {
            return current;
          }

          return records[0]?.call_id || "";
        });
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              "Unable to load conversations."
          );
        }
      } finally {
        if (!cancelled) setLoadingCalls(false);
      }
    };

    loadCalls();

    return () => {
      cancelled = true;
    };
  }, [location.state?.callId, refreshKey]);

  // Load selected call transcript
  useEffect(() => {
    if (!selectedCallId) {
      setConversation(null);
      return;
    }

    let cancelled = false;

    const loadHistory = async () => {
      setLoadingHistory(true);
      setConversation(null);

      try {
        const data = await getCallHistory(selectedCallId);

        if (!cancelled) {
          setConversation(data);
        }
      } catch (err) {
        if (!cancelled) {
          setConversation(null);
          setError(
            err.response?.data?.detail ||
              "Unable to load this conversation."
          );
        }
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    };

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [selectedCallId]);

  const messages = conversation?.messages || [];

  return (
    <div className="space-y-5">
      {/* Heading */}
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Conversations
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Explore call transcripts and conversation details.
          </p>
        </div>

        <button
          onClick={() => setRefreshKey((current) => current + 1)}
          disabled={loadingCalls}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-60"
        >
          <RefreshCw
            size={16}
            className={loadingCalls ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle size={17} />
          {error}
        </div>
      )}

      {/* Three-column workspace */}
      <div className="grid min-h-162.5 grid-cols-1 gap-4 xl:grid-cols-12">
        {/* Left: call list */}
        <section className="flex min-h-87.5 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm xl:col-span-3">
          <div className="border-b border-slate-100 p-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-slate-900">
                All conversations
              </h2>
              <span className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600">
                {calls.length}
              </span>
            </div>

            <div className="relative mt-4">
              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
              />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search calls..."
                className="w-full rounded-lg border border-slate-200 py-2.5 pl-9 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loadingCalls ? (
              <p className="p-6 text-center text-sm text-slate-500">
                Loading conversations...
              </p>
            ) : filteredCalls.length === 0 ? (
              <div className="p-6 text-center">
                <MessagesSquare
                  size={28}
                  className="mx-auto text-slate-300"
                />
                <p className="mt-2 text-sm text-slate-500">
                  No conversations found
                </p>
              </div>
            ) : (
              filteredCalls.map((call) => {
                const selected = call.call_id === selectedCallId;

                return (
                  <button
                    key={call.call_id}
                    onClick={() => setSelectedCallId(call.call_id)}
                    className={`w-full border-b border-slate-100 p-4 text-left transition ${
                      selected
                        ? "border-l-4 border-l-blue-600 bg-blue-50"
                        : "border-l-4 border-l-transparent hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-medium text-slate-800">
                        {call.call_id.slice(0, 13)}...
                      </span>
                      <StatusBadge status={call.status} />
                    </div>

                    <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                      <span>
                        {call.language?.toUpperCase() || "—"}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <MessageSquare size={13} />
                        {call.message_count ?? 0}
                      </span>
                    </div>

                    <p className="mt-2 text-xs text-slate-400">
                      {formatDate(call.started_at)}
                    </p>
                  </button>
                );
              })
            )}
          </div>
        </section>

        {/* Center: transcript */}
        <section className="flex min-h-125 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm xl:col-span-6">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <div>
              <h2 className="font-semibold text-slate-900">
                Conversation transcript
              </h2>
              <p className="mt-1 font-mono text-xs text-slate-500">
                {selectedCallId
                  ? selectedCallId
                  : "Select a conversation"}
              </p>
            </div>

            {conversation && <StatusBadge status={conversation.status} />}
          </div>

          <div className="flex-1 space-y-5 overflow-y-auto bg-slate-50/70 p-5">
            {!selectedCallId ? (
              <div className="flex h-full min-h-87.5 flex-col items-center justify-center text-center">
                <MessageSquare size={40} className="text-slate-300" />
                <h3 className="mt-4 font-medium text-slate-700">
                  Select a conversation
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Choose a call from the left panel to view its transcript.
                </p>
              </div>
            ) : loadingHistory ? (
              <div className="flex min-h-87.5 items-center justify-center text-sm text-slate-500">
                Loading transcript...
              </div>
            ) : messages.length === 0 ? (
              <div className="flex min-h-87.5 flex-col items-center justify-center text-center">
                <MessagesSquare size={36} className="text-slate-300" />
                <p className="mt-3 font-medium text-slate-700">
                  No messages yet
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  This call doesn't have any stored transcript messages.
                </p>
              </div>
            ) : (
              messages.map((message, index) => {
                const isUser = message.role === "user";

                return (
                  <div
                    key={`${message.timestamp || index}-${index}`}
                    className={`flex items-start gap-3 ${
                      isUser ? "justify-end" : "justify-start"
                    }`}
                  >
                    {!isUser && (
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                        <Bot size={18} />
                      </div>
                    )}

                    <div
                      className={`max-w-[85%] rounded-xl px-4 py-3 shadow-sm ${
                        isUser
                          ? "rounded-tr-sm bg-blue-600 text-white"
                          : "rounded-tl-sm border border-slate-200 bg-white text-slate-800"
                      }`}
                    >
                      <div
                        className={`mb-1 text-xs font-semibold ${
                          isUser ? "text-blue-100" : "text-slate-500"
                        }`}
                      >
                        {isUser ? "Caller" : "SamvadAI"}
                      </div>

                      <p className="whitespace-pre-wrap wrap-break-word text-sm leading-relaxed">
                        {message.content}
                      </p>

                      {message.timestamp && (
                        <p
                          className={`mt-2 text-right text-[10px] ${
                            isUser ? "text-blue-100" : "text-slate-400"
                          }`}
                        >
                          {formatDate(message.timestamp)}
                        </p>
                      )}
                    </div>

                    {isUser && (
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
                        <User size={18} />
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>

          <div className="border-t border-slate-100 bg-white px-5 py-3">
            <p className="text-center text-xs text-slate-400">
              Read-only transcript · Messages retrieved from PostgreSQL
            </p>
          </div>
        </section>

        {/* Right: call details */}
        <section className="min-h-87.5 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm xl:col-span-3">
          <div className="border-b border-slate-100 p-5">
            <h2 className="font-semibold text-slate-900">
              Call details
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Metadata for the selected call
            </p>
          </div>

          {selectedCall ? (
            <div className="space-y-5 p-5">
              <div>
                <p className="text-xs text-slate-500">Call ID</p>
                <p className="mt-1 break-all font-mono text-xs text-slate-800">
                  {selectedCall.call_id}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-500">Status</p>
                <div className="mt-2">
                  <StatusBadge status={selectedCall.status} />
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Languages size={17} className="mt-0.5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Language</p>
                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {selectedCall.language?.toUpperCase() || "—"}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MessageSquare size={17} className="mt-0.5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Total messages</p>
                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {selectedCall.message_count ?? messages.length}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CalendarDays size={17} className="mt-0.5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Started at</p>
                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {formatDate(selectedCall.started_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock3 size={17} className="mt-0.5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Duration</p>
                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {formatDuration(
                      selectedCall.started_at,
                      selectedCall.ended_at
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone size={17} className="mt-0.5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Ended at</p>
                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {formatDate(selectedCall.ended_at)}
                  </p>
                </div>
              </div>

              <div className="border-t border-slate-100 pt-4">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <CheckCircle2 size={15} className="text-emerald-500" />
                  Data loaded from SamvadAI API
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-sm text-slate-500">
              Select a call to view its details.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
