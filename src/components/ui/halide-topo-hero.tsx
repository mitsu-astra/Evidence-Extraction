import { cn } from "@/lib/utils";
import { useState } from "react";

/**
 * Halide Component - Simple interactive counter with Halide aesthetic
 * Demonstrates the silver/accent color scheme
 */
export const Component = () => {
  const [count, setCount] = useState(0);

  return (
    <style>{`
      .halide-card {
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid rgba(255, 60, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      }

      .halide-card:hover {
        border-color: rgba(255, 60, 0, 0.6);
        box-shadow: 0 0 20px rgba(255, 60, 0, 0.3);
      }

      .halide-btn {
        background: transparent;
        border: 1px solid #ff3c00;
        color: #ff3c00;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
      }

      .halide-btn:hover {
        background: rgba(255, 60, 0, 0.1);
        box-shadow: 0 0 15px rgba(255, 60, 0, 0.5);
        transform: translateY(-2px);
      }

      .halide-text {
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
      }

      .halide-accent {
        color: #ff3c00;
        text-shadow: 0 0 10px rgba(255, 60, 0, 0.5);
      }
    `}</style>

    <div className={cn("halide-card flex flex-col items-center gap-6 p-8 rounded-lg")}>
      <h1 className="halide-text text-2xl font-bold">HALIDE_COMPONENT</h1>
      <h2 className="halide-accent text-5xl font-bold">{String(count).padStart(3, '0')}</h2>
      <div className="flex gap-4">
        <button 
          className="halide-btn"
          onClick={() => setCount((prev) => prev - 1)}
        >
          [ − ]
        </button>
        <button 
          className="halide-btn"
          onClick={() => setCount((prev) => prev + 1)}
        >
          [ + ]
        </button>
      </div>
      <p className="halide-text text-xs opacity-60 font-mono">INTERACTION_COUNTER</p>
    </div>
  );
};

