import { useState } from "react";
import { useParams } from "next/navigation";
import { Plus } from "lucide-react";
// plane imports
import { Button } from "@plane/ui";
// hooks
import { useAppRouter } from "@/hooks/use-app-router";
// services
import { ProjectService } from "@/services/project/project.service";
import { ProjectPageService } from "@/services/page/project-page.service";

const projectService = new ProjectService();
const pageService = new ProjectPageService();

export function NewPageButton() {
  const { workspaceSlug } = useParams();
  const router = useAppRouter();
  const [creating, setCreating] = useState(false);

  const create = async () => {
    if (!workspaceSlug || creating) return;
    setCreating(true);
    try {
      const projects = await projectService.getWorkspaceProjects(workspaceSlug as string);
      const projectId = projects?.[0]?.id;
      if (!projectId) return;
      const page = await pageService.create(workspaceSlug as string, projectId, { name: "Untitled" });
      router.push(`/${workspaceSlug}/projects/${projectId}/pages/${page.id}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <Button variant="accent-primary" size="sm" onClick={create} disabled={creating}>
      <Plus className="h-3.5 w-3.5" />
      {creating ? "Creating..." : "New page"}
    </Button>
  );
}