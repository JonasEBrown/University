import Link from "next/link";
import Image from "next/image";

export default function Navigation() {
    return (
        <div className="bg-transparent text-white px-6 py-6 font-sans w-screen">
            <header className="bg-transparent flex justify-between items-center">
                <Link href="/" className="flex justify-between space-x-2 items-center">
                    <Image src="/Portfolio/favicon.ico" alt="logo" className="aspect-square w-12" width={100} height={100} />
                    <p className="pl-2 text-2xl font-bold">PORTFOLIO</p>
                </Link>
                <nav className="space-x-6">
                    <Link href="/coursework" className="underline-animation">Coursework</Link>
                    <Link href="/projects" className="underline-animation">Projects</Link>
                </nav>
            </header>
        </div>
        
    );
}