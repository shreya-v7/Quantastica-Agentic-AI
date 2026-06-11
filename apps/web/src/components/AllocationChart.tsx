import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { AllocationSlice } from "@quantastica/types";
import { formatPercent } from "../lib/format";

const COLORS = ["#4f46e5", "#06b6d4", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899"];

export function AllocationChart({ data }: { data: AllocationSlice[] }) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="weight" nameKey="key" innerRadius={55} outerRadius={90}>
            {data.map((slice, index) => (
              <Cell key={slice.key} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name) => [formatPercent(Number(value)), String(name)]}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
