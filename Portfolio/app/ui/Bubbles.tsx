'use client';

import { useRef, useMemo, useState, useEffect, useCallback } from "react";

import useWindowDimensions from "@/app/utils/useWindowDimensions";

import { Bubble, BubbleData } from "@/app/ui/components/Bubble";
import InteractiveBubble from "@/app/ui/components/InteractiveBubble";

function mulberry32(seed: number) {
  return function () {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export default function Bubbles({ children }: { children: React.ReactNode }) {
    const windowDimensions = useWindowDimensions();

    const rng = useMemo(() => mulberry32(Math.floor(Math.random() * 0xfffffffff)), []);

    const [bubbles, setBubbles] = useState<BubbleData[]>(() =>
        Array.from({ length: 20 }, (_, i) => ({
            id: i,
            position: {
                x: rng() * windowDimensions.width,
                y: rng() * windowDimensions.height,
            },
            velocity: {
                x: rng() * 5,
                y: rng() * 5,
            },
            size: rng() * windowDimensions.width,
            color: `rgb(${Math.floor(rng() * 255)},${Math.floor(rng() * 255)},${Math.floor(rng() * 255)})`,
        })
    ));

    const lastTick = useRef(Date.now());
    const [ , updateState ] = useState({});
    const forceUpdate = useCallback(() => updateState({}), []);

    useEffect(() => {
        setInterval(() => {
            const tick = Date.now();
            const deltaTime: number = (tick - lastTick.current) / 1000;
            lastTick.current = tick;
    
            bubbles.forEach((bubble, index) => {    
                bubble.position.x = bubble.position.x + (bubble.velocity.x * deltaTime);
                bubble.position.y = bubble.position.y + (bubble.velocity.y * deltaTime);
                
                if ((bubble.position.x < 0) || (bubble.position.x > windowDimensions.width)) bubble.velocity.x *= -1;
                if ((bubble.position.y < 0) || (bubble.position.y > windowDimensions.height)) bubble.velocity.y *= -1;

                bubbles[index] = bubble;
                setBubbles(bubbles);
            });
        }, 1000);
    }, [ forceUpdate, bubbles, windowDimensions ]);

    return (
        <div className="gradient-background">
            {/* <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
            <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" /> */}
            {/* <div className="g1" />
            <div className="g2" />
            <div className="g3" />
            <div className="g4" />
            <div className="g5" /> */}
            {/* <InteractiveBubble bubbleData={} /> */}

            {
                bubbles.map((bubble, index) => {
                    return <Bubble key={index} bubble={bubble} />
                })
            }

            {children}
        </div>
    );
}