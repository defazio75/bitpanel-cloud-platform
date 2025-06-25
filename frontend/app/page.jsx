--- a/frontend/app/page.jsx
+++ b/frontend/app/page.jsx
@@
+// Force this page to run on every request, so redirect() works at runtime
+export const dynamic = 'force-dynamic';
+
 import { redirect } from "next/navigation";

 export default function Home() {
   // Server‐side 307 redirect to /login
   redirect("/login");
 }
