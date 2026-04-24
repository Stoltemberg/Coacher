"use client";

import AppDashboard from "@/components/app/AppDashboard";
import AuthUI from "@/components/app/AuthUI";
import { useBridge } from "@/contexts/BridgeContext";

export default function DesktopPage() {
  const { auth } = useBridge();
  return auth?.authenticated ? <AppDashboard /> : <AuthUI />;
}
