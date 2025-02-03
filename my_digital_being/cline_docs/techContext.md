# Tech Context

• Language and Framework:  
  - The system is primarily written in Python.  
  - Activities are structured using an async pattern (for example, see async functions in news fetching).

• Key Technologies and Dependencies:  
  - LinkupClient for external news fetching.  
  - Custom frameworks for activity management (e.g., ActivityBase, ActivityResult).  
  - Pylance for static analysis in VSCode.  

• Environment Setup:  
  - Dependencies installed typically via pip (e.g., pip install -r requirements.txt).  
  - .env file or environment variables store sensitive credentials like API keys.

• Constraints:  
  - Activities can be toggled in config/activity_constraints.json to manage memory usage or skill requirements.  
  - External integrations (like Twitter, GitHub) are currently optional and can be enabled or disabled depending on user needs.

• Development Workflow:  
  - Code changes revolve around enabling/disabling activities, adding new ones, or adjusting internal logic.  
  - Pylance is used to identify syntax and import issues in the codebase. Any missing references or leftover placeholders should be cleaned regularly to avoid persistent warnings.