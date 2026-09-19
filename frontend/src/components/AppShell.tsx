import { NavLink, Navigate, Outlet } from 'react-router-dom';
import {
  LayoutDashboard, User, Sparkles, Compass, Target, Map, ClipboardList,
  FolderGit2, BarChart3, Settings as SettingsIcon, LogOut, Users,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { LoadingState } from './States';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/profile', label: 'My Profile', icon: User },
  { to: '/skills', label: 'Skill Intelligence', icon: Sparkles },
  { to: '/careers', label: 'Career Explorer', icon: Compass },
  { to: '/gap-analysis', label: 'Skill Gap Analysis', icon: Target },
  { to: '/roadmap', label: 'Learning Roadmap', icon: Map },
  { to: '/assessments', label: 'Assessments', icon: ClipboardList },
  { to: '/evidence', label: 'Projects / Evidence', icon: FolderGit2 },
  { to: '/analytics', label: 'Progress Analytics', icon: BarChart3 },
  { to: '/placement', label: 'Placement Insights', icon: Users },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
];

export function AppShell() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside
        className="fixed inset-y-0 left-0 z-20 flex w-64 flex-col justify-between px-4 py-6"
        style={{ background: 'var(--ink)', color: 'var(--slate-dark)' }}
      >
        <div>
          <div className="mb-8 flex items-center gap-2 px-2">
            <img
              src="/careerlens-logo.png"
              alt="CareerLens AI"
              className="h-7 w-7 rounded object-contain"
            />
            <span className="font-display text-lg text-white">CareerLens AI</span>
          </div>
          <nav className="flex flex-col gap-0.5">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `focus-ring flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                    isActive ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                <Icon size={17} strokeWidth={1.75} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="border-t px-2 pt-4" style={{ borderColor: 'var(--line-dark)' }}>
          <p className="truncate text-sm text-white">{user?.full_name}</p>
          <p className="truncate text-xs">{user?.email}</p>
          <button
            onClick={logout}
            className="focus-ring mt-3 flex items-center gap-2 text-xs hover:text-white"
          >
            <LogOut size={14} /> Log out
          </button>
        </div>
      </aside>
      <main className="ml-64 min-h-screen flex-1 px-10 py-8" style={{ background: 'var(--paper)' }}>
        <Outlet />
      </main>
    </div>
  );
}

export function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingState label="Checking your session…" />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.onboarding_complete) return <Navigate to="/onboarding" replace />;
  return <Outlet />;
}

export function RequireAuthOnly() {
  // For onboarding: needs a logged-in user, but doesn't require onboarding to be complete
  const { user, loading } = useAuth();
  if (loading) return <LoadingState label="Checking your session…" />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
