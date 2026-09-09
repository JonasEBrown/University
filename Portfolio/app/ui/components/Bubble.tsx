export interface Vector2 {
    x: number,
    y: number,
};

export interface BubbleData {
    position: Vector2,
    velocity: Vector2,
    size: number,
    color: string,
    id: number,
};

export function Bubble({ bubble, ...props }: { bubble: BubbleData }) {
    return (
        <div className={`bubble`} style={{
            // top: `-100% + ${bubble.size / 4}`,
            // left: `-100% + ${bubble.size / 4}`,
            // top: `${Math.round(bubble.position.x)}px`,
            // left: `${Math.round(bubble.position.y)}px`,
            width: `${bubble.size}px`,
            backgroundImage: `radial-gradient(circle at center, color-mix(in srgb, ${bubble.color} 80%, transparent) 0, transparent 50%)`,
            //    bg-radial from-[rgba(var(--color-interactive),0.8)] to-50% to-[rba(var(--color-interactive),0)]
            transform: `translate(${Math.round(bubble.position.x)}px, ${Math.round(bubble.position.y)}px)`,
        }} {...props} />
    );
}