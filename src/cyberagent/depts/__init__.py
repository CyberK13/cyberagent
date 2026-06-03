"""5 departments: industry / financial / risk / valuation / strategy.

Each department is a separate LLM call with its own system prompt, builds on
prior-department outputs, and emits a structured DeptReport.
Implementations land in 0.1.0.
"""
