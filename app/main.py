# CodeBuddy --> Orchestrator --> ErrorExtractorAgent or StackRedHub

# Orchestor --> Agent which finds out the suitable agents who can complete that specific task with the available tools.
# ErrorExtractor --> Agent which extracts from error messages from the provided image and gives you complete understanding of the occuring error.
# StackRedHub --> Agent which uses sources like github, reddit, stackoverflow to understand the occuring error and find resolutions for the same.
# A dedicated mcp server which has all the tools which the agents and access and complete its tasks
# And Opik is used as a agent observability here to monitor the agent behaviour of what its trying to do.



# poetry install
# poetry run mcp_server
# Export your GOOGLE_API_KEY= before running the agents in each terminal
# poetry run error_extractor_agent --> to run the error_extractor_agent
# poetry run stackredhub_agent --> to run the error stackredhub_agent 
# poetry run orchestrator_agent --> to run the orchestrator_agent
# Each agent should run on seperate terminal
# After running all the agent run the coding buddy --> poetry run coding_buddy
# Njoy Chatting
# Make sure that the free version of gemini has a limit and u cant chat for along time 