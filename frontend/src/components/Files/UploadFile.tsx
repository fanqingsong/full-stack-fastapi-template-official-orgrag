import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Upload as UploadIcon, Shield } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  file: z
    .instanceof(File, { message: "File is required" })
    .refine((file: File) => file.name && file.name.trim().length > 0, {
      message: "File name cannot be empty",
    }),
  responsible_function_id: z.string().uuid().optional(),
  visible_bu_id: z.string().uuid().optional(),
  visible_function_ids: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

const UploadFile = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      file: undefined,
      responsible_function_id: undefined,
      visible_bu_id: undefined,
      visible_function_ids: undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      const formData = new FormData()
      formData.append("file", data.file)

      // Add permission parameters as query params
      const params = new URLSearchParams()
      if (data.responsible_function_id) {
        params.append("responsible_function_id", data.responsible_function_id)
      }
      if (data.visible_bu_id) {
        params.append("visible_bu_id", data.visible_bu_id)
      }
      if (data.visible_function_ids) {
        params.append("visible_function_ids", data.visible_function_ids)
      }

      // Get authentication token
      const token = localStorage.getItem("access_token")
      // Use fetch directly to handle file upload
      const url = `/api/v1/files/upload${params.toString() ? "?" + params.toString() : ""}`
      const response = await fetch(url, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        // Clear token on authentication errors
        if (response.status === 401 || response.status === 403) {
          localStorage.removeItem("access_token")
          window.location.href = "/login"
        }
        throw new Error(error.detail || "Upload failed")
      }

      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("File uploaded successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      form.setValue("file", e.target.files[0], {
        shouldValidate: true,
        shouldDirty: true,
      })
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <UploadIcon className="mr-2" />
          Upload File
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Upload File</DialogTitle>
          <DialogDescription>
            Select a file to upload and configure access permissions.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="file"
                render={() => (
                  <FormItem>
                    <FormControl>
                      <Input
                        type="file"
                        onChange={handleFileChange}
                        disabled={mutation.isPending}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Permission Configuration Section */}
              <div className="border-t pt-4">
                <div className="flex items-center gap-2 mb-4">
                  <Shield className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">File Permissions (Optional)</h3>
                </div>

                <div className="grid gap-4">
                  <FormField
                    control={form.control}
                    name="responsible_function_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Responsible Function</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Which function uploaded this?" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {/* TODO: Load from API after client regeneration */}
                            <SelectItem value="placeholder">Select Function...</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="visible_bu_id"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Visible to Business Unit</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Which BU can view? (Optional)" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {/* TODO: Load from API after client regeneration */}
                            <SelectItem value="">All Users (Public)</SelectItem>
                            <SelectItem value="placeholder">Select BU...</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="visible_function_ids"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Visible to Functions</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Comma-separated function IDs (e.g., id1,id2,id3)"
                            className="resize-none"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </div>

            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  Cancel
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                Upload
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default UploadFile
