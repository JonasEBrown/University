import { getServerSession } from 'next-auth'
import { authOptions } from '@/src/lib/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <h1 className="text-2xl font-bold">
        Welcome, {session.user?.name || session.user?.email}!
      </h1>
    </div>
  )
}
