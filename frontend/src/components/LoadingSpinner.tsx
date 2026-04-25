export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-400 animate-spin" />
        <div className="absolute inset-1 rounded-full border-2 border-transparent border-t-violet-400 animate-spin [animation-duration:1.5s] [animation-direction:reverse]" />
      </div>
      <p className="text-sm text-slate-400 animate-pulse">Loading analytics...</p>
    </div>
  );
}
