import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const CAP_COLORS: Record<string, string> = {
  text: "bg-gray-50 text-gray-700 dark:bg-gray-950 dark:text-gray-300",
  coding: "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  reasoning: "bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300",
  vision: "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300",
  tts: "bg-pink-50 text-pink-700 dark:bg-pink-950 dark:text-pink-300",
  audio: "bg-orange-50 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
  embedding: "bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
  image: "bg-cyan-50 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-300",
  tool: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
};

const FALLBACK = "bg-muted text-muted-foreground";

export function capClass(cap: string): string {
  return CAP_COLORS[cap] || FALLBACK;
}
