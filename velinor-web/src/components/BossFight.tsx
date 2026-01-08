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
    overlayUrl = "/velinor/overlays/chamber-fill_overlay.png",
}: BossFightProps) {
    const [x, setX] = useState(0.1); // 0..1
    const dirRef = useRef(1); // 1 right, -1 left
    const speedRef = useRef(0.09); // fraction per second (slower baseline)
    const [frame, setFrame] = useState<"left" | "right" | "forward">("right");
    const forwardTimerRef = useRef(0);
    const [overlayFill, setOverlayFill] = useState(0);
    const [overlayOffset, setOverlayOffset] = useState(0);
    const [hits, setHits] = useState(0);
    const [shudder, setShudder] = useState(false);
    const [defeated, setDefeated] = useState(false);

    const rafRef = useRef<number | null>(null);
    const lastRef = useRef<number | null>(null);

    useEffect(() => {
        let mounted = true;

        const step = (t: number) => {
            if (!mounted) return;
            if (lastRef.current == null) lastRef.current = t;
            const dt = Math.min(0.08, (t - lastRef.current) / 1000); // cap to ~12.5fps for older systems
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

            // overlay fill — slower baseline so it doesn't overwhelm quickly
            setOverlayFill((v) => Math.min(1, v + 0.003 * dt));
            // move texture slightly for visible motion
            setOverlayOffset((o) => (o + 8 * dt) % 1000);

            // shudder decays
            if (shudder) {
                // hide shudder after small time
                setTimeout(() => setShudder(false), 220);
            }

            // stop animation if defeated (we let a short vanish animation play in UI)
            if (defeated) {
                if (rafRef.current) cancelAnimationFrame(rafRef.current);
                return;
            }

            rafRef.current = requestAnimationFrame(step);
        };

        rafRef.current = requestAnimationFrame(step);
        return () => {
            mounted = false;
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [shudder, defeated]);

    const handleHit = () => {
        if (frame !== "forward" || defeated) return;
        // successful hit
        setHits((h) => {
            const newHits = h + 1;
            // apply speed increase per hit, with a reasonable cap
            speedRef.current = Math.min(2.5, speedRef.current * 1.2);
            // overlay surges on hit
            setOverlayFill((v) => Math.min(1, v + 0.08));

            // shudder visual
            setShudder(true);

            // check for vanquish threshold
            if (newHits >= 10) {
                setDefeated(true);
                // trigger vanish: clear forward window and set frame to forward briefly
                forwardTimerRef.current = 0;
                setFrame("forward");
                // let animation show then stop
                setTimeout(() => {
                    // stop requestAnimationFrame loop by setting defeated true (handled in step)
                }, 300);
            } else {
                // shorten forward window so it doesn't stay
                forwardTimerRef.current = 0;
                setFrame(dirRef.current === 1 ? "right" : "left");
            }

            return newHits;
        });
    };

    const bossUrl = frame === "left" ? bossLeftUrl : frame === "right" ? bossRightUrl : bossForwardUrl;

    // visual filters to increase contrast against background
    const bossBaseFilter = "contrast(1.35) saturate(1.15) drop-shadow(0 12px 24px rgba(0,0,0,0.7))";

    return (
        <div style={{ position: "relative", width: "100%", maxWidth: 1200, margin: "0 auto", aspectRatio: "16/9", overflow: "hidden" }}>
            <style>{`
                                @keyframes bf-shake {
                                    0% { transform: translateX(-50%) translateY(0) rotate(0deg); }
                                    20% { transform: translateX(-50%) translateY(-6px) rotate(-1deg); }
                                    40% { transform: translateX(-50%) translateY(4px) rotate(1deg); }
                                    60% { transform: translateX(-50%) translateY(-3px) rotate(-0.5deg); }
                                    80% { transform: translateX(-50%) translateY(2px) rotate(0.5deg); }
                                    100% { transform: translateX(-50%) translateY(0) rotate(0deg); }
                                }
                                .bf-shake { animation: bf-shake 0.22s ease; }

                                @keyframes bf-pulse {
                                    0% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.8 }
                                    50% { transform: translate(-50%, -50%) scale(1.05); opacity: 1 }
                                    100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.8 }
                                }
                        `}</style>
            <img src={bgUrl} alt="boss bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />

            {/* rising semi-transparent overlay (uses overlay image for texture + tint) */}
            <div style={{
                position: "absolute",
                left: 0,
                right: 0,
                bottom: 0,
                height: `${overlayFill * 100}%`,
                pointerEvents: "none",
                transition: "height 0.6s linear",
                zIndex: 5,
                backgroundImage: `linear-gradient(rgba(8,12,22,0.76), rgba(8,12,22,0.76)), url(${overlayUrl})`,
                backgroundSize: "cover",
                backgroundPosition: `center ${overlayOffset}px`,
                backgroundRepeat: "repeat-y",
                opacity: 0.9,
                mixBlendMode: 'multiply'
            }} />

            {/* boss image or disintegration effect when defeated */}
            {!defeated ? (
                <img
                    src={bossUrl}
                    alt="triglyph"
                    onClick={handleHit}
                    className={shudder ? "bf-shake" : ""}
                    style={{
                        position: "absolute",
                        bottom: "6%",
                        left: `${x * 100}%`,
                        transform: `translateX(-50%) translateY(${shudder ? (Math.random() * 12 - 6) : 0}px)`,
                        height: "50%",
                        cursor: frame === "forward" ? "pointer" : "default",
                        zIndex: 10,
                        transition: "left 0.12s linear, transform 0.06s ease",
                        filter: `${bossBaseFilter}${shudder ? " brightness(1.25)" : ""}`,
                        pointerEvents: "auto",
                    }}
                />
            ) : (
                <>
                    <img
                        src="/velinor/glyph_images/transcendance/transcendance_on_boss_chamber.gif"
                        alt="disintegrate"
                        style={{
                            position: "absolute",
                            bottom: "6%",
                            left: `${x * 100}%`,
                            transform: "translateX(-50%)",
                            height: "60%",
                            zIndex: 12,
                            pointerEvents: "none",
                            opacity: 1,
                        }}
                    />

                    {/* pulsing transcendance glyph center */}
                    <img
                        src="/velinor/glyph_images/transcendance/transcendance_pulse.gif"
                        alt="transcendance"
                        style={{
                            position: "absolute",
                            left: "50%",
                            top: "44%",
                            transform: "translate(-50%, -50%)",
                            width: "36%",
                            zIndex: 15,
                            pointerEvents: "none",
                            opacity: 1,
                            animation: "bf-pulse 1.6s ease-in-out infinite",
                        }}
                    />
                </>
            )}

            {/* small HUD */}
            <div style={{ position: "absolute", left: 12, top: 12, zIndex: 20, color: "#eee", fontSize: 14 }}>
                {defeated ? (
                    <span style={{ color: '#a3ffb5', fontWeight: 700 }}>Vanquished!</span>
                ) : (
                    <>Overlay: {(overlayFill * 100).toFixed(0)}% • Speed: {speedRef.current.toFixed(2)} • Hits: {hits}</>
                )}
            </div>
        </div>
    );
}
