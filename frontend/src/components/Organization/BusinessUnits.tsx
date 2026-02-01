import { useSuspenseQuery } from "@tanstack/react-query"
import { Building2 } from "lucide-react"
import { Suspense } from "react"

import { BusinessUnitsService } from "@/client"
import AddBusinessUnit from "@/components/Organization/AddBusinessUnit"
import { DataTable } from "@/components/Common/DataTable"
import PendingItems from "@/components/Pending/PendingItems"
import { businessUnitColumns } from "@/components/Organization/businessUnitColumns"

function getBusinessUnitsQueryOptions() {
  return {
    queryFn: async () => {
      return await BusinessUnitsService.readBusinessUnits({
        skip: 0,
        limit: 100,
      })
    },
    queryKey: ["business-units"],
  }
}

function BusinessUnitsTableContent() {
  const { data: businessUnits } = useSuspenseQuery(getBusinessUnitsQueryOptions())

  if (businessUnits.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Building2 className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No business units yet</h3>
        <p className="text-muted-foreground">Create a business unit to get started</p>
      </div>
    )
  }

  return <DataTable columns={businessUnitColumns} data={businessUnits.data} />
}

function BusinessUnitsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <BusinessUnitsTableContent />
    </Suspense>
  )
}

export default function BusinessUnits() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Business Units</h2>
          <p className="text-sm text-muted-foreground">
            Manage business units (业务单元)
          </p>
        </div>
        <AddBusinessUnit />
      </div>
      <BusinessUnitsTable />
    </div>
  )
}
