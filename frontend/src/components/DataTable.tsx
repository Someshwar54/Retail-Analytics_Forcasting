interface DataTableProps {
  headers: string[];
  rows: Record<string, string | number>[];
  keyField: string;
}

export default function DataTable({ headers, rows, keyField }: DataTableProps) {
  if (!rows.length) return null;

  return (
    <div className="glass-card overflow-hidden animate-fade-in-up">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/[0.06]">
              {headers.map((h) => (
                <th
                  key={h}
                  className="px-5 py-3.5 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={String(row[keyField]) + i}
                className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
              >
                {headers.map((h) => {
                  const val = row[h];
                  const formatted =
                    typeof val === "number"
                      ? val >= 1000
                        ? `$${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                        : val.toLocaleString(undefined, { maximumFractionDigits: 2 })
                      : String(val);
                  return (
                    <td key={h} className="px-5 py-3 text-slate-300">
                      {formatted}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
