import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Software Compiler | Prompt → Executable App Config",
  description: "Compiler-style pipeline that converts natural language product prompts into strict, validated, executable application configurations.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
