import { useSuspenseQuery } from "@tanstack/react-query"
import { Users } from "lucide-react"
import { Suspense } from "react"

import { FunctionsService } from "@/client"
import AddFunction from "@/components/Organization/AddFunction"
import PendingItems from "@/components/Pending/PendingItems"

function getFunctionsQueryOptions() {
  return {
    queryFn: async () => {
      return await FunctionsService.readFunctions({ skip: 0, limit: 100 })
    },
    queryKey: ["functions"],
  }
}

function FunctionsTableContent() {
  const { data: functions } = useSuspenseQuery(getFunctionsQueryOptions())

  if (functions.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Users className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No functions yet</h3>
        <p className="text-muted-foreground">Create a function to get started</p>
      </div>
    )
  }

  return (
    <div className="border rounded-lg">
      <table className="w-full">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="p-3 text-left text-sm font-medium">Name</th>
            <th className="p-3 text-left text-sm font-medium">Code</th>
            <th className="p-3 text-left text-sm font-medium">Business Unit</th>
            <th className="p-3 text-left text-sm font-medium">Description</th>
            <th className="p-3 text-left text-sm font-medium">Active</th>
          </tr>
        </thead>
        <tbody>
          {functions.data.map((func) => (
            <tr key={func.id} className="border-b hover:bg-muted/30">
              <td className="p-3 text-sm">{func.name}</td>
              <td className="p-3 text-sm font-mono">{func.code}</td>
              <td className="p-3 text-sm">{func.business_unit_id}</td>
              <td className="p-3 text-sm text-muted-foreground">
                {func.description || "-"}
              </td>
              <td className="p-3 text-sm">
                {func.is_active ? (
                  <span className="text-green-600">Yes</span>
                ) : (
                  <span className="text-red-600">No</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function FunctionsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <FunctionsTableContent />
    </Suspense>
  )
}

function Functions() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Functions</h2>
          <p className="text-sm text-muted-foreground">
            Manage functional roles (职能角色)
          </p>
        </div>
        <AddFunction />
      </div>
      <FunctionsTable />
    </div>
  )
}

export default Functions
