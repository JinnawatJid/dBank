export default function SideNavBar() {
  return (
    <aside className="h-full w-64 fixed left-0 border-r border-slate-200/10 bg-[#f2f4f6] flex flex-col p-4 gap-2 hidden lg:flex">
      <div className="mb-6 px-2">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-2 h-2 rounded-full bg-on-primary-container"></div>
          <span className="font-headline font-bold text-[#00201d] text-sm uppercase">AI Insights</span>
        </div>
        <p className="text-[10px] uppercase font-headline text-slate-500 tracking-tight">Institutional Grade</p>
      </div>

      <button className="flex items-center gap-3 px-4 py-3 bg-white text-[#0c9488] font-semibold rounded-lg shadow-sm translate-x-1 transition-transform">
        <span className="material-symbols-outlined">chat_bubble</span>
        <span className="font-body text-sm font-medium">Current Analysis</span>
      </button>

      <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-200 transition-all duration-200">
        <span className="material-symbols-outlined">history</span>
        <span className="font-body text-sm font-medium">History</span>
      </button>

      <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-200 transition-all duration-200">
        <span className="material-symbols-outlined">analytics</span>
        <span className="font-body text-sm font-medium">Saved Reports</span>
      </button>

      <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-200 transition-all duration-200">
        <span className="material-symbols-outlined">folder_special</span>
        <span className="font-body text-sm font-medium">Collections</span>
      </button>

      <button className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:bg-slate-200 transition-all duration-200">
        <span className="material-symbols-outlined">group</span>
        <span className="font-body text-sm font-medium">Team Shared</span>
      </button>

      <div className="mt-auto pt-4 border-t border-slate-200/50 flex flex-col gap-1">
        <button className="flex items-center gap-3 px-4 py-2 text-slate-500 hover:bg-slate-200 transition-all">
          <span className="material-symbols-outlined">help</span>
          <span className="font-body text-xs">Support</span>
        </button>
        <button className="flex items-center gap-3 px-4 py-2 text-slate-500 hover:bg-slate-200 transition-all">
          <span className="material-symbols-outlined">code</span>
          <span className="font-body text-xs">API Docs</span>
        </button>
      </div>
    </aside>
  );
}
