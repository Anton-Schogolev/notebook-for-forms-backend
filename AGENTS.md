# Development workflow

For trivial changes or questions, handle the task directly.

For substantive implementation tasks, use the delegated workflow below
by default. If the user asks for direct work, solo work, or no subagents,
use the direct workflow instead. Keep the selected workflow for the
current task unless the user changes it.

## Direct workflow

The top-level agent performs all work itself. Do not spawn subagents.

1. Inspect relevant code and define the approach, acceptance criteria,
   and validation steps.
2. Present the plan and wait for explicit approval before implementation,
   unless the user explicitly authorizes proceeding without approval
   after planning. Selecting direct work alone does not waive this pause.
3. Edit files, run appropriate validation, review the changes yourself,
   and correct any issues.
4. Summarize the changes, validation results, and unresolved issues.

## Delegated workflow

1. Act as planner and coordinator. Inspect relevant code and define
   the approach, acceptance criteria, and validation steps.
2. Present the plan to the user and wait for their explicit go-ahead
   before delegating to the coder or starting implementation. Skip this
   pause only when the user explicitly authorizes proceeding without
   approval after planning. Silence or elapsed time is not approval.
3. After approval, delegate implementation to the coder agent. Provide
   the original requirements, plan, acceptance criteria, and relevant
   constraints.
4. Wait for implementation and validation to finish.
5. Delegate review to the reviewer agent. Provide the requirements,
   acceptance criteria, changed files, and validation results.
6. Send actionable review findings to the coder for correction,
   then have the reviewer check the updated changes.
7. Allow at most two correction rounds. Report any remaining findings.
8. Summarize the changes, validation results, and unresolved issues.

Keep coding and review sequential. Only the coder should edit files
during the delegated workflow. This restriction does not apply to the
direct workflow.
