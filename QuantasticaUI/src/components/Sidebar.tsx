import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Bot, Newspaper, Users, Shield, BarChart, FileText, Calendar, User, Menu, X, Sparkles } from 'lucide-react';

const navItems = [
  { name: 'Dashboard', icon: Home, path: '/dashboard' },
  { name: 'Insights', icon: Sparkles, path: '/insights' },
  { name: 'Chat', icon: Bot, path: '/chat' },
  { name: 'News Analysis', icon: Newspaper, path: '/news' },
  { name: 'Group Investments', icon: Users, path: '/group-investments' },
  { name: 'Risk Analyzer', icon: Shield, path: '/investments' },
  { name: 'Finance Tracker', icon: BarChart, path: '/finance-tracker' },
  { name: 'Tax Advisor', icon: FileText, path: '/tax-advisor' },
  { name: 'Family Finance', icon: User, path: '/family-finance' },
  { name: 'Trade Execution', icon: Calendar, path: '/trade-execution' },
];

export default function Sidebar() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={toggleSidebar}
        className="fixed top-4 left-4 z-50 p-2 rounded-md bg-accent text-accent-foreground md:hidden"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-card/80 backdrop-blur-xl text-card-foreground flex flex-col p-6 shadow-xl glass
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:static md:flex
          z-40
        `}
      >
        <div>
          <h1 className="text-2xl font-bold mb-2">Quantastica</h1>
          <p className="text-xs opacity-70 mb-6">Your Personal Finance Assistant</p>
          <div className="mb-8">
            <div className="text-sm font-semibold">Premium Plan</div>
            <div className="text-xs opacity-70 mb-1">20 days left in trial</div>
            <div className="w-full h-2 bg-background rounded-full">
              <div className="h-full bg-accent rounded-full w-3/4 transition-all duration-500"></div>
            </div>
          </div>
          <nav className="flex-1">
            <ul className="space-y-2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <li key={item.name} className="relative group">
                    <Link
                      to={item.path}
                      onClick={() => setSidebarOpen(false)} // close sidebar on link click (mobile)
                      className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg transition-all duration-200
                        ${isActive ? 'bg-background/60 shadow ring-2 ring-accent/30' : 'hover:bg-background/40'}
                      `}
                    >
                      <span
                        className={`absolute left-0 top-0 h-full w-1 rounded-r-lg transition-transform duration-300
                          ${isActive ? 'bg-accent scale-y-100' : 'bg-accent scale-y-0 group-hover:scale-y-100'}
                          origin-top
                        `}
                      ></span>
                      <item.icon className="h-5 w-5 text-accent transition-transform duration-200 group-hover:scale-110" />
                      <span className="font-medium">{item.name}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
        <div className="mt-auto pt-8">
          <button className="w-full py-2 rounded-lg bg-accent text-accent-foreground font-semibold hover:opacity-90 transition-all duration-200 shadow-lg hover:scale-105">
            Upgrade to Premium
          </button>
        </div>
      </aside>
    </>
  );
}
