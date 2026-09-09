"use client";

import { signIn } from "next-auth/react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import Card from "@/src/components/ui/Card";

export default function LoginPage() {
	// const router = useRouter()
	// const searchParams = useSearchParams()
	// const callbackUrl = searchParams.get('callbackUrl') || '/'

	// const [email, setEmail] = useState('')
	// const [password, setPassword] = useState('')
	// const [error, setError] = useState('')

	// const handleSubmit = async (e: React.FormEvent) => {
	//   e.preventDefault()

	//   const res = await signIn('credentials', {
	//     redirect: false,
	//     email,
	//     password,
	//     callbackUrl,
	//   })

	//   if (res?.error) {
	//     setError('Invalid email or password')
	//   } else {
	//     router.push(callbackUrl)
	//   }
	// }

	return (
		<div className="flex items-center justify-center h-screen">
			<form>
				<Card>create login form</Card>
			</form>
		</div>
		// <div className="min-h-screen flex items-center justify-center">
		//   <form
		//     onSubmit={handleSubmit}
		//     className="p-8 rounded shadow-md w-full max-w-sm"
		//   >
		//     <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>

		//     {error && (
		//       <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
		//     )}

		//     <div className="mb-4">
		//       <label className="block text-sm font-medium text-gray-700">
		//         Email
		//       </label>
		//       <input
		//         type="email"
		//         required
		//         value={email}
		//         onChange={(e) => setEmail(e.target.value)}
		//         className="mt-1 px-3 py-2 border rounded w-full"
		//       />
		//     </div>

		//     <div className="mb-6">
		//       <label className="block text-sm font-medium text-gray-700">
		//         Password
		//       </label>
		//       <input
		//         type="password"
		//         required
		//         value={password}
		//         onChange={(e) => setPassword(e.target.value)}
		//         className="mt-1 px-3 py-2 border rounded w-full"
		//       />
		//     </div>

		//     <button
		//       type="submit"
		//       className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
		//     >
		//       Sign In
		//     </button>
		//   </form>
		// </div>
	);
}
