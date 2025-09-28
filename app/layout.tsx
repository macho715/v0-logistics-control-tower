import type { Metadata } from "next";
import "./globals.css";

// Font imports (adjust paths as needed)
import { 
  V0_Font_Geist, 
  V0_Font_Geist_Mono, 
  V0_Font_Source_Serif_4 
} from "./fonts"; // or wherever your fonts are imported from

// ✅ FIX: Initialize fonts and assign to const variables
const geist = V0_Font_Geist({ 
  weight: ["100","200","300","400","500","600","700","800","900"],
  subsets: ["latin"],
  variable: "--font-geist"
});

const geistMono = V0_Font_Geist_Mono({ 
  weight: ["100","200","300","400","500","600","700","800","900"],
  subsets: ["latin"],
  variable: "--font-geist-mono"
});

const sourceSerif = V0_Font_Source_Serif_4({ 
  weight: ["200","300","400","500","600","700","800","900"],
  subsets: ["latin"],
  variable: "--font-source-serif"
});

export const metadata: Metadata = {
  title: "Logistics Control Tower v2.5",
  description: "Advanced logistics management and monitoring system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${geistMono.variable} ${sourceSerif.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
