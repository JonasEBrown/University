'use client';

import { useRef, useEffect, useState, PointerEvent } from "react";

import { BubbleData } from "@/app/ui/components/Bubble";

let currentX: number = 0;
let currentY: number = 0;
let targetX: number = 0;
let targetY: number = 0;

export default function InteractiveBubble({ bubbleData }: { bubbleData: BubbleData }) {

    const bubble = useRef<HTMLDivElement>(null);
    const [ position, setPosition ] = useState({
        x: 0,
        y: 0,
    });

    const moveBubble = () => {
        setPosition({     
            x: position.x + ((targetX - position.x) / 20),
            y: position.y + ((targetY - position.y) / 20),
        });
        requestAnimationFrame(() => {
            moveBubble();
        });
    };

    const onMouseMove = (event: PointerEvent) => {
        targetX = event.clientX;
        targetY = event.clientY;
    };

    useEffect(moveBubble, []);

    return (
        <div ref={bubble} className="bubble" style={{
            // top: bubble.current ? `calc(-100% + var(--circle-size)/4)` : 0,
            // left: bubble.current ? `calc(-100% + var(--circle-size)/4)` : 0,
            // transform: `translate(${Math.round(position.x)}px, ${Math.round(position.y)}px)`,
            width: `${bubbleData.size}px`,
            backgroundImage: `radial-gradient(circle at center, color-mix(in srgb, ${bubbleData.color} 80%, transparent) 0, transparent 50%)`,
            transform: `translate(${Math.round(position.x)}px, ${Math.round(position.y)}px)`,
        }} onPointerMove={onMouseMove} />
    );
}