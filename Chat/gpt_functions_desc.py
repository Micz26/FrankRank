gpt_functions_descriptions = [
            {
                "name": "get_stock_value",
                "description": "Get the current value about the given stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chosen_stock": {
                            "type": "string",
                            "description": "Stock name e.g. META or MSFT",
                        },
                        "unit": {"type": "string",
                                 "enum": ["USD"]},
                    },
                    "required": ["chosen_stock"],
                },
            },

            {
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
            },

            {
                "name": "show_news",
                "description": "show brief or fast or quick (it have to be clearly stated) news about given stock",
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
            },

            {
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
            },

            {
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
            },

        ]