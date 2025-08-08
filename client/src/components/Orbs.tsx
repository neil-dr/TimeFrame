import React from "react";
import "../orbs.css"

/**
 * Visual state of the orb.
 * - "default"     : idle breathing
 * - "listening"   : EQ bars appear, size grows
 * - "processing"  : gentle pulse while thinking
 * - "speaking"    : shrinks slightly while talking
 */
export type OrbMode = "default" | "listening" | "processing" | "speaking";

export interface OrbProps {
  /** Current visual mode. Defaults to "default" */
  mode?: OrbMode;
  /** Extra Tailwind classes */
  className?: string;
}

/**
 * Orb – High‑fidelity recreation of the ChatGPT floating orb.
 *
 * Tailwind utilities handle sizing; bespoke styles (gradients, keyframes)
 * live in `Orb.css` (make sure to `import "./Orb.css"`).
 */
export const Orbs: React.FC<OrbProps> = ({ mode = "default", className = "" }) => {
  /* Tailwind‑controlled diameter per mode */
  const size = {
    default: "w-16 h-16", // 64px
    listening: "w-20 h-20", // 80px
    processing: "w-16 h-16",
    speaking: "w-12 h-12", // 48px
  }[mode];

  return (
    <div
      aria-hidden="true"
      className={`relative inline-block ${size} ${className} orb-${mode}`}
    >
      {/* ----- Core animated layers ----- */}
      <div className="orb-container">
        <div className="orb-layer" />
        <div className="orb-layer" />
        <div className="orb-layer" />

        {/* Ambient glow */}
        <div className="orb-glow" />

        {/* Floating particles */}
        <div className="orb-particles" />

        {/* Glossy highlight */}
        <div className="orb-highlight mix-blend-mode-overlay" />

        {/* Waveform appears only while listening */}
        {mode === "listening" && (
          <div className="waveform-container">
            {Array.from({ length: 5 }).map((_, i) => (
              <span key={i} className="waveform-bar" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Orbs;
