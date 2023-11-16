gpt_functions_descriptions = [
            {
                "type": "function",
                 "function": {
                    "name": "get_stock_value",
                    "description": "Get the current value about the given stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chosen_stock": {
                                "type": "string",
                                "description": "Stock name e.g. META or MSFT",
                            },
                            "unit": {"type": "string", "enum": ["USD"]},
                        },
                        "required": ["chosen_stock"],
                    },
                 }
            },

            {
                "type": "function",
                "function": {
                    "name": "interpret_a_chart",
                    "description": "Interpret a list of given stock (1y or 1m or 1d)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chosen_stock": {
                                "type": "string",
                                "description": "Stock name e.g. META or ACN",
                            },
                            "time": {
                                "type": "string",
                                "enum": ["1y", "1m", "1d"]},
                        },
                        "required": ["chosen_stock", "time"],
                    },
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "display_major_holders",
                    "description": "display major holders of given stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chosen_stock": {
                                "type": "string",
                                "description": "Stock name e.g. META or ACN",
                            },
                        },
                        "required": ["chosen_stock"],
                    },
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "show_newsPLUSArticles",
                    "description": "show news about given stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chosen_stock": {
                                "type": "string",
                                "description": "Stock name e.g. META or ACN",
                            },
                        },
                        "required": ["chosen_stock"],
                    },
                }
            },

        ]