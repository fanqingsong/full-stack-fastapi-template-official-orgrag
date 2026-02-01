import { createFileRoute } from "@tanstack/react-router"

import BusinessUnits from "@/components/Organization/BusinessUnits"
import Functions from "@/components/Organization/Functions"

export const Route = createFileRoute("/_layout/organization")({
  component: Organization,
  head: () => ({
    meta: [
      {
        title: "Organization - FastAPI Cloud",
      },
    ],
  }),
})

function Organization() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Organization Management</h1>
        <p className="text-muted-foreground">
          Manage business units and functional roles
        </p>
      </div>

      <div className="grid gap-6">
        <BusinessUnits />
        <Functions />
      </div>
    </div>
  )
}
