"use client";

import TopNavBar from "./components/TopNavBar";
import SideNavBar from "./components/SideNavBar";
import ChatInterface from "./components/ChatInterface";

export default function Home() {
  return (
    <>
      <TopNavBar />
      <div className="flex h-screen pt-16">
        <SideNavBar />
        <main className="flex-1 lg:ml-64 flex flex-col h-full bg-surface relative">
          <ChatInterface />

          {/* Background Subtle Gradients */}
          <div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 opacity-30 overflow-hidden">
              <div className="absolute -top-1/4 -right-1/4 w-[800px] h-[800px] bg-gradient-to-br from-secondary-container to-transparent rounded-full blur-[120px]"></div>
              <div className="absolute -bottom-1/4 -left-1/4 w-[600px] h-[600px] bg-gradient-to-tr from-primary-fixed-dim to-transparent rounded-full blur-[100px]"></div>
          </div>
        </main>
      </div>
    </>
  );
}
