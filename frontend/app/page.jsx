// frontend/app/page.jsx

export const dynamic = 'force-dynamic';

import { redirect } from 'next/navigation';

export default function Home() {
  // Server-side 307 redirect to /login
  redirect('/login');
}
