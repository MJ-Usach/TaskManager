# Developer Task Manager

A modern, dark-themed Kanban like task management application built with Python and Tkinter. Organize your development work across multiple workflow stages with a clean and simple, intuitive interface.

## Features

- **5-Column Kanban Board**: Organize tasks into Pending, Done, Discoveries, In Revision, and Extras columns
- **Task Details**: Add detailed notes and descriptions to each task
- **Dark Mode UI**: Eye-friendly dark theme optimized for developers
- **CSV Import/Export**: Easily import and export tasks for data portability
- **Task Editing**: Inline editing and comprehensive task management
- **Persistent Storage**: Tasks are automatically saved to JSON format


### Requirements
- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup

1. Clone or download the repository:
```bash
git clone http://www.github.com/MJ-Usach/TaskManager
cd TaskManager
```

2. Run the application:
```bash
python task_manager.py
```

## Usage

### Adding Tasks
1. Click the **+ Add Task** button in any column
2. Enter your task description
3. Press Enter or click Save

### Editing Tasks
- **Single-click** a task to view and edit its details
- Add detailed notes in the Details section

### Moving Tasks Between Columns
1. Click a task to open the details dialog
2. Select a different column from the dropdown
3. Click **Save All** to move the task

### Deleting Tasks
1. Open task details (single-click)
2. Click **Delete Task** button
3. Confirm the deletion

### Exporting Tasks
- Click **📤 Export CSV** button
- Choose a location and filename
- Tasks will be saved as CSV with all details

### Importing Tasks
- Click **📥 Import CSV** button
- Select a CSV file
- Choose import mode:
  - **Append**: Add imported tasks to existing ones
  - **Replace**: Replace all existing tasks
- Optional: Skip duplicates or clear current data before import

## Data Storage

### tasks.json
Your tasks and details are stored in `tasks.json` with the following structure:
```json
{
  "tasks": {
    "Pending": ["Task 1", "Task 2"],
    "Done": ["Completed Task"],
    "Discoveries": [],
    "In Revision": [],
    "Extras": []
  },
  "details": {
    "Pending::Task 1": "Detailed notes about task 1",
    "Done::Completed Task": "Details here"
  }
}
```

## Keyboard Shortcuts

- **Enter**: Save task when adding or editing
- **Escape**: Close dialogs (via standard window controls)
- **Double-click**: Quick edit task name

## Color Scheme

- **Pending**: Red (#e85d75)
- **Done**: Green (#5fb878)
- **Discoveries**: Orange (#f9a825)
- **In Revision**: Blue (#42a5f5)
- **Extras**: Purple (#ab47bc)

## File Structure

```
TaskManager/
├── task_manager.py          # Main application
├── tasks.json               # Task data (auto-created)
└── README.md                # This file
```

## Troubleshooting

### Tasks not saving
- Ensure you have write permissions in the application directory
- Check that `tasks.json` is not corrupted

### CSV import issues
- Verify CSV format: Column, Task, Details (3 columns)
- Ensure valid column names: Pending, Done, Discoveries, In Revision, Extras

### UI rendering issues
- Try resizing the window
- Restart the application if scrollbars appear unresponsive

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3).

**License summary:**
- You may use, modify, and share this code, including for commercial purposes.
- If you modify and deploy this code (or a derivative) for users over a network (e.g., as a web service), you must also make your modified source code available to those users under the same license.
- See the LICENSE file for full terms.

## Contributing

Contributions are welcome! Feel free to submit issues and enhancement requests.
If you have a suggestion or feature you want to add let me know!. 

## Future Enhancements

- Drag-and-drop task reordering
- Task priorities and due dates
- Dark/Light theme toggle
- Search and filter functionality
- Backup and restore features
- Priority Flag
- Custom Columns