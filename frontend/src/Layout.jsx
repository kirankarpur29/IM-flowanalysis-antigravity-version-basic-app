import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { FolderKanban, PlusSquare, Settings, Database, Box } from 'lucide-react';

const SidebarItem = ({ to, icon: Icon, label }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${isActive
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
            }`
        }
    >
        <Icon className="w-5 h-5 transition-transform group-hover:scale-110" />
        <span className="font-medium">{label}</span>
    </NavLink>
);

const Layout = () => {
    return (
        <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 flex flex-col border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl">
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Box className="text-white w-6 h-6" />
                        </div>
                        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            MoldFlow<span className="text-blue-500">Pro</span>
                        </h1>
                    </div>

                    <nav className="space-y-2">
                        <SidebarItem to="/" icon={FolderKanban} label="Dashboard" />
                        <SidebarItem to="/new" icon={PlusSquare} label="New Project" />
                        <SidebarItem to="/library" icon={Database} label="Material Library" />
                    </nav>
                </div>

                <div className="mt-auto p-6 border-t border-slate-800">
                    <SidebarItem to="/settings" icon={Settings} label="Settings" />
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;
