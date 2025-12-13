import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FirstPerson - Audio Conversation",
  description: "Talk with FirstPerson AI companion",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
