
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  MessageSquare,
  Clock3,
  Phone,
  RefreshCw,
  BarChart3,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";

import { getDashboardAnalytics } from "../services/api";

const STATUS_COLORS = {
  active: "#10B981",
  completed: "#2563EB",
};

const formatDuration = (seconds = 0) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);

  if (minutes === 0) return `${remainingSeconds}s`;

  return `${minutes}m ${remainingSeconds}s`;
};

const formatDay = (value) => {
  if (!value) return "";

  return new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
};

function MetricCard({ title, value, description, icon: Icon, color }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <h3 className="mt-3 text-2xl font-semibold text-slate-900">
            {value}
          </h3>
        </div>

        <div className={`rounded-lg p-3 ${color}`}>
          <Icon size={21} />
        </div>
      </div>

      <p className="mt-4 text-xs text-slate-500">{description}</p>
    </div>
  );
}

function ChartCard({ title, description, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5">
        <h2 className="font-semibold text-slate-900">{title}</h2>
        <p className="mt-1 text-xs text-slate-500">{description}</p>
      </div>

      {children}
    </section>
  );
}

function EmptyChart({ message = "No data available yet" }) {
  return (
    <div className="flex h-full min-h-57.5 items-center justify-center text-sm text-slate-400">
      {message}
    </div>
  );
}

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getDashboardAnalytics();
      setAnalytics(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load analytics. Please check your backend."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  const dailyActivity = analytics?.daily_activity || [];
  const callStatus = analytics?.call_status || [];
  const languageDistribution = analytics?.language_distribution || [];

  const statusTotal = callStatus.reduce(
    (sum, item) => sum + item.count,
    0
  );

  const hasActivity = dailyActivity.some(
    (item) => item.total_calls > 0
  );

  const hasStatus = statusTotal > 0;
  const hasLanguages = languageDistribution.length > 0;

  return (
    <div className="space-y-7">
      {/* Heading */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Analytics
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Understand call activity and SamvadAI usage.
          </p>
        </div>

        <button
          onClick={loadAnalytics}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-60"
        >
          <RefreshCw
            size={16}
            className={loading ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Calls this week"
          value={
            loading
              ? "..."
              : dailyActivity.reduce(
                  (sum, item) => sum + item.total_calls,
                  0
                )
          }
          description="Calls started in the last 7 days"
          icon={Phone}
          color="bg-blue-50 text-blue-600"
        />

        <MetricCard
          title="Total Messages"
          value={loading ? "..." : analytics?.total_messages ?? 0}
          description="Messages stored across all calls"
          icon={MessageSquare}
          color="bg-violet-50 text-violet-600"
        />

        <MetricCard
          title="Average Duration"
          value={
            loading
              ? "..."
              : formatDuration(
                  analytics?.average_call_duration_seconds || 0
                )
          }
          description="Average completed-call duration"
          icon={Clock3}
          color="bg-amber-50 text-amber-600"
        />

        <MetricCard
          title="Languages"
          value={loading ? "..." : languageDistribution.length}
          description="Languages represented in call records"
          icon={Activity}
          color="bg-emerald-50 text-emerald-600"
        />
      </div>

      {loading && !analytics ? (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500">
          Loading analytics...
        </div>
      ) : analytics ? (
        <>
          {/* Daily activity */}
          <ChartCard
            title="Call Activity"
            description="Daily call volume over the last 7 days"
          >
            {hasActivity ? (
              <div className="h-75 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={dailyActivity}
                    margin={{ top: 10, right: 15, left: -15, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient
                        id="callActivityGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor="#2563EB"
                          stopOpacity={0.22}
                        />
                        <stop
                          offset="95%"
                          stopColor="#2563EB"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#E2E8F0"
                    />

                    <XAxis
                      dataKey="date"
                      tickFormatter={formatDay}
                      tick={{ fontSize: 12, fill: "#64748B" }}
                      axisLine={false}
                      tickLine={false}
                    />

                    <YAxis
                      allowDecimals={false}
                      tick={{ fontSize: 12, fill: "#64748B" }}
                      axisLine={false}
                      tickLine={false}
                    />

                    <Tooltip
                      labelFormatter={(value) => formatDay(value)}
                      contentStyle={{
                        borderRadius: 10,
                        border: "1px solid #E2E8F0",
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="total_calls"
                      name="Calls"
                      stroke="#2563EB"
                      strokeWidth={2.5}
                      fill="url(#callActivityGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyChart message="No calls recorded in the last 7 days" />
            )}
          </ChartCard>

          {/* Distribution charts */}
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <ChartCard
              title="Call Status Distribution"
              description="Lifetime breakdown of call statuses"
            >
              {hasStatus ? (
                <div className="flex flex-col items-center gap-5 sm:flex-row">
                  <div className="h-60 w-full sm:w-1/2">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={callStatus}
                          dataKey="count"
                          nameKey="status"
                          cx="50%"
                          cy="50%"
                          innerRadius={62}
                          outerRadius={95}
                          paddingAngle={4}
                        >
                          {callStatus.map((item) => (
                            <Cell
                              key={item.status}
                              fill={
                                STATUS_COLORS[item.status] || "#94A3B8"
                              }
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="w-full space-y-4 sm:w-1/2">
                    {callStatus.map((item) => (
                      <div
                        key={item.status}
                        className="flex items-center justify-between gap-3"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className="h-3 w-3 rounded-full"
                            style={{
                              backgroundColor:
                                STATUS_COLORS[item.status] || "#94A3B8",
                            }}
                          />
                          <span className="text-sm capitalize text-slate-600">
                            {item.status}
                          </span>
                        </div>

                        <div className="text-right">
                          <p className="text-sm font-semibold text-slate-900">
                            {item.count}
                          </p>
                          <p className="text-xs text-slate-400">
                            {((item.count / statusTotal) * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <EmptyChart />
              )}
            </ChartCard>

            <ChartCard
              title="Language Distribution"
              description="Calls grouped by detected session language"
            >
              {hasLanguages ? (
                <div className="h-65 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={languageDistribution}
                      margin={{ top: 10, right: 10, left: -15, bottom: 5 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#E2E8F0"
                      />

                      <XAxis
                        dataKey="language"
                        tickFormatter={(value) => value.toUpperCase()}
                        tick={{ fontSize: 12, fill: "#64748B" }}
                        axisLine={false}
                        tickLine={false}
                      />

                      <YAxis
                        allowDecimals={false}
                        tick={{ fontSize: 12, fill: "#64748B" }}
                        axisLine={false}
                        tickLine={false}
                      />

                      <Tooltip
                        formatter={(value) => [value, "Calls"]}
                      />

                      <Bar
                        dataKey="count"
                        name="Calls"
                        fill="#2563EB"
                        radius={[6, 6, 0, 0]}
                        maxBarSize={55}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <EmptyChart message="No language data available" />
              )}
            </ChartCard>
          </div>

          {/* Daily breakdown */}
          <ChartCard
            title="Daily Breakdown"
            description="Call totals and statuses for each day"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Date
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Total Calls
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Completed
                    </th>
                    <th className="px-5 py-3 text-xs font-medium text-slate-500">
                      Active
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {dailyActivity.map((day) => (
                    <tr key={day.date}>
                      <td className="px-5 py-3 text-sm text-slate-700">
                        {formatDay(day.date)}
                      </td>
                      <td className="px-5 py-3 text-sm font-medium text-slate-900">
                        {day.total_calls}
                      </td>
                      <td className="px-5 py-3 text-sm text-blue-600">
                        {day.completed_calls}
                      </td>
                      <td className="px-5 py-3 text-sm text-emerald-600">
                        {day.active_calls}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>
        </>
      ) : null}
    </div>
  );
}
