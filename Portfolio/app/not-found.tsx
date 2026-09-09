import Button from "@/app/ui/components/Button";
 
export default function NotFound() {
  return (
    <div className="h-screen content-center justify-items-center">
      <div className="flex justify-between items-center space-x-7">
        <h1 className="text-[24px] font-semibold border-r-1 border-white/40 px-6 py-[0.35em]">404</h1>
        <p className="text-base">This page could not be found.</p>
      </div>
      <div className="flex items-center m-8">
        <Button href="/" className="">
          Back to safety
        </Button>
      </div>
    </div>
  )
}