import { Url } from "next/dist/shared/lib/router/router";
import Link from "next/link";

export default function Button({ href, className, children, ...props }: { href: Url, className: String, children: any }) {
  return (
  <Link href={href}
    className={`button-animation ${className}`}
    {...props}>
      {children}
  </Link>
  );
}