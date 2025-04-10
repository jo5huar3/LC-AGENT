context = """Purpose: The primary role of this agent is to answere prompts by selecting the correct tool,
            extracting the correct parameters from prompt, and sending its output as input to selected tool/tools."""

code_parser_template = """Parse the response from a previous LLM into a description and a string of valid code, 
                            also come up with a valid filename this could be saved as that doesnt contain special characters. 
                            Here is the response: {response}. You should parse this in the following JSON Format: """
