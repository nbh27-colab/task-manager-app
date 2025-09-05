# streamlit_app/app.py

import streamlit as st
import requests
from datetime import datetime, date
import json

# --- Configuration ---
FASTAPI_BASE_URL = "http://127.0.0.1:8000" # Ensure your FastAPI is running here

# --- Helper Functions for API Calls ---

def get_headers(token: str = None):
    """Returns headers for API requests, including Authorization if a token is provided."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def register_user(email, password):
    """Calls the FastAPI /users/register endpoint."""
    response = requests.post(
        f"{FASTAPI_BASE_URL}/users/register",
        json={"email": email, "password": password}
    )
    return response.json(), response.status_code

def login_user(email, password):
    """Calls the FastAPI /users/token endpoint for user login."""
    # FastAPI's /token endpoint expects x-www-form-urlencoded, not JSON
    response = requests.post(
        f"{FASTAPI_BASE_URL}/users/token",
        data={"username": email, "password": password}
    )
    return response.json(), response.status_code

def get_tasks(token: str, skip: int = 0, limit: int = 100):
    """Fetches tasks for the current user."""
    response = requests.get(
        f"{FASTAPI_BASE_URL}/tasks/",
        headers=get_headers(token),
        params={"skip": skip, "limit": limit}
    )
    return response.json(), response.status_code

def create_task(token: str, task_data: dict):
    """Creates a new task."""
    response = requests.post(
        f"{FASTAPI_BASE_URL}/tasks/",
        headers=get_headers(token),
        json=task_data
    )
    return response.json(), response.status_code

def update_task(token: str, task_id: int, task_data: dict):
    """Updates an existing task."""
    response = requests.put(
        f"{FASTAPI_BASE_URL}/tasks/{task_id}",
        headers=get_headers(token),
        json=task_data
    )
    return response.json(), response.status_code

def delete_task(token: str, task_id: int):
    """Deletes a task."""
    response = requests.delete(
        f"{FASTAPI_BASE_URL}/tasks/{task_id}",
        headers=get_headers(token)
    )
    return response.status_code

def get_projects(token: str):
    """Fetches projects for the current user."""
    response = requests.get(
        f"{FASTAPI_BASE_URL}/projects/",
        headers=get_headers(token)
    )
    return response.json(), response.status_code

def get_categories(token: str):
    """Fetches categories for the current user."""
    response = requests.get(
        f"{FASTAPI_BASE_URL}/categories/",
        headers=get_headers(token)
    )
    return response.json(), response.status_code

def get_ai_suggestions(token: str, title: str, description: str):
    """Requests AI suggestions for a task."""
    response = requests.post(
        f"{FASTAPI_BASE_URL}/tasks/suggest",
        headers=get_headers(token),
        json={"title": title, "description": description}
    )
    return response.json(), response.status_code

def estimate_task_time(token: str, task_data: dict):
    """Requests AI time estimation for a task."""
    response = requests.post(
        f"{FASTAPI_BASE_URL}/tasks/estimate",
        headers=get_headers(token),
        json=task_data
    )
    return response.json(), response.status_code

def chat_with_agent(token: str, message: str, chat_history: list):
    """Sends a message to the AI agent and gets a response."""
    payload = {
        "message": message,
        "chat_history": chat_history # Pass the full chat history
    }
    response = requests.post(
        f"{FASTAPI_BASE_URL}/agent/chat",
        headers=get_headers(token),
        json=payload
    )
    return response.json(), response.status_code

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Intelligent Task Management App")

st.title("Intelligent Task Management Application")

# Session state for login and tasks
if "token" not in st.session_state:
    st.session_state.token = None
if "current_user_email" not in st.session_state:
    st.session_state.current_user_email = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "projects" not in st.session_state:
    st.session_state.projects = []
if "categories" not in st.session_state:
    st.session_state.categories = []
# Initialize AI-related suggestions in session state
if 'suggested_category_id' not in st.session_state:
    st.session_state.suggested_category_id = None
if 'suggested_project_id' not in st.session_state:
    st.session_state.suggested_project_id = None
if 'suggested_tags' not in st.session_state:
    st.session_state.suggested_tags = ""
if 'suggested_priority' not in st.session_state:
    st.session_state.suggested_priority = 5
if 'suggested_urgency' not in st.session_state:
    st.session_state.suggested_urgency = None
if 'suggested_importance' not in st.session_state:
    st.session_state.suggested_importance = None
if 'ai_estimated_time' not in st.session_state:
    st.session_state.ai_estimated_time = None
if 'ai_confidence' not in st.session_state:
    st.session_state.ai_confidence = None


# --- Authentication Section ---
if st.session_state.token is None:
    st.header("Login / Register")
    auth_tab = st.tabs(["Login", "Register"])

    with auth_tab[0]:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            if submitted:
                response_data, status_code = login_user(email, password)
                if status_code == 200:
                    st.session_state.token = response_data["access_token"]
                    st.session_state.current_user_email = email
                    st.success("Login successful!")
                    st.rerun() # Rerun to show main app
                else:
                    st.error(f"Login failed: {response_data.get('detail', 'Unknown error')}")

    with auth_tab[1]:
        with st.form("register_form"):
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Register")
            if submitted:
                response_data, status_code = register_user(email, password)
                if status_code == 201:
                    st.success(f"Registration successful for {response_data['email']}! You can now log in.")
                else:
                    st.error(f"Registration failed: {response_data.get('detail', 'Unknown error')}")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.current_user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.current_user_email = None
        st.session_state.chat_history = []
        st.session_state.projects = []
        st.session_state.categories = []
        # Clear AI related session state on logout
        st.session_state.suggested_category_id = None
        st.session_state.suggested_project_id = None
        st.session_state.suggested_tags = ""
        st.session_state.suggested_priority = 5
        st.session_state.suggested_urgency = None
        st.session_state.suggested_importance = None
        st.session_state.ai_estimated_time = None
        st.session_state.ai_confidence = None
        st.rerun()

    # --- Main App Tabs ---
    app_tabs = st.tabs(["Task List", "Create Task", "Update Task", "AI Agent / Chat", "Manage Projects/Categories"])

    # Fetch projects and categories once logged in
    if not st.session_state.projects:
        projects_data, status_code = get_projects(st.session_state.token)
        if status_code == 200:
            st.session_state.projects = projects_data
        else:
            st.error(f"Could not load projects: {projects_data.get('detail', 'Unknown error')}")
    
    if not st.session_state.categories:
        categories_data, status_code = get_categories(st.session_state.token)
        if status_code == 200:
            st.session_state.categories = categories_data
        else:
            st.error(f"Could not load categories: {categories_data.get('detail', 'Unknown error')}")

    # Create dictionaries for easy lookup of project/category IDs by name
    project_options = {p['name']: p['id'] for p in st.session_state.projects}
    category_options = {c['name']: c['id'] for c in st.session_state.categories}
    
    # --- Tab 1: List Tasks ---
    with app_tabs[0]:
        st.header("Your Task List")
        if st.button("Refresh Tasks"):
            pass # Rerun will re-fetch
        
        tasks_data, status_code = get_tasks(st.session_state.token)
        if status_code == 200:
            if tasks_data:
                for task in tasks_data:
                    st.markdown(f"### 📄 {task['title']}")
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Priority:** {task['priority']}")
                    st.write(f"**Deadline:** {task['deadline'].split('T')[0] if task['deadline'] else 'N/A'}")
                    project_name = next((p['name'] for p in st.session_state.projects if p['id'] == task['project_id']), 'N/A')
                    category_name = next((c['name'] for c in st.session_state.categories if c['id'] == task['category_id']), 'N/A')
                    st.write(f"**Project:** {project_name}")
                    st.write(f"**Category:** {category_name}")
                    if task.get('ai_estimated_time_hours'):
                        st.write(f"**AI Estimated:** {task['ai_estimated_time_hours']:.2f} hours")
                    st.markdown("---")
            else:
                st.info("You don't have any tasks yet. Go create one!")
        else:
            st.error(f"Could not load tasks: {tasks_data.get('detail', 'Unknown error')}")

    # --- Tab 2: Create Task ---
    with app_tabs[1]:
        st.header("Create New Task")

        # Input fields for task creation, outside the form for AI buttons
        # Use session state to store temporary inputs for AI buttons
        new_title = st.text_input("Task Title", key="new_title_input")
        new_description = st.text_area("Description", key="new_description_input")

        col_ai_buttons_1, col_ai_buttons_2 = st.columns(2)
        with col_ai_buttons_1:
            if st.button("Get AI Suggestions", key="ai_suggest_btn"):
                if new_title:
                    suggestions, status_code = get_ai_suggestions(st.session_state.token, new_title, new_description)
                    if status_code == 200:
                        st.session_state.suggested_category_id = suggestions.get('category_id')
                        st.session_state.suggested_project_id = suggestions.get('project_id')
                        st.session_state.suggested_tags = suggestions.get('tags', '')
                        st.session_state.suggested_priority = suggestions.get('priority', 5)
                        st.session_state.suggested_urgency = suggestions.get('urgency_score')
                        st.session_state.suggested_importance = suggestions.get('importance_score')
                        st.success("Received suggestions from AI!")
                    else:
                        st.error(f"Error getting AI suggestions: {suggestions.get('detail', 'Unknown error')}")
                else:
                    st.warning("Please enter a task title to get suggestions.")
        
        with col_ai_buttons_2:
            if st.button("Estimate Time with AI", key="ai_estimate_btn"):
                if new_title:
                    task_for_estimation = {
                        "title": new_title,
                        "description": new_description,
                        "project_id": st.session_state.suggested_project_id, # Use suggested if available
                        "category_id": st.session_state.suggested_category_id, # Use suggested if available
                        "priority": st.session_state.suggested_priority, # Use suggested if available
                        "tags": st.session_state.suggested_tags, # Use suggested if available
                        "deadline": None # Deadline is not required for estimation
                    }
                    estimation, status_code = estimate_task_time(st.session_state.token, task_for_estimation)
                    if status_code == 200:
                        st.session_state.ai_estimated_time = estimation['ai_estimated_time_hours']
                        st.session_state.ai_confidence = estimation['confidence_score']
                        st.success(f"AI estimated completion time: {st.session_state.ai_estimated_time:.2f} hours (Confidence: {st.session_state.ai_confidence:.2f})")
                    else:
                        st.error(f"Error estimating time: {estimation.get('detail', 'Unknown error')}")
                else:
                    st.warning("Please enter a task title to estimate time.")

        # Display AI suggestions/estimations
        if st.session_state.suggested_category_id is not None:
            st.write(f"**Suggested Category:** {next((c['name'] for c in st.session_state.categories if c['id'] == st.session_state.suggested_category_id), 'N/A')}")
        if st.session_state.suggested_project_id is not None:
            st.write(f"**Suggested Project:** {next((p['name'] for p in st.session_state.projects if p['id'] == st.session_state.suggested_project_id), 'N/A')}")
        if st.session_state.suggested_tags:
            st.write(f"**Suggested Tags:** {st.session_state.suggested_tags}")
        if st.session_state.suggested_priority:
            st.write(f"**Suggested Priority:** {st.session_state.suggested_priority}")
        if st.session_state.suggested_urgency is not None:
            st.write(f"**Suggested Urgency:** {st.session_state.suggested_urgency:.2f}")
        if st.session_state.suggested_importance is not None:
            st.write(f"**Suggested Importance:** {st.session_state.suggested_importance:.2f}")
        if st.session_state.ai_estimated_time is not None:
            st.write(f"**AI Estimated Time:** {st.session_state.ai_estimated_time:.2f} hours")
        if st.session_state.ai_confidence is not None:
            st.write(f"**AI Confidence:** {st.session_state.ai_confidence:.2f}")

        # Task creation form, using the inputs from above and potentially suggestions
        with st.form("create_task_form"):
            # Use the values from text_input/textarea (new_title, new_description) as initial values
            # for form elements, allowing them to be overridden or confirmed by the user.
            # Make sure to use different keys for form elements than the ones outside.
            form_title = st.text_input("Task Title (Confirm/Edit)", value=new_title, key="form_title")
            form_description = st.text_area("Description (Confirm/Edit)", value=new_description, key="form_description")
            
            # Apply suggestions if available for initial selectbox value
            default_category_name = ""
            if st.session_state.suggested_category_id:
                for cat in st.session_state.categories:
                    if cat['id'] == st.session_state.suggested_category_id:
                        default_category_name = cat['name']
                        break
            
            # Find the index of the default category name in the options list
            category_options_list = [""] + list(category_options.keys())
            default_category_index = 0
            if default_category_name in category_options_list:
                default_category_index = category_options_list.index(default_category_name)

            selected_category_name = st.selectbox(
                "Category",
                options=category_options_list,
                index=default_category_index,
                key="form_category"
            )
            form_category_id = category_options.get(selected_category_name) if selected_category_name else None

            default_project_name = ""
            if st.session_state.suggested_project_id:
                for proj in st.session_state.projects:
                    if proj['id'] == st.session_state.suggested_project_id:
                        default_project_name = proj['name']
                        break

            project_options_list = [""] + list(project_options.keys())
            default_project_index = 0
            if default_project_name in project_options_list:
                default_project_index = project_options_list.index(default_project_name)

            selected_project_name = st.selectbox(
                "Project",
                options=project_options_list,
                index=default_project_index,
                key="form_project"
            )
            form_project_id = project_options.get(selected_project_name) if selected_project_name else None
            
            form_priority = st.slider("Priority", 1, 10, value=st.session_state.get('suggested_priority', 5), key="form_priority")
            form_deadline_str = st.date_input("Deadline", value=None, key="form_deadline")
            form_tags = st.text_input("Tags (comma-separated)", value=st.session_state.get('suggested_tags', ''), key="form_tags")

            submitted_create = st.form_submit_button("Create Task")
            if submitted_create:
                task_data = {
                    "title": form_title,
                    "description": form_description,
                    "status": "To Do", # New tasks start as To Do
                    "deadline": str(form_deadline_str) + "T00:00:00Z" if form_deadline_str else None, # Format for ISO 8601
                    "project_id": form_project_id,
                    "category_id": form_category_id,
                    "initial_estimated_time_hours": st.session_state.get('ai_estimated_time', None), # Use AI estimate if available
                    "tags": form_tags,
                    "priority": form_priority,
                    "urgency_score": st.session_state.get('suggested_urgency', None),
                    "importance_score": st.session_state.get('suggested_importance', None)
                }
                response_data, status_code = create_task(st.session_state.token, task_data)
                if status_code == 201:
                    st.success(f"Task '{response_data['title']}' created successfully!")
                    # Clear suggestions and estimates from session state after creation
                    for key in ['suggested_category_id', 'suggested_project_id', 'suggested_tags', 
                                'suggested_priority', 'suggested_urgency', 'suggested_importance', 
                                'ai_estimated_time', 'ai_confidence']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun() # Rerun to refresh task list
                else:
                    st.error(f"Error creating task: {response_data.get('detail', 'Unknown error')}")

    # --- Tab 3: Update Task ---
    with app_tabs[2]:
        st.header("Update / Complete / Delete Task")
        
        tasks_to_update, status_code = get_tasks(st.session_state.token)
        if status_code == 200 and tasks_to_update:
            # Create a dictionary for selectbox: display_name -> task_id
            task_titles = {f"{task['id']} - {task['title']} ({task['status']})": task['id'] for task in tasks_to_update}
            selected_task_display = st.selectbox(
                "Select task to update/delete",
                options=list(task_titles.keys()),
                key="select_update_task"
            )
            selected_task_id = task_titles.get(selected_task_display)

            if selected_task_id:
                current_task = next((t for t in tasks_to_update if t['id'] == selected_task_id), None)
                if current_task:
                    with st.form(f"update_task_form_{selected_task_id}"):
                        st.subheader(f"Updating Task: {current_task['title']}")
                        
                        update_title = st.text_input("Title", value=current_task['title'], key=f"update_title_{selected_task_id}")
                        update_description = st.text_area("Description", value=current_task['description'], key=f"update_description_{selected_task_id}")
                        
                        # Populate current project and category for selectbox
                        current_project_name = next((p['name'] for p in st.session_state.projects if p['id'] == current_task['project_id']), "")
                        selected_project_for_update = st.selectbox(
                            "Project",
                            options=[""] + list(project_options.keys()),
                            index=list(project_options.keys()).index(current_project_name) + 1 if current_project_name else 0,
                            key=f"update_project_{selected_task_id}"
                        )
                        update_project_id = project_options.get(selected_project_for_update) if selected_project_for_update else None

                        current_category_name = next((c['name'] for c in st.session_state.categories if c['id'] == current_task['category_id']), "")
                        selected_category_for_update = st.selectbox(
                            "Category",
                            options=[""] + list(category_options.keys()),
                            index=list(category_options.keys()).index(current_category_name) + 1 if current_category_name else 0,
                            key=f"update_category_{selected_task_id}"
                        )
                        update_category_id = category_options.get(selected_category_for_update) if selected_category_for_update else None
                        
                        update_priority = st.slider("Priority", 1, 10, value=current_task['priority'], key=f"update_priority_{selected_task_id}")
                        
                        # Handle datetime for deadline input (convert ISO string to date object)
                        current_deadline = None
                        if current_task['deadline']:
                            try:
                                current_deadline = datetime.fromisoformat(current_task['deadline'].replace('Z', '+00:00')).date()
                            except ValueError:
                                current_deadline = None # Fallback if format is unexpected
                        update_deadline = st.date_input("Deadline", value=current_deadline, key=f"update_deadline_{selected_task_id}")
                        
                        update_tags = st.text_input("Tags (comma-separated)", value=current_task['tags'] or "", key=f"update_tags_{selected_task_id}")
                        
                        # Status dropdown (must match TaskStatusEnum in schemas)
                        status_options = ["To Do", "In Progress", "Done", "On Hold", "Cancelled", "Blocked"]
                        current_status_index = status_options.index(current_task['status']) if current_task['status'] in status_options else 0
                        update_status = st.selectbox("Status", options=status_options, index=current_status_index, key=f"update_status_{selected_task_id}")

                        col_update_btn, col_delete_btn = st.columns(2)
                        with col_update_btn:
                            submitted_update = st.form_submit_button("Update Task")
                        with col_delete_btn:
                            submitted_delete = st.form_submit_button("Delete Task", type="secondary")

                        if submitted_update:
                            task_data_to_update = {
                                "title": update_title,
                                "description": update_description,
                                "status": update_status,
                                "deadline": str(update_deadline) + "T00:00:00Z" if update_deadline else None, # Format for ISO 8601
                                "project_id": update_project_id,
                                "category_id": update_category_id,
                                "priority": update_priority,
                                "tags": update_tags
                            }
                            response_data, status_code = update_task(st.session_state.token, selected_task_id, task_data_to_update)
                            if status_code == 200:
                                st.success(f"Task '{response_data['title']}' updated successfully!")
                                st.rerun() # Rerun to refresh task list
                            else:
                                st.error(f"Error updating task: {response_data.get('detail', 'Unknown error')}")
                        
                        if submitted_delete:
                            # Add a simple confirmation for deletion
                            # Streamlit button itself is a trigger. We don't need a separate confirmation dialog here.
                            # The user has to click the delete button to initiate.
                            status_code = delete_task(st.session_state.token, selected_task_id)
                            if status_code == 204: # 204 No Content for successful deletion
                                st.success(f"Task ID {selected_task_id} deleted.")
                                st.rerun() # Rerun to refresh task list
                            else:
                                st.error(f"Error deleting task: {status_code}") # No JSON response for 204
                else:
                    st.info("Select a task from the list above to view details and update.")
            else:
                st.info("No tasks available to update or delete.")

    # --- Tab 4: AI Agent Chat ---
    with app_tabs[3]:
        st.header("AI Agent Chat")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["type"] == "human":
                st.chat_message("user").write(msg["content"])
            elif msg["type"] == "ai":
                st.chat_message("ai").write(msg["content"])

        user_input = st.chat_input("Type your message...", key="chat_input")

        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"type": "human", "content": user_input})
            st.chat_message("user").write(user_input)

            # Call AI agent
            with st.spinner("AI is thinking..."):
                # Pass current chat history to agent for context
                response_data, status_code = chat_with_agent(st.session_state.token, user_input, st.session_state.chat_history)
                
                if status_code == 200:
                    ai_response = response_data.get("response", "No response from AI.")
                    st.session_state.chat_history.append({"type": "ai", "content": ai_response})
                    st.chat_message("ai").write(ai_response)
                else:
                    error_message = response_data.get("detail", "Unknown error from AI Agent.")
                    st.error(f"AI Agent Error: {error_message}")
                    st.session_state.chat_history.append({"type": "ai", "content": f"Sorry, an error occurred: {error_message}"})

    # --- Tab 5: Manage Projects/Categories ---
    with app_tabs[4]:
        st.header("Manage Projects and Categories")

        st.subheader("Your Projects")
        if st.session_state.projects:
            for proj in st.session_state.projects:
                st.write(f"- **{proj['name']}**: {proj['description'] or 'No description'}")
        else:
            st.info("No projects yet.")
        # Future: Add forms to create/update/delete projects

        st.subheader("Your Categories")
        if st.session_state.categories:
            for cat in st.session_state.categories:
                st.write(f"- **{cat['name']}**")
        else:
            st.info("No categories yet.")
        # Future: Add forms to create/update/delete categories