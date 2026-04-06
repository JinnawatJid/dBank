import { NAVIGATION_LINKS } from "../../config/constants";

export default function TopNavBar() {
  return (
    <header className="fixed top-0 w-full z-50 bg-[#f7f9fb] flex justify-between items-center h-16 px-8 border-none">
      <div className="flex items-center gap-8">
        <span className="text-xl font-bold font-headline text-[#191c1e]">Deep Insights Copilot</span>
        <nav className="hidden md:flex items-center gap-6">
          {NAVIGATION_LINKS.map((link) => (
            <a key={link.label} className="text-slate-500 hover:text-slate-900 font-body text-[11px] uppercase tracking-wider transition-colors" href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <button aria-label="Notifications" className="p-2 text-slate-500 hover:bg-slate-200/50 transition-all rounded-lg active:opacity-80">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button aria-label="Settings" className="p-2 text-slate-500 hover:bg-slate-200/50 transition-all rounded-lg active:opacity-80">
          <span className="material-symbols-outlined">settings</span>
        </button>
        <div className="w-8 h-8 rounded-full overflow-hidden bg-surface-container ml-2">
          <img
            alt="Current user's profile avatar"
            className="w-full h-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuASv9iVMcCOmQ1DQjhrEy8Va7ehMzO34yLNrLvNX4_pDJq4C02YuOk44tjGNJXCJVjITDf87Vfaaj4CPTKbBY4ITpnBsyl6cy1bpkvr6INrbomrgHJNjhc61Gu8sGBd-bpQ9KSXBGwfP5U0r4ML97vZaZu2GsPV81B6OzD7SJuB3NjydCWZ6XAIB9ia7oYqzLUT2GtsPRu02kl3iQE3x6o2yEhn6Woim74t7XT_konc7YruWDtIQr-Wc2zgxDQWV3tMzcsHQv8yTV4E"
          />
        </div>
      </div>
    </header>
  );
}
