"use client";

import React, { useEffect, useRef, useState } from "react";

interface BossFightProps {
    bgUrl?: string;
    bossLeftUrl?: string;
    bossRightUrl?: string;
    bossForwardUrl?: string;
    overlayUrl?: string;
}

export default function BossFight({
    bgUrl = "/velinor/backgrounds/boss_chamber01.png",
    bossLeftUrl = "/velinor/bosses/triglyph_boss_nobg_left.png",
    bossRightUrl = "/velinor/bosses/triglyph_boss_nobg_right.png",
    bossForwardUrl = "/velinor/bosses/triglyph_boss_nobg_forward2.png",
    overlayUrl = "/velinor/overlays/boss_chamber_fill_overlay.png",
}: BossFightProps) {
    const [x, setX] = useState(0.1); // 0..1
    const dirRef = useRef(1); // 1 right, -1 left
    const speedRef = useRef(0.12); // fraction per second
    const [frame, setFrame] = useState<"left" | "right" | "forward">("right");
    const forwardTimerRef = useRef(0);
    const [overlayFill, setOverlayFill] = useState(0);
    const [hits, setHits] = useState(0);
    const [shudder, setShudder] = useState(false);

    const rafRef = useRef<number | null>(null);
    const lastRef = useRef<number | null>(null);

    useEffect(() => {
        let mounted = true;

        const step = (t: number) => {
            if (!mounted) return;
            if (lastRef.current == null) lastRef.current = t;
            const dt = Math.min(0.05, (t - lastRef.current) / 1000);
            lastRef.current = t;

            // move
            setX((prev) => {
                let next = prev + dirRef.current * speedRef.current * dt;
                if (next >= 0.95) {
                    next = 0.95;
                    dirRef.current = -1;
                    setFrame("left");
                } else if (next <= 0.05) {
                    next = 0.05;
                    dirRef.current = 1;
                    setFrame("right");
                }
                return next;
            });

            // forward window
            if (forwardTimerRef.current <= 0) {
                if (Math.random() < 0.6 * dt) {
                    forwardTimerRef.current = 0.6;
                    setFrame("forward");
                }
            } else {
                forwardTimerRef.current -= dt;
                if (forwardTimerRef.current <= 0) {
                    setFrame(dirRef.current === 1 ? "right" : "left");
                }
            }

            // overlay fill
            setOverlayFill((v) => Math.min(1, v + 0.02 * dt));

            // shudder decays
            if (shudder) {
                // hide shudder after small time
                setTimeout(() => setShudder(false), 180);
            }

            rafRef.current = requestAnimationFrame(step);
        };

        rafRef.current = requestAnimationFrame(step);
        return () => {
            mounted = false;
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [shudder]);

    const handleHit = () => {
        if (frame !== "forward") return;
        // successful hit
        setHits((h) => h + 1);
        setShudder(true);
        speedRef.current = Math.min(1.5, speedRef.current * 1.25);
        setOverlayFill((v) => Math.min(1, v + 0.08));
        // shorten forward window so it doesn't stay
        forwardTimerRef.current = 0;
        setFrame(dirRef.current === 1 ? "right" : "left");
    };

    const bossUrl = frame === "left" ? bossLeftUrl : frame === "right" ? bossRightUrl : bossForwardUrl;

    return (
        <div style={{ position: "relative", width: "100%", maxWidth: 1200, margin: "0 auto", aspectRatio: "16/9", overflow: "hidden" }}>
            <img src={bgUrl} alt="boss bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />

            {/* rising semi-transparent overlay */}
            <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${overlayFill * 100}%`, background: "rgba(18,18,18,0.6)", pointerEvents: "none", transition: "height 0.12s linear", zIndex: 5 }} />

            {/* boss image */}
            <img
                src={bossUrl}
                alt="triglyph"
                onClick={handleHit}
                style={{
                    position: "absolute",
                    bottom: "6%",
                    left: `${x * 100}%`,
                    transform: "translateX(-50%)",
                    height: "45%",
                    cursor: frame === "forward" ? "pointer" : "default",
                    zIndex: 10,
                    transition: shudder ? "transform 0.05s" : "left 0.06s linear",
                    filter: shudder ? "brightness(1.1) drop-shadow(0 8px 18px rgba(0,0,0,0.6))" : "none",
                }}
            />

            {/* small HUD */}
            <div style={{ position: "absolute", left: 12, top: 12, zIndex: 20, color: "#eee", fontSize: 14 }}>
                Overlay: {(overlayFill * 100).toFixed(0)}% • Speed: {speedRef.current.toFixed(2)} • Hits: {hits}
            </div>
        </div>
    );
}
