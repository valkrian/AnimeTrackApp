import type { Metadata } from 'next';
import { QueryProvider } from './providers/QueryProvider';
import './globals.css';

export const metadata: Metadata = {
  title: 'Seasonal Anime Tracker',
  description: 'Track current seasonal anime releases',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
