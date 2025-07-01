class TaskManagement:
    """Task management API"""
    def __init__(self):
        self.tasks = {
            "task_name": [],
            "status": []
        }
    def create_task(self, task_name: str) -> str:
        """Create a task"""
        self.tasks["task_name"].append(task_name)
        self.tasks["status"].append("pending")
        return "task created"
    def update_task(self, task_name: str) -> str:
        """Update a task"""
        self.tasks["status"][self.tasks["task_name"].index(task_name)] = "done"
        return "updated"
    def get_task(self, task: str) -> str:
        """Get a task"""
        print(f"Task: {self.tasks["task_name"]}, Status: {self.tasks["status"]}")
        return "task"
    def delete_task(self, task: str) -> str:
        """Delete a task"""
        return "task deleted"
TaskManagement = TaskManagement()
TaskManagement.create_task("Do homework")
TaskManagement.update_task("Do homework")
TaskManagement.get_task("Do homework")
